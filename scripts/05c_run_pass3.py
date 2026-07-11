#!/usr/bin/env python3
"""Stage 05c: adjudicate disagreements between independent function passes."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, apply_taxonomy_fields, call_model_json, compact_taxonomy_text, default_model, load_done_ids, make_schema, read_taxonomy, require_columns

FIELDS = ["row_id", "sentence", "pass1_function_id", "pass2_function_id", "final_function_id", "final_function_label", "final_confidence", "adjudication_rationale", "human_review_recommended"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate independent function passes.")
    parser.add_argument("--pass1", required=True); parser.add_argument("--pass2", required=True)
    parser.add_argument("--taxonomy", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass3")); parser.add_argument("--only_problem_cases", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    p1 = pd.read_csv(args.pass1, dtype=str).fillna(""); p2 = pd.read_csv(args.pass2, dtype=str).fillna("")
    required = ["row_id", "sentence", "function_id", "confidence", "rationale"]
    require_columns(p1, required, "Function Pass 1"); require_columns(p2, required, "Function Pass 2")
    left = p1.rename(columns={"function_id":"pass1_function_id", "confidence":"pass1_confidence", "rationale":"pass1_rationale"})
    right = p2[["row_id", "function_id", "confidence", "rationale"]].rename(columns={"function_id":"pass2_function_id", "confidence":"pass2_confidence", "rationale":"pass2_rationale"})
    cases = left.merge(right, on="row_id")
    if args.only_problem_cases:
        cases = cases[(cases.pass1_function_id != cases.pass2_function_id) | (cases.pass1_confidence == "low") | (cases.pass2_confidence == "low")]
    if args.limit > 0: cases = cases.head(args.limit)

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy)); taxonomy_text = compact_taxonomy_text(records)
    output = Path(args.output); done = load_done_ids(output)
    properties = {"row_id":{"type":"string"}, "pass1_function_id":{"type":"string"}, "pass2_function_id":{"type":"string"}, "final_function_id":{"type":"string"}, "final_function_label":{"type":"string"}, "final_confidence":{"type":"string", "enum":["high","medium","low"]}, "adjudication_rationale":{"type":"string"}, "human_review_recommended":{"type":"boolean"}}
    required_output = ["row_id", "pass1_function_id", "pass2_function_id", "final_function_id", "final_function_label", "final_confidence", "adjudication_rationale", "human_review_recommended"]
    schema = make_schema("function_adjudication", properties, required_output)
    for _, series in cases.iterrows():
        row = {key:str(value) for key,value in series.to_dict().items()}
        if row["row_id"] in done: continue
        prompt = f"""Adjudicate two independent sentence-function annotations. Judge what the whole sentence is doing, not its topic, sampled lemma or lexical sense. Use the controlled taxonomy. Recommend human review if ambiguity remains.
TAXONOMY
{taxonomy_text}
SENTENCE
{row['sentence']}
PASS 1: {row['pass1_function_id']} | {row['pass1_confidence']} | {row['pass1_rationale']}
PASS 2: {row['pass2_function_id']} | {row['pass2_confidence']} | {row['pass2_rationale']}"""
        result = call_model_json(args.model, prompt, schema); result = apply_taxonomy_fields(result, "final_function_id", hierarchy)
        result["sentence"] = row["sentence"]
        append_csv_row(output, FIELDS, result); done.add(row["row_id"])
        print(f"Function adjudication {row['row_id']}: {result['final_function_id']}")

if __name__ == "__main__": main()
