#!/usr/bin/env python3
"""Stage 05b: LLM Pass 2 blind validation of Pass 1 function tags."""

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

PASS2_FIELDS = [
    "row_id",
    "sentence",
    "pass1_function_id",
    "validator_decision",
    "function_id",
    "function_label",
    "confidence",
    "validation_rationale",
    "requires_review",
]


def schema() -> dict:
    return make_schema(
        "cefr_function_pass2",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "pass1_function_id": {"type": "string"},
            "validator_decision": {"type": "string", "enum": ["accept", "change", "uncertain"]},
            "function_id": {"type": "string"},
            "function_label": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "validation_rationale": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        PASS2_FIELDS,
    )


def validate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    instructions = f"""
You are doing blind validation of a provisional sentence-level function tag.

Task: challenge the Pass 1 label and decide whether it is the best available taxonomy label.

Rules:
- Tag what the whole sentence is doing communicatively.
- Do not tag the sentence topic.
- Do not tag the sampled lemma itself.
- Accept the Pass 1 tag if it is reasonable and defensible.
- Change it only if another function is clearly better.
- If genuinely ambiguous, use validator_decision = uncertain and requires_review = true.
- Use only one function_id from the controlled taxonomy.
- Keep validation_rationale to a maximum of 30 words.
- Outputs are provisional Tier 4 candidate material for expert review.

CONTROLLED TAXONOMY:
{taxonomy_text}

CASE:
row_id: {row['row_id']}
sentence: {row['sentence']}
pass1_function_id: {row['function_id']}
pass1_function_label: {row.get('function_label', '')}
pass1_rationale: {row.get('rationale', '')}
"""
    result = call_model_json(model, instructions, schema())
    result = apply_taxonomy_fields(result, "function_id", hierarchy)
    return result


def dry_run_result(row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    fid = str(row["function_id"])
    if fid not in hierarchy:
        fid = next(iter(hierarchy))
    h = hierarchy[fid]
    return {
        "row_id": row["row_id"],
        "sentence": row["sentence"],
        "pass1_function_id": row["function_id"],
        "validator_decision": "uncertain",
        "function_id": fid,
        "function_label": h["function_label"],
        "confidence": "low",
        "validation_rationale": "Dry run only; not an LLM validation.",
        "requires_review": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pass 2 blind validation.")
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass2"))
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)

    p1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    require_columns(p1, ["row_id", "sentence", "function_id", "function_label"], "Pass 1")
    if args.limit and args.limit > 0:
        p1 = p1.head(args.limit)

    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in p1.iterrows():
        row_dict = row.to_dict()
        row_dict["row_id"] = str(row_dict["row_id"])
        if row_dict["row_id"] in done:
            continue
        result = dry_run_result(row_dict, hierarchy) if args.dry_run else validate(args.model, taxonomy_text, row_dict, hierarchy)
        append_csv_row(output_path, PASS2_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f"Pass 2 row {row_dict['row_id']}: {result['validator_decision']} -> {result['function_id']}")
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Pass 2 complete: {output_path}")


if __name__ == "__main__":
    main()
