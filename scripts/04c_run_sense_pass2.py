#!/usr/bin/env python3
"""Stage 04c: second independent lexical-sense assignment; Pass 1 is unseen."""
from __future__ import annotations

import argparse
import time
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, call_model_json, default_model, load_done_ids, make_schema
from llm_sense_tagging_utils import compact_inventory, ensure_target_columns, inventory_for_row, read_inventory

FIELDS = ["row_id", "sentence", "language", "target_token", "target_lemma", "target_pos", "inventory_id", "sense_id", "sense_gloss", "confidence", "rationale", "alternative_sense_id", "requires_review"]


def classify(model: str, row: dict[str, str], inventory: list[dict[str, str]]) -> dict:
    valid_ids = [x["sense_id"] for x in inventory]
    schema = make_schema("lexical_sense_pass2_independent", {
        "row_id": {"type": "string"}, "sense_id": {"type": "string", "enum": valid_ids},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "rationale": {"type": "string"}, "alternative_sense_id": {"type": "string"},
        "requires_review": {"type": "boolean"}},
        ["row_id", "sense_id", "confidence", "rationale", "alternative_sense_id", "requires_review"])
    prompt = f"""
You are the SECOND INDEPENDENT lexical-sense annotator. Make a fresh decision; you have not seen Pass 1.
Select the meaning of the target lemma, not the communicative function of the sentence.
Use only the approved inventory. Use OTHER for a clear missing sense and UNCLEAR for insufficient context.
Use low confidence and requires_review=true when uncertain. Keep the rationale under 25 words.

TARGET: {row['language']} | {row['target_token']} | {row['target_lemma']} | {row['target_pos']}
APPROVED INVENTORY
{compact_inventory(inventory)}
SENTENCE
row_id: {row['row_id']}
{row['sentence']}
"""
    result = call_model_json(model, prompt, schema)
    selected = next(x for x in inventory if x["sense_id"] == result["sense_id"])
    if result.get("alternative_sense_id") not in valid_ids: result["alternative_sense_id"] = ""
    result.update({key: row[key] for key in ["sentence", "language", "target_token", "target_lemma", "target_pos"]})
    result["inventory_id"] = selected["inventory_id"]; result["sense_gloss"] = selected["sense_gloss"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent lexical-sense Pass 2.")
    parser.add_argument("--samples", required=True); parser.add_argument("--inventory", required=True)
    parser.add_argument("--output", required=True); parser.add_argument("--model", default=default_model("sense_pass2"))
    parser.add_argument("--allow_provisional", action="store_true"); parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.0); parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()
    data = ensure_target_columns(pd.read_csv(args.samples, dtype=str).fillna(""), "Samples")
    inventories = read_inventory(Path(args.inventory), args.allow_provisional)
    if args.limit > 0: data = data.head(args.limit)
    output = Path(args.output); done = load_done_ids(output)
    for _, series in data.iterrows():
        row = {key: str(value) for key, value in series.to_dict().items()}
        if row["row_id"] in done: continue
        inventory = inventory_for_row(row, inventories)
        if args.dry_run:
            selected = inventory[-1]
            result = {**{k: row[k] for k in ["row_id", "sentence", "language", "target_token", "target_lemma", "target_pos"]}, "inventory_id": selected["inventory_id"], "sense_id": selected["sense_id"], "sense_gloss": selected["sense_gloss"], "confidence": "low", "rationale": "Dry run only", "alternative_sense_id": "", "requires_review": True}
        else: result = classify(args.model, row, inventory)
        append_csv_row(output, FIELDS, result); done.add(row["row_id"])
        print(f"Sense Pass 2 {row['row_id']}: {result['sense_id']}")
        if args.sleep: time.sleep(args.sleep)

if __name__ == "__main__": main()
