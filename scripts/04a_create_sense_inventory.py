#!/usr/bin/env python3
"""Stage 04a: propose coarse lexical-sense inventories for sampled lemmas."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import pandas as pd

from llm_function_tagging_utils import call_model_json, make_schema
from llm_sense_tagging_utils import ensure_target_columns

FIELDS = [
    "inventory_id", "language", "target_lemma", "target_pos", "sense_id",
    "sense_gloss", "distinguishing_features", "typical_patterns",
    "evidence_row_ids", "inventory_status", "expert_comment",
]


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper() or "ITEM"


def schema() -> dict:
    return make_schema(
        "provisional_sense_inventory",
        {"senses": {"type": "array", "minItems": 1, "maxItems": 12,
            "items": {"type": "object", "additionalProperties": False,
                "properties": {
                    "sense_gloss": {"type": "string"},
                    "distinguishing_features": {"type": "string"},
                    "typical_patterns": {"type": "string"},
                    "evidence_row_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["sense_gloss", "distinguishing_features", "typical_patterns", "evidence_row_ids"],
            }}},
        ["senses"],
    )


def propose(model: str, language: str, lemma: str, pos: str, examples: list[dict[str, str]]) -> list[dict]:
    evidence = "\n".join(f"{x['row_id']}: {x['sentence']}" for x in examples)
    prompt = f"""
Propose a small, coarse-grained lexical-sense inventory for this target lemma.
language: {language}
lemma: {lemma}
part of speech: {pos}

Split senses only where the distinction could materially affect translation,
grammatical construction, learner understanding, CEFR judgement or pedagogical
treatment. Prefer defensible broad senses over dictionary micro-senses. Analyse
the target lemma, not the communicative function of the whole sentence. Cite
representative row IDs. Do not add OTHER or UNCLEAR; the script adds them.

EXAMPLES
{evidence}
"""
    return call_model_json(model, prompt, schema())["senses"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create provisional sense inventories.")
    parser.add_argument("--samples", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--max_examples", type=int, default=50)
    parser.add_argument("--limit_lemmas", type=int, default=0)
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    data = ensure_target_columns(pd.read_csv(args.samples, dtype=str).fillna(""), "Samples")
    groups = list(data.groupby(["language", "target_lemma", "target_pos"], sort=True))
    if args.limit_lemmas > 0:
        groups = groups[:args.limit_lemmas]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    exists = output.exists() and output.stat().st_size > 0
    completed = set()
    if exists:
        previous = pd.read_csv(output, dtype=str).fillna("")
        completed = set(previous.get("inventory_id", []))

    with output.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        for (language, lemma, pos), group in groups:
            inventory_id = f"{language.lower()}__{safe_id(lemma)}__{safe_id(pos)}__v1"
            if inventory_id in completed:
                continue
            examples = group[["row_id", "sentence"]].head(args.max_examples).to_dict("records")
            senses = ([{"sense_gloss": "Dry-run placeholder sense", "distinguishing_features": "Testing only", "typical_patterns": "", "evidence_row_ids": [x["row_id"] for x in examples[:3]]}]
                      if args.dry_run else propose(args.model, language, lemma, pos, examples))
            prefix = f"{safe_id(lemma)}_{safe_id(pos)}"
            for number, sense in enumerate(senses, 1):
                writer.writerow({
                    "inventory_id": inventory_id, "language": language,
                    "target_lemma": lemma, "target_pos": pos,
                    "sense_id": f"{prefix}_{number:02d}",
                    "sense_gloss": sense["sense_gloss"],
                    "distinguishing_features": sense["distinguishing_features"],
                    "typical_patterns": sense["typical_patterns"],
                    "evidence_row_ids": json.dumps(sense["evidence_row_ids"], ensure_ascii=False),
                    "inventory_status": "provisional", "expert_comment": "",
                })
            for suffix, gloss in [
                ("OTHER", "A distinct interpretable sense missing from the approved inventory"),
                ("UNCLEAR", "The sentence context is insufficient to determine the sense"),
            ]:
                writer.writerow({
                    "inventory_id": inventory_id, "language": language,
                    "target_lemma": lemma, "target_pos": pos,
                    "sense_id": f"{prefix}_{suffix}", "sense_gloss": gloss,
                    "distinguishing_features": "", "typical_patterns": "",
                    "evidence_row_ids": "[]", "inventory_status": "provisional",
                    "expert_comment": "",
                })
            handle.flush()
            print(f"Proposed inventory: {inventory_id}")

    print(f"Output: {output}")
    print("NEXT: a human expert must revise the inventory and mark retained rows approved.")


if __name__ == "__main__":
    main()
