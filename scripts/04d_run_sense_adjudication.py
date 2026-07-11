#!/usr/bin/env python3
"""Stage 04d: adjudicate disagreements between independent sense passes."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, call_model_json, default_model, load_done_ids, make_schema, require_columns
from llm_sense_tagging_utils import compact_inventory, inventory_for_row, read_inventory

FIELDS = ["row_id", "sentence", "language", "target_lemma", "target_pos", "pass1_sense_id", "pass2_sense_id", "final_sense_id", "final_sense_gloss", "final_confidence", "adjudication_rationale", "human_review_recommended"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate independent sense passes.")
    parser.add_argument("--pass1", required=True); parser.add_argument("--pass2", required=True)
    parser.add_argument("--inventory", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("sense_pass3")); parser.add_argument("--allow_provisional", action="store_true")
    parser.add_argument("--only_problem_cases", action="store_true"); parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    p1 = pd.read_csv(args.pass1, dtype=str).fillna(""); p2 = pd.read_csv(args.pass2, dtype=str).fillna("")
    required = ["row_id", "sentence", "language", "target_lemma", "target_pos", "sense_id", "confidence", "rationale"]
    require_columns(p1, required, "Sense Pass 1"); require_columns(p2, required, "Sense Pass 2")
    left = p1.rename(columns={"sense_id":"pass1_sense_id", "confidence":"pass1_confidence", "rationale":"pass1_rationale"})
    right = p2[["row_id", "sense_id", "confidence", "rationale"]].rename(columns={"sense_id":"pass2_sense_id", "confidence":"pass2_confidence", "rationale":"pass2_rationale"})
    cases = left.merge(right, on="row_id")
    if args.only_problem_cases:
        cases = cases[(cases.pass1_sense_id != cases.pass2_sense_id) | (cases.pass1_confidence == "low") | (cases.pass2_confidence == "low")]
    if args.limit > 0: cases = cases.head(args.limit)

    inventories = read_inventory(Path(args.inventory), args.allow_provisional)
    output = Path(args.output); done = load_done_ids(output)
    for _, series in cases.iterrows():
        row = {key: str(value) for key, value in series.to_dict().items()}
        if row["row_id"] in done: continue
        inventory = inventory_for_row(row, inventories); valid_ids = [x["sense_id"] for x in inventory]
        schema = make_schema("sense_adjudication", {
            "row_id":{"type":"string"}, "pass1_sense_id":{"type":"string"}, "pass2_sense_id":{"type":"string"},
            "final_sense_id":{"type":"string", "enum":valid_ids}, "final_confidence":{"type":"string", "enum":["high","medium","low"]},
            "adjudication_rationale":{"type":"string"}, "human_review_recommended":{"type":"boolean"}}, FIELDS[0:1]+FIELDS[5:])
        prompt = f"""Adjudicate two independent lexical-sense annotations. Judge the target lemma meaning, not sentence function. Use only the approved inventory. Recommend human review for unresolved ambiguity, OTHER, UNCLEAR or likely inventory problems.
INVENTORY
{compact_inventory(inventory)}
SENTENCE
{row['sentence']}
PASS 1: {row['pass1_sense_id']} | {row['pass1_confidence']} | {row['pass1_rationale']}
PASS 2: {row['pass2_sense_id']} | {row['pass2_confidence']} | {row['pass2_rationale']}"""
        result = call_model_json(args.model, prompt, schema)
        selected = next(x for x in inventory if x["sense_id"] == result["final_sense_id"])
        result.update({"sentence":row["sentence"], "language":row["language"], "target_lemma":row["target_lemma"], "target_pos":row["target_pos"], "final_sense_gloss":selected["sense_gloss"]})
        append_csv_row(output, FIELDS, result); done.add(row["row_id"])
        print(f"Sense adjudication {row['row_id']}: {result['final_sense_id']}")

if __name__ == "__main__": main()
