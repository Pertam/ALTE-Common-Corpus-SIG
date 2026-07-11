#!/usr/bin/env python3
"""Stage 04c: informed critical review of the Pass 1 lexical-sense annotation.

Production mode sees both the Pass 1 sense and the Pass 1 sentence function.
Use --blind only for a sampled reliability study.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, call_model_json, default_model, load_done_ids, make_schema, require_columns
from llm_sense_tagging_utils import compact_inventory, ensure_target_columns, inventory_for_row, read_inventory

FIELDS = [
    "row_id", "sentence", "language", "target_token", "target_lemma", "target_pos",
    "inventory_id", "pass1_sense_id", "pass1_function_id", "pass1_function_label",
    "validator_decision", "sense_id", "sense_gloss", "confidence", "rationale",
    "alternative_sense_id", "interaction_note", "requires_review", "review_mode",
]


def classify(model: str, row: dict[str, str], inventory: list[dict[str, str]], blind: bool) -> dict:
    valid_ids = [x["sense_id"] for x in inventory]
    schema = make_schema(
        "lexical_sense_pass2_review",
        {
            "row_id": {"type": "string"},
            "validator_decision": {"type": "string", "enum": ["accept", "change", "uncertain"]},
            "sense_id": {"type": "string", "enum": valid_ids},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "rationale": {"type": "string"},
            "alternative_sense_id": {"type": "string"},
            "interaction_note": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        ["row_id", "validator_decision", "sense_id", "confidence", "rationale", "alternative_sense_id", "interaction_note", "requires_review"],
    )
    prior = "" if blind else f"""
PASS 1 SENSE PROPOSAL
sense_id: {row['pass1_sense_id']}
confidence: {row['pass1_sense_confidence']}
rationale: {row['pass1_sense_rationale']}

PASS 1 SENTENCE-FUNCTION PROPOSAL
function_id: {row['pass1_function_id']}
function_label: {row['pass1_function_label']}
confidence: {row['pass1_function_confidence']}
rationale: {row['pass1_function_rationale']}
"""
    role = "BLIND lexical-sense annotator for a reliability sample" if blind else "INFORMED CRITICAL REVIEWER of the Pass 1 lexical-sense annotation"
    prompt = f"""
You are the {role}.

Decide what the target lemma means in this sentence. In informed mode, critically inspect the Pass 1 sense, rationale and proposed sentence function. The function may provide useful context, but it must not determine the lexical sense. Accept Pass 1 only when it is defensible; otherwise change it or mark it uncertain.

Use only the approved inventory. Use OTHER for a clear missing sense and UNCLEAR for insufficient context. Keep the rationale under 35 words. In interaction_note, state briefly whether the proposed function helped, conflicted with, or was irrelevant to the sense decision. Recommend human review for unresolved ambiguity, OTHER, UNCLEAR or a likely inventory problem.

TARGET
language: {row['language']}
token: {row['target_token']}
lemma: {row['target_lemma']}
POS: {row['target_pos']}

APPROVED INVENTORY
{compact_inventory(inventory)}

SENTENCE
row_id: {row['row_id']}
{row['sentence']}
{prior}
"""
    result = call_model_json(model, prompt, schema)
    selected = next(x for x in inventory if x["sense_id"] == result["sense_id"])
    if result.get("alternative_sense_id") not in valid_ids:
        result["alternative_sense_id"] = ""
    result.update({key: row[key] for key in ["sentence", "language", "target_token", "target_lemma", "target_pos"]})
    result["inventory_id"] = selected["inventory_id"]
    result["sense_gloss"] = selected["sense_gloss"]
    result["pass1_sense_id"] = "" if blind else row["pass1_sense_id"]
    result["pass1_function_id"] = "" if blind else row["pass1_function_id"]
    result["pass1_function_label"] = "" if blind else row["pass1_function_label"]
    result["review_mode"] = "blind_validation" if blind else "informed_review"
    return result


def build_cases(samples: pd.DataFrame, sense_pass1: str | None, function_pass1: str | None, blind: bool) -> pd.DataFrame:
    if blind:
        result = samples.copy()
        for column in ["pass1_sense_id", "pass1_sense_confidence", "pass1_sense_rationale", "pass1_function_id", "pass1_function_label", "pass1_function_confidence", "pass1_function_rationale"]:
            result[column] = ""
        return result
    if not sense_pass1 or not function_pass1:
        raise ValueError("Informed review requires --pass1 and --function_pass1. Use --blind only for a sampled blind-validation run.")
    sense = pd.read_csv(sense_pass1, dtype=str).fillna("")
    function = pd.read_csv(function_pass1, dtype=str).fillna("")
    require_columns(sense, ["row_id", "sense_id", "confidence", "rationale"], "Sense Pass 1")
    require_columns(function, ["row_id", "function_id", "function_label", "confidence", "rationale"], "Function Pass 1")
    sense = sense[["row_id", "sense_id", "confidence", "rationale"]].rename(columns={"sense_id":"pass1_sense_id", "confidence":"pass1_sense_confidence", "rationale":"pass1_sense_rationale"})
    function = function[["row_id", "function_id", "function_label", "confidence", "rationale"]].rename(columns={"function_id":"pass1_function_id", "function_label":"pass1_function_label", "confidence":"pass1_function_confidence", "rationale":"pass1_function_rationale"})
    return samples.merge(sense, on="row_id", how="inner").merge(function, on="row_id", how="inner")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run informed lexical-sense Pass 2 review.")
    parser.add_argument("--samples", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--pass1", help="Sense Pass 1 CSV; required unless --blind")
    parser.add_argument("--function_pass1", help="Function Pass 1 CSV; required unless --blind")
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("sense_pass2"))
    parser.add_argument("--allow_provisional", action="store_true")
    parser.add_argument("--blind", action="store_true", help="Do not show Pass 1 outputs; use only for a sampled reliability study")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    samples = ensure_target_columns(pd.read_csv(args.samples, dtype=str).fillna(""), "Samples")
    data = build_cases(samples, args.pass1, args.function_pass1, args.blind)
    inventories = read_inventory(Path(args.inventory), args.allow_provisional)
    if args.limit > 0:
        data = data.head(args.limit)
    output = Path(args.output)
    done = load_done_ids(output)
    for _, series in data.iterrows():
        row = {key: str(value) for key, value in series.to_dict().items()}
        if row["row_id"] in done:
            continue
        inventory = inventory_for_row(row, inventories)
        if args.dry_run:
            selected = inventory[0]
            result = {
                **{k: row[k] for k in ["row_id", "sentence", "language", "target_token", "target_lemma", "target_pos"]},
                "inventory_id": selected["inventory_id"],
                "pass1_sense_id": "" if args.blind else row["pass1_sense_id"],
                "pass1_function_id": "" if args.blind else row["pass1_function_id"],
                "pass1_function_label": "" if args.blind else row["pass1_function_label"],
                "validator_decision": "uncertain",
                "sense_id": selected["sense_id"],
                "sense_gloss": selected["sense_gloss"],
                "confidence": "low",
                "rationale": "Dry run only",
                "alternative_sense_id": "",
                "interaction_note": "Dry run only",
                "requires_review": True,
                "review_mode": "blind_validation" if args.blind else "informed_review",
            }
        else:
            result = classify(args.model, row, inventory, args.blind)
        append_csv_row(output, FIELDS, result)
        done.add(row["row_id"])
        print(f"Sense Pass 2 {row['row_id']}: {result['validator_decision']} -> {result['sense_id']} ({result['review_mode']})")
        if args.sleep:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
