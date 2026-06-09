#!/usr/bin/env python3
"""Stage 05a: LLM Pass 1 sentence-level function tagging.

Tags the communicative function of the whole sentence using the controlled
CEFR-derived taxonomy. Outputs are provisional Tier 4 candidate material only.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from llm_function_tagging_utils import (
    append_csv_row,
    apply_taxonomy_fields,
    call_model_json,
    compact_taxonomy_text,
    default_model,
    load_done_ids,
    make_schema,
    read_taxonomy,
    require_columns,
)

PASS1_FIELDS = [
    "row_id",
    "sentence",
    "top_level_label",
    "subcategory_id",
    "subcategory_label",
    "function_id",
    "function_label",
    "confidence",
    "rationale",
    "alternative_function_id",
    "ambiguity_note",
    "requires_review",
]


def schema() -> dict:
    return make_schema(
        "cefr_function_pass1",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "top_level_label": {"type": "string"},
            "subcategory_id": {"type": "string"},
            "subcategory_label": {"type": "string"},
            "function_id": {"type": "string"},
            "function_label": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "rationale": {"type": "string"},
            "alternative_function_id": {"type": "string"},
            "ambiguity_note": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        PASS1_FIELDS,
    )


def annotate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    instructions = f"""
You are annotating ONE sentence for the European CEFR Vocabulary Atlas pilot.

Task: assign the best sentence-level communicative function from the controlled taxonomy.

Rules:
- Tag what the whole sentence is doing communicatively.
- Do not tag the topic of the sentence.
- Do not tag the sampled lemma itself.
- Use only one function_id from the taxonomy.
- If uncertain, use confidence = low and requires_review = true.
- Keep rationale to a maximum of 25 words.
- If there is no plausible alternative, set alternative_function_id to an empty string.
- Outputs are provisional Tier 4 candidate material for expert review.

CONTROLLED TAXONOMY:
{taxonomy_text}

SENTENCE:
row_id: {row['row_id']}
sentence: {row['sentence']}
"""
    result = call_model_json(model, instructions, schema())
    result = apply_taxonomy_fields(result, "function_id", hierarchy)
    alt = str(result.get("alternative_function_id", "")).strip()
    if alt and alt not in hierarchy:
        result["alternative_function_id"] = ""
    return result


def dry_run_result(row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    first_id = next(iter(hierarchy))
    h = hierarchy[first_id]
    return {
        "row_id": row["row_id"],
        "sentence": row["sentence"],
        "top_level_label": h["top_level_label"],
        "subcategory_id": h["subcategory_id"],
        "subcategory_label": h["subcategory_label"],
        "function_id": first_id,
        "function_label": h["function_label"],
        "confidence": "low",
        "rationale": "Dry run only; not an LLM judgment.",
        "alternative_function_id": "",
        "ambiguity_note": "Dry run placeholder for pipeline testing.",
        "requires_review": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pass 1 sentence-level function tagging.")
    parser.add_argument("--sentences", "--input", dest="sentences", required=True, help="Sampled sentence CSV from Stage 04")
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass1"))
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between API calls")
    parser.add_argument("--limit", type=int, default=0, help="Optional row limit for testing")
    parser.add_argument("--dry_run", action="store_true", help="Write structurally valid non-LLM rows for pipeline testing")
    args = parser.parse_args()

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)

    data = pd.read_csv(args.sentences, dtype=str).fillna("")
    require_columns(data, ["sentence"], "Sentence sample")
    if "row_id" not in data.columns:
        data.insert(0, "row_id", [f"row_{i + 1:06d}" for i in range(len(data))])
        print("WARNING: input had no row_id column; generated row_000001-style IDs for this run.")
    if args.limit and args.limit > 0:
        data = data.head(args.limit)

    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in data.iterrows():
        row_dict = {"row_id": str(row["row_id"]), "sentence": str(row["sentence"])}
        if row_dict["row_id"] in done:
            continue
        result = dry_run_result(row_dict, hierarchy) if args.dry_run else annotate(args.model, taxonomy_text, row_dict, hierarchy)
        append_csv_row(output_path, PASS1_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f"Pass 1 row {row_dict['row_id']}: {result['function_id']} ({result['confidence']})")
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Pass 1 complete: {output_path}")


if __name__ == "__main__":
    main()
