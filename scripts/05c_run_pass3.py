#!/usr/bin/env python3
"""Stage 05c: LLM Pass 3 adjudication / final moderated sentence tag."""

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
    normalise_bool,
    read_taxonomy,
    require_columns,
)

PASS3_FIELDS = [
    "row_id",
    "sentence",
    "pass1_function_id",
    "pass2_function_id",
    "final_function_id",
    "final_function_label",
    "final_confidence",
    "adjudication_rationale",
    "human_review_recommended",
]


def schema() -> dict:
    return make_schema(
        "cefr_function_pass3",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "pass1_function_id": {"type": "string"},
            "pass2_function_id": {"type": "string"},
            "final_function_id": {"type": "string"},
            "final_function_label": {"type": "string"},
            "final_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "adjudication_rationale": {"type": "string"},
            "human_review_recommended": {"type": "boolean"},
        },
        PASS3_FIELDS,
    )


def adjudicate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    instructions = f"""
You are making the final moderated decision for one sentence-level CEFR-derived function tag.

Rules:
- Use the controlled taxonomy only.
- Decide independently using the sentence, Pass 1 and Pass 2 evidence.
- If Pass 1 and Pass 2 agree, still check that the agreed function is genuinely best.
- If they disagree, choose the function that best captures what the whole sentence is doing communicatively.
- Do not tag the sampled lemma or sentence topic.
- Keep adjudication_rationale to a maximum of 35 words.
- Mark human_review_recommended true if the case remains genuinely ambiguous.
- Outputs are provisional Tier 4 candidate material for expert review.

CONTROLLED TAXONOMY:
{taxonomy_text}

CASE:
row_id: {row['row_id']}
sentence: {row['sentence']}

PASS 1:
function_id: {row['pass1_function_id']}
rationale: {row.get('pass1_rationale', '')}
confidence: {row.get('pass1_confidence', '')}

PASS 2:
function_id: {row['pass2_function_id']}
decision: {row.get('validator_decision', '')}
rationale: {row.get('pass2_rationale', '')}
confidence: {row.get('pass2_confidence', '')}
"""
    result = call_model_json(model, instructions, schema())
    result = apply_taxonomy_fields(result, "final_function_id", hierarchy)
    return result


def dry_run_result(row: dict[str, str], hierarchy: dict[str, dict[str, str]]) -> dict:
    fid = str(row.get("pass2_function_id") or row.get("pass1_function_id"))
    if fid not in hierarchy:
        fid = next(iter(hierarchy))
    h = hierarchy[fid]
    return {
        "row_id": row["row_id"],
        "sentence": row["sentence"],
        "pass1_function_id": row["pass1_function_id"],
        "pass2_function_id": row["pass2_function_id"],
        "final_function_id": fid,
        "final_function_label": h["function_label"],
        "final_confidence": "low",
        "adjudication_rationale": "Dry run only; not an LLM adjudication.",
        "human_review_recommended": True,
    }


def build_cases(pass1_path: Path, pass2_path: Path, only_problem_cases: bool) -> pd.DataFrame:
    p1 = pd.read_csv(pass1_path, dtype=str).fillna("")
    p2 = pd.read_csv(pass2_path, dtype=str).fillna("")
    require_columns(p1, ["row_id", "sentence", "function_id", "confidence", "rationale"], "Pass 1")
    require_columns(p2, ["row_id", "function_id", "confidence", "validator_decision", "validation_rationale", "requires_review"], "Pass 2")

    p1_small = p1.rename(
        columns={
            "function_id": "pass1_function_id",
            "confidence": "pass1_confidence",
            "rationale": "pass1_rationale",
        }
    )[["row_id", "sentence", "pass1_function_id", "pass1_confidence", "pass1_rationale"]]

    p2_small = p2.rename(
        columns={
            "function_id": "pass2_function_id",
            "confidence": "pass2_confidence",
            "validation_rationale": "pass2_rationale",
        }
    )[["row_id", "pass2_function_id", "pass2_confidence", "pass2_rationale", "validator_decision", "requires_review"]]

    merged = p1_small.merge(p2_small, on="row_id", how="inner")

    if only_problem_cases:
        mask = (
            (merged["pass1_function_id"] != merged["pass2_function_id"])
            | (merged["validator_decision"].str.lower() != "accept")
            | (merged["requires_review"].apply(normalise_bool))
        )
        merged = merged[mask].copy()

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pass 3 final adjudication.")
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--pass2", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass3"))
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only_problem_cases", action="store_true")
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)
    cases = build_cases(Path(args.pass1), Path(args.pass2), args.only_problem_cases)
    if args.limit and args.limit > 0:
        cases = cases.head(args.limit)

    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in cases.iterrows():
        row_dict = row.to_dict()
        row_dict["row_id"] = str(row_dict["row_id"])
        if row_dict["row_id"] in done:
            continue
        result = dry_run_result(row_dict, hierarchy) if args.dry_run else adjudicate(args.model, taxonomy_text, row_dict, hierarchy)
        append_csv_row(output_path, PASS3_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f"Pass 3 row {row_dict['row_id']}: {result['final_function_id']}")
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Pass 3 complete: {output_path}")


if __name__ == "__main__":
    main()
