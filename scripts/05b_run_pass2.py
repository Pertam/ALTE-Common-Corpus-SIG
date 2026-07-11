#!/usr/bin/env python3
"""Stage 05b: informed critical review of the Pass 1 sentence-function annotation.

Production mode sees both the Pass 1 function and the Pass 1 lexical sense.
Use --blind only for a sampled reliability study.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, apply_taxonomy_fields, call_model_json, compact_taxonomy_text, default_model, load_done_ids, make_schema, read_taxonomy, require_columns

FIELDS = [
    "row_id", "sentence", "pass1_function_id", "pass1_sense_id", "pass1_sense_gloss",
    "validator_decision", "top_level_label", "subcategory_id", "subcategory_label",
    "function_id", "function_label", "confidence", "rationale",
    "alternative_function_id", "ambiguity_note", "interaction_note",
    "requires_review", "review_mode",
]


def schema() -> dict:
    return make_schema(
        "cefr_function_pass2_review",
        {
            "row_id": {"type": "string"},
            "validator_decision": {"type": "string", "enum": ["accept", "change", "uncertain"]},
            "top_level_label": {"type": "string"},
            "subcategory_id": {"type": "string"},
            "subcategory_label": {"type": "string"},
            "function_id": {"type": "string"},
            "function_label": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "rationale": {"type": "string"},
            "alternative_function_id": {"type": "string"},
            "ambiguity_note": {"type": "string"},
            "interaction_note": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        ["row_id", "validator_decision", "top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "confidence", "rationale", "alternative_function_id", "ambiguity_note", "interaction_note", "requires_review"],
    )


def annotate(model: str, taxonomy_text: str, row: dict[str, str], hierarchy, blind: bool) -> dict:
    prior = "" if blind else f"""
PASS 1 FUNCTION PROPOSAL
function_id: {row['pass1_function_id']}
function_label: {row['pass1_function_label']}
confidence: {row['pass1_function_confidence']}
rationale: {row['pass1_function_rationale']}

PASS 1 LEXICAL-SENSE PROPOSAL
sense_id: {row['pass1_sense_id']}
sense_gloss: {row['pass1_sense_gloss']}
confidence: {row['pass1_sense_confidence']}
rationale: {row['pass1_sense_rationale']}
"""
    role = "BLIND communicative-function annotator for a reliability sample" if blind else "INFORMED CRITICAL REVIEWER of the Pass 1 communicative-function annotation"
    prompt = f"""
You are the {role}.

Decide what the whole sentence is doing communicatively. In informed mode, critically inspect the Pass 1 function, rationale and proposed target-lemma sense. The lexical sense may provide useful context, but it must not determine the sentence function. Accept Pass 1 only when it is defensible; otherwise change it or mark it uncertain.

Do not tag the sentence topic. Use one function_id from the controlled taxonomy. Keep the rationale under 35 words. In interaction_note, state briefly whether the proposed sense helped, conflicted with, or was irrelevant to the function decision. Recommend human review for unresolved ambiguity or a likely taxonomy problem.

CONTROLLED TAXONOMY
{taxonomy_text}

SENTENCE
row_id: {row['row_id']}
{row['sentence']}
{prior}
"""
    result = call_model_json(model, prompt, schema())
    result = apply_taxonomy_fields(result, "function_id", hierarchy)
    if result.get("alternative_function_id") not in hierarchy:
        result["alternative_function_id"] = ""
    result["sentence"] = row["sentence"]
    result["pass1_function_id"] = "" if blind else row["pass1_function_id"]
    result["pass1_sense_id"] = "" if blind else row["pass1_sense_id"]
    result["pass1_sense_gloss"] = "" if blind else row["pass1_sense_gloss"]
    result["review_mode"] = "blind_validation" if blind else "informed_review"
    return result


def build_cases(samples: pd.DataFrame, function_pass1: str | None, sense_pass1: str | None, blind: bool) -> pd.DataFrame:
    if blind:
        result = samples.copy()
        for column in ["pass1_function_id", "pass1_function_label", "pass1_function_confidence", "pass1_function_rationale", "pass1_sense_id", "pass1_sense_gloss", "pass1_sense_confidence", "pass1_sense_rationale"]:
            result[column] = ""
        return result
    if not function_pass1 or not sense_pass1:
        raise ValueError("Informed review requires --pass1 and --sense_pass1. Use --blind only for a sampled blind-validation run.")
    function = pd.read_csv(function_pass1, dtype=str).fillna("")
    sense = pd.read_csv(sense_pass1, dtype=str).fillna("")
    require_columns(function, ["row_id", "function_id", "function_label", "confidence", "rationale"], "Function Pass 1")
    require_columns(sense, ["row_id", "sense_id", "sense_gloss", "confidence", "rationale"], "Sense Pass 1")
    function = function[["row_id", "function_id", "function_label", "confidence", "rationale"]].rename(columns={"function_id":"pass1_function_id", "function_label":"pass1_function_label", "confidence":"pass1_function_confidence", "rationale":"pass1_function_rationale"})
    sense = sense[["row_id", "sense_id", "sense_gloss", "confidence", "rationale"]].rename(columns={"sense_id":"pass1_sense_id", "sense_gloss":"pass1_sense_gloss", "confidence":"pass1_sense_confidence", "rationale":"pass1_sense_rationale"})
    return samples.merge(function, on="row_id", how="inner").merge(sense, on="row_id", how="inner")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run informed Function Pass 2 review.")
    parser.add_argument("--sentences", "--input", dest="sentences", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--pass1", help="Function Pass 1 CSV; required unless --blind")
    parser.add_argument("--sense_pass1", help="Sense Pass 1 CSV; required unless --blind")
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=default_model("pass2"))
    parser.add_argument("--blind", action="store_true", help="Do not show Pass 1 outputs; use only for a sampled reliability study")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    records, _, hierarchy = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(records)
    samples = pd.read_csv(args.sentences, dtype=str).fillna("")
    require_columns(samples, ["sentence"], "Sentence sample")
    if "row_id" not in samples.columns:
        samples.insert(0, "row_id", [f"row_{i+1:06d}" for i in range(len(samples))])
    data = build_cases(samples, args.pass1, args.sense_pass1, args.blind)
    if args.limit > 0:
        data = data.head(args.limit)
    output = Path(args.output)
    done = load_done_ids(output)
    for _, series in data.iterrows():
        row = {key: str(value) for key, value in series.to_dict().items()}
        if row["row_id"] in done:
            continue
        if args.dry_run:
            fid = next(iter(hierarchy))
            h = hierarchy[fid]
            result = {
                "row_id": row["row_id"],
                "sentence": row["sentence"],
                "pass1_function_id": "" if args.blind else row["pass1_function_id"],
                "pass1_sense_id": "" if args.blind else row["pass1_sense_id"],
                "pass1_sense_gloss": "" if args.blind else row["pass1_sense_gloss"],
                "validator_decision": "uncertain",
                "top_level_label": h["top_level_label"],
                "subcategory_id": h["subcategory_id"],
                "subcategory_label": h["subcategory_label"],
                "function_id": fid,
                "function_label": h["function_label"],
                "confidence": "low",
                "rationale": "Dry run only",
                "alternative_function_id": "",
                "ambiguity_note": "Dry run only",
                "interaction_note": "Dry run only",
                "requires_review": True,
                "review_mode": "blind_validation" if args.blind else "informed_review",
            }
        else:
            result = annotate(args.model, taxonomy_text, row, hierarchy, args.blind)
        append_csv_row(output, FIELDS, result)
        done.add(row["row_id"])
        print(f"Function Pass 2 {row['row_id']}: {result['validator_decision']} -> {result['function_id']} ({result['review_mode']})")
        if args.sleep:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
