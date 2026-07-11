#!/usr/bin/env python3
"""Stage 05b: second independent sentence-level function annotation."""
from __future__ import annotations

import argparse
import time
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, apply_taxonomy_fields, call_model_json, compact_taxonomy_text, default_model, load_done_ids, make_schema, read_taxonomy, require_columns

FIELDS = ["row_id", "sentence", "top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "confidence", "rationale", "alternative_function_id", "ambiguity_note", "requires_review"]


def schema() -> dict:
    return make_schema("cefr_function_pass2_independent", {
        "row_id":{"type":"string"}, "sentence":{"type":"string"},
        "top_level_label":{"type":"string"}, "subcategory_id":{"type":"string"}, "subcategory_label":{"type":"string"},
        "function_id":{"type":"string"}, "function_label":{"type":"string"},
        "confidence":{"type":"string", "enum":["high","medium","low"]}, "rationale":{"type":"string"},
        "alternative_function_id":{"type":"string"}, "ambiguity_note":{"type":"string"}, "requires_review":{"type":"boolean"}}, FIELDS)


def annotate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy) -> dict:
    prompt = f"""
You are the SECOND INDEPENDENT communicative-function annotator. Make a fresh decision; you have not seen Pass 1.
Tag what the whole sentence is doing communicatively. Do not tag its topic, sampled lemma or lexical sense.
Use one function_id from the controlled taxonomy. Use low confidence and requires_review=true when uncertain.
Keep the rationale under 25 words.

TAXONOMY
{taxonomy_text}
SENTENCE
row_id: {row['row_id']}
{row['sentence']}
"""
    result = call_model_json(model, prompt, schema())
    result = apply_taxonomy_fields(result, "function_id", hierarchy)
    if result.get("alternative_function_id") not in hierarchy: result["alternative_function_id"] = ""
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent Function Pass 2.")
    parser.add_argument("--sentences", "--input", dest="sentences", required=True)
    parser.add_argument("--taxonomy", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass2")); parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.0); parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()
    records, _, hierarchy = read_taxonomy(Path(args.taxonomy)); taxonomy_text = compact_taxonomy_text(records)
    data = pd.read_csv(args.sentences, dtype=str).fillna(""); require_columns(data, ["sentence"], "Sentence sample")
    if "row_id" not in data.columns: data.insert(0, "row_id", [f"row_{i+1:06d}" for i in range(len(data))])
    if args.limit > 0: data = data.head(args.limit)
    output = Path(args.output); done = load_done_ids(output)
    for _, series in data.iterrows():
        row = {"row_id":str(series["row_id"]), "sentence":str(series["sentence"])}
        if row["row_id"] in done: continue
        if args.dry_run:
            fid = next(iter(hierarchy)); h = hierarchy[fid]
            result = {"row_id":row["row_id"], "sentence":row["sentence"], "top_level_label":h["top_level_label"], "subcategory_id":h["subcategory_id"], "subcategory_label":h["subcategory_label"], "function_id":fid, "function_label":h["function_label"], "confidence":"low", "rationale":"Dry run only", "alternative_function_id":"", "ambiguity_note":"", "requires_review":True}
        else: result = annotate(args.model, taxonomy_text, row, hierarchy)
        append_csv_row(output, FIELDS, result); done.add(row["row_id"])
        print(f"Function Pass 2 {row['row_id']}: {result['function_id']}")
        if args.sleep: time.sleep(args.sleep)

if __name__ == "__main__": main()
