#!/usr/bin/env python3
"""Stage 05a: first independent sentence-level communicative-function annotation.

The function label describes what the whole sentence is doing communicatively.
It is intentionally independent of the target lemma's lexical-sense annotation.
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

FIELDS = [
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
        FIELDS,
    )


def annotate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    instructions = f"""
You are the FIRST INDEPENDENT annotator for one sentence-level communicative-function tag.

RULES
- Tag what the whole sentence is doing communicatively.
- Do not tag the sentence topic.
- Do not tag the sampled lemma or its lexical sense.
- Use only one function_id from the controlled taxonomy.
- If uncertain, use confidence=low and requires_review=true.
- Keep the rationale to 25 words or fewer.
- If there is no plausible alternative, set alternative_function_id to an empty string.
- Outputs are provisional Tier 4 candidate material for expert review.

CONTROLLED TAXONOMY
{taxonomy_text}

SENTENCE
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
    item = hierarchy[first_id]
    return {
        "row_id": row["row_id"],
        "sentence": row["sentence"],
        "top_level_label": item["top_level_label"],
        "subcategory_id": item["subcategory_id"],
        "subcategory_label": item["subcategory_label"],
        "function_id": first_id,
        "function_label": item["function_label"],
        "confidence": "low",
        "rationale": "Dry run only; not an LLM judgement.",
        "alternative_function_id": "",
        "ambiguity_note": "Dry-run placeholder.",
        "requires_review": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent Function Pass 1.")
    parser.add_argument(
        "--sentences",
        "--input",
        dest="sentences",
        required=True,
        help="Sampled target-occurrence CSV from Stage 03",
    )
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass1"))
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)

    data = pd.read_csv(args.sentences, dtype=str).fillna("")
    require_columns(data, ["sentence"], "Sentence sample")
    if "row_id" not in data.columns:
        data.insert(0, "row_id", [f"row_{i + 1:06d}" for i in range(len(data))])
        print("WARNING: input had no row_id; generated row_000001-style IDs.")
    if args.limit > 0:
        data = data.head(args.limit)

    output_path = Path(args.output)
    done = load_done_ids(output_path)
    for _, series in data.iterrows():
        row = {"row_id": str(series["row_id"]), "sentence": str(series["sentence"])}
        if row["row_id"] in done:
            continue
        result = dry_run_result(row, hierarchy) if args.dry_run else annotate(
            args.model, taxonomy_text, row, hierarchy
        )
        append_csv_row(output_path, FIELDS, result)
        done.add(row["row_id"])
        print(f"Function Pass 1 {row['row_id']}: {result['function_id']} ({result['confidence']})")
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Function Pass 1 complete: {output_path}")


if __name__ == "__main__":
    main()
