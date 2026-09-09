#!/usr/bin/env python3
"""Stage 05c: adjudicate Pass 1 and informed Pass 2 function decisions."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, apply_taxonomy_fields, call_model_json, compact_taxonomy_text, default_model, load_done_ids, make_schema, normalise_bool, read_taxonomy, require_columns

FIELDS = [
    "row_id", "sentence", "pass1_function_id", "pass2_function_id",
    "pass1_requires_review", "pass2_validator_decision", "pass2_requires_review",
    "interaction_note", "review_mode", "final_function_id", "final_function_label",
    "final_function_confidence", "adjudication_rationale", "human_review_recommended",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate Pass 1 and informed Function Pass 2.")
    parser.add_argument("--pass1", required=True); parser.add_argument("--pass2", required=True)
    parser.add_argument("--taxonomy", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass3")); parser.add_argument("--only_problem_cases", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    p1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    p2 = pd.read_csv(args.pass2, dtype=str).fillna("")
    required = ["row_id", "sentence", "function_id", "confidence", "rationale", "requires_review"]
    require_columns(p1, required, "Function Pass 1")
    require_columns(p2, required, "Function Pass 2")

    left = p1.rename(columns={
        "function_id":"pass1_function_id",
        "confidence":"pass1_confidence",
        "rationale":"pass1_rationale",
        "requires_review":"pass1_requires_review",
    })
    p2_columns = ["row_id", "function_id", "confidence", "rationale", "requires_review"]
    for optional in ["validator_decision", "interaction_note", "review_mode"]:
        if optional in p2.columns:
            p2_columns.append(optional)
    right = p2[p2_columns].rename(columns={
        "function_id":"pass2_function_id",
        "confidence":"pass2_confidence",
        "rationale":"pass2_rationale",
        "requires_review":"pass2_requires_review",
        "validator_decision":"pass2_validator_decision",
    })
    cases = left.merge(right, on="row_id", validate="one_to_one")

    if args.only_problem_cases:
        mask = (
            (cases.pass1_function_id != cases.pass2_function_id)
            | (cases.pass1_confidence == "low")
            | (cases.pass2_confidence == "low")
            | cases.pass1_requires_review.str.lower().isin(["true", "1", "yes"])
            | cases.pass2_requires_review.str.lower().isin(["true", "1", "yes"])
        )
        if "pass2_validator_decision" in cases.columns:
            mask = mask | (cases.pass2_validator_decision != "accept")
        cases = cases[mask]
    if args.limit > 0:
        cases = cases.head(args.limit)

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)
    output = Path(args.output)
    done = load_done_ids(output)
    properties = {
        "final_function_id":{"type":"string", "enum": sorted(hierarchy)},
        "final_function_confidence":{"type":"string", "enum":["high","medium","low"]},
        "adjudication_rationale":{"type":"string"},
        "human_review_recommended":{"type":"boolean"},
    }
    required_output = ["final_function_id", "final_function_confidence", "adjudication_rationale", "human_review_recommended"]
    schema = make_schema("function_adjudication", properties, required_output)

    for _, series in cases.iterrows():
        row = {key:str(value) for key,value in series.to_dict().items()}
        if row["row_id"] in done:
            continue
        prompt = f"""
Adjudicate an initial sentence-function annotation and its informed critical review.
Judge what the whole sentence is doing, not its topic, sampled lemma or lexical sense. Pass 2 may have used the proposed sense as contextual evidence, so check independently that it did not allow sense to determine function. Use the controlled taxonomy. Recommend human review if ambiguity remains.

TAXONOMY
{taxonomy_text}

SENTENCE
{row['sentence']}

PASS 1 INITIAL ANNOTATION
{row['pass1_function_id']} | {row['pass1_confidence']} | {row['pass1_rationale']}
requires_review: {row['pass1_requires_review']}

PASS 2 INFORMED REVIEW
review decision: {row.get('pass2_validator_decision', '')}
function: {row['pass2_function_id']} | {row['pass2_confidence']} | {row['pass2_rationale']}
requires_review: {row['pass2_requires_review']}
interaction note: {row.get('interaction_note', '')}
review mode: {row.get('review_mode', 'informed_review')}
"""
        result = call_model_json(args.model, prompt, schema)
        result = apply_taxonomy_fields(result, "final_function_id", hierarchy)

        # Preserve explicit upstream review flags; adjudication cannot erase them.
        if (
            normalise_bool(row["pass1_requires_review"])
            or normalise_bool(row["pass2_requires_review"])
            or str(row.get("pass2_validator_decision", "")).lower() in {"change", "uncertain"}
        ):
            result["human_review_recommended"] = True

        result.update({
            "row_id": row["row_id"],
            "sentence": row["sentence"],
            "pass1_function_id": row["pass1_function_id"],
            "pass2_function_id": row["pass2_function_id"],
            "pass1_requires_review": row["pass1_requires_review"],
            "pass2_validator_decision": row.get("pass2_validator_decision", ""),
            "pass2_requires_review": row["pass2_requires_review"],
            "interaction_note": row.get("interaction_note", ""),
            "review_mode": row.get("review_mode", "informed_review"),
        })
        append_csv_row(output, FIELDS, result)
        done.add(row["row_id"])
        print(f"Function adjudication {row['row_id']}: {result['final_function_id']}")


if __name__ == "__main__":
    main()
