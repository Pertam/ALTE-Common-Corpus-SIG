#!/usr/bin/env python3
"""Stage 04d: adjudicate Pass 1 and informed Pass 2 lexical-sense decisions."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, call_model_json, default_model, load_done_ids, make_schema, normalise_bool, require_columns
from llm_sense_tagging_utils import compact_inventory, inventory_for_row, read_inventory

FIELDS = [
    "row_id", "sentence", "language", "target_lemma", "target_pos", "inventory_id",
    "pass1_sense_id", "pass2_sense_id", "pass1_requires_review",
    "pass2_validator_decision", "pass2_requires_review", "interaction_note", "review_mode",
    "final_sense_id", "final_sense_gloss", "final_sense_confidence",
    "adjudication_rationale", "human_review_recommended",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate Pass 1 and informed Sense Pass 2.")
    parser.add_argument("--pass1", required=True); parser.add_argument("--pass2", required=True)
    parser.add_argument("--inventory", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("sense_pass3")); parser.add_argument("--allow_provisional", action="store_true")
    parser.add_argument("--only_problem_cases", action="store_true"); parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    p1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    p2 = pd.read_csv(args.pass2, dtype=str).fillna("")
    required = ["row_id", "sentence", "language", "target_lemma", "target_pos", "inventory_id", "sense_id", "confidence", "rationale", "requires_review"]
    require_columns(p1, required, "Sense Pass 1")
    require_columns(p2, required, "Sense Pass 2")

    left = p1.rename(columns={
        "inventory_id": "pass1_inventory_id",
        "sense_id": "pass1_sense_id",
        "confidence": "pass1_confidence",
        "rationale": "pass1_rationale",
        "requires_review": "pass1_requires_review",
    })
    p2_columns = ["row_id", "inventory_id", "sense_id", "confidence", "rationale", "requires_review"]
    for optional in ["validator_decision", "interaction_note", "review_mode"]:
        if optional in p2.columns:
            p2_columns.append(optional)
    right = p2[p2_columns].rename(columns={
        "inventory_id": "pass2_inventory_id",
        "sense_id": "pass2_sense_id",
        "confidence": "pass2_confidence",
        "rationale": "pass2_rationale",
        "requires_review": "pass2_requires_review",
        "validator_decision": "pass2_validator_decision",
    })
    cases = left.merge(right, on="row_id", validate="one_to_one")

    mismatch = cases["pass1_inventory_id"] != cases["pass2_inventory_id"]
    if mismatch.any():
        bad = cases.loc[mismatch, ["row_id", "pass1_inventory_id", "pass2_inventory_id"]].head(20).to_dict("records")
        raise ValueError(f"Sense Pass 1 and Pass 2 use different inventory IDs: {bad}")

    if args.only_problem_cases:
        mask = (
            (cases.pass1_sense_id != cases.pass2_sense_id)
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

    inventories = read_inventory(Path(args.inventory), args.allow_provisional)
    output = Path(args.output)
    done = load_done_ids(output)

    for _, series in cases.iterrows():
        row = {key: str(value) for key, value in series.to_dict().items()}
        if row["row_id"] in done:
            continue
        inventory = inventory_for_row(row, inventories)
        inventory_ids = {x["inventory_id"] for x in inventory}
        if inventory_ids != {row["pass2_inventory_id"]}:
            raise ValueError(
                f"Adjudication inventory for {row['row_id']} does not match Pass 1/2 inventory_id "
                f"{row['pass2_inventory_id']}."
            )
        valid_ids = [x["sense_id"] for x in inventory]
        properties = {
            "final_sense_id": {"type": "string", "enum": valid_ids},
            "final_sense_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "adjudication_rationale": {"type": "string"},
            "human_review_recommended": {"type": "boolean"},
        }
        schema = make_schema(
            "sense_adjudication",
            properties,
            ["final_sense_id", "final_sense_confidence", "adjudication_rationale", "human_review_recommended"],
        )
        prompt = f"""
Adjudicate an initial lexical-sense annotation and its informed critical review.
Judge the target lemma meaning, not the sentence function. Pass 2 may have used the proposed function as contextual evidence, so check independently that it did not allow function to determine sense. Use only the approved inventory. Recommend human review for unresolved ambiguity, OTHER, UNCLEAR or a likely inventory problem.

INVENTORY
{compact_inventory(inventory)}

SENTENCE
{row['sentence']}

PASS 1 INITIAL ANNOTATION
{row['pass1_sense_id']} | {row['pass1_confidence']} | {row['pass1_rationale']}
requires_review: {row['pass1_requires_review']}

PASS 2 INFORMED REVIEW
review decision: {row.get('pass2_validator_decision', '')}
sense: {row['pass2_sense_id']} | {row['pass2_confidence']} | {row['pass2_rationale']}
requires_review: {row['pass2_requires_review']}
interaction note: {row.get('interaction_note', '')}
review mode: {row.get('review_mode', 'informed_review')}
"""
        result = call_model_json(args.model, prompt, schema)
        selected = next(x for x in inventory if x["sense_id"] == result["final_sense_id"])

        # Preserve upstream review flags deterministically; adjudication cannot erase them.
        if (
            normalise_bool(row["pass1_requires_review"])
            or normalise_bool(row["pass2_requires_review"])
            or str(row.get("pass2_validator_decision", "")).lower() in {"change", "uncertain"}
            or str(selected.get("sense_role", "")).upper() in {"OTHER", "UNCLEAR"}
        ):
            result["human_review_recommended"] = True

        result.update({
            "row_id": row["row_id"],
            "sentence": row["sentence"],
            "language": row["language"],
            "target_lemma": row["target_lemma"],
            "target_pos": row["target_pos"],
            "inventory_id": row["pass2_inventory_id"],
            "pass1_sense_id": row["pass1_sense_id"],
            "pass2_sense_id": row["pass2_sense_id"],
            "pass1_requires_review": row["pass1_requires_review"],
            "pass2_validator_decision": row.get("pass2_validator_decision", ""),
            "pass2_requires_review": row["pass2_requires_review"],
            "interaction_note": row.get("interaction_note", ""),
            "review_mode": row.get("review_mode", "informed_review"),
            "final_sense_gloss": selected["sense_gloss"],
        })
        append_csv_row(output, FIELDS, result)
        done.add(row["row_id"])
        print(f"Sense adjudication {row['row_id']}: {result['final_sense_id']}")


if __name__ == "__main__":
    main()
