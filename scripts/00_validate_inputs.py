#!/usr/bin/env python3
"""Stage 00: validate pipeline inputs and key schemas.

This script is deliberately conservative: it checks only the files you ask it to
check. It can therefore be run at any stage of the workflow.

Examples
--------
python scripts/00_validate_inputs.py \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv

python scripts/00_validate_inputs.py \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --sample data/stage4_samples/stage4_en_random_15_lemmas_all_sentences.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

TAXONOMY_REQUIRED = {
    "top_level_label",
    "subcategory_id",
    "subcategory_label",
    "function_id",
    "function_label",
}

SAMPLE_MINIMUM_REQUIRED = {
    "row_id",
    "language_code",
    "lemma",
    "pos",
    "sentence_uid",
    "sentence",
}

PASS1_REQUIRED = {
    "row_id",
    "sentence",
    "top_level_label",
    "subcategory_id",
    "subcategory_label",
    "function_id",
    "function_label",
    "confidence",
    "rationale",
    "alternative_function_id",
    "ambiguity_note",
    "requires_review",
}

PASS2_REQUIRED = {
    "row_id",
    "sentence",
    "pass1_function_id",
    "validator_decision",
    "function_id",
    "function_label",
    "confidence",
    "validation_rationale",
    "requires_review",
}

PASS3_REQUIRED = {
    "row_id",
    "sentence",
    "pass1_function_id",
    "pass2_function_id",
    "final_function_id",
    "final_function_label",
    "final_confidence",
    "adjudication_rationale",
    "human_review_recommended",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path, dtype=str).fillna("")


def check_columns(df: pd.DataFrame, required: Iterable[str], label: str, path: Path) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{label} file {path} is missing required columns: {sorted(missing)}")


def validate_taxonomy(path: Path) -> None:
    df = read_csv(path)
    check_columns(df, TAXONOMY_REQUIRED, "Taxonomy", path)
    if df["function_id"].duplicated().any():
        dupes = df.loc[df["function_id"].duplicated(), "function_id"].tolist()
        raise ValueError(f"Duplicate function_id values in taxonomy: {dupes[:20]}")
    if (df["function_id"].str.strip() == "").any():
        raise ValueError("Taxonomy contains blank function_id values.")
    print(f"OK taxonomy: {path} ({len(df):,} rows, {df['function_id'].nunique():,} functions)")


def validate_sample(path: Path) -> None:
    df = read_csv(path)
    check_columns(df, SAMPLE_MINIMUM_REQUIRED, "Sample", path)
    if df["row_id"].duplicated().any():
        dupes = df.loc[df["row_id"].duplicated(), "row_id"].tolist()
        raise ValueError(f"Duplicate row_id values in sample: {dupes[:20]}")
    if (df["sentence"].str.strip() == "").any():
        raise ValueError("Sample contains blank sentence values.")
    print(f"OK sample: {path} ({len(df):,} rows)")


def validate_pass(path: Path, required: set[str], label: str) -> None:
    df = read_csv(path)
    check_columns(df, required, label, path)
    if df["row_id"].duplicated().any():
        dupes = df.loc[df["row_id"].duplicated(), "row_id"].tolist()
        raise ValueError(f"Duplicate row_id values in {label}: {dupes[:20]}")
    print(f"OK {label}: {path} ({len(df):,} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CEFR Vocabulary Atlas pipeline input/output files.")
    parser.add_argument("--taxonomy", help="Path to taxonomy CSV")
    parser.add_argument("--sample", help="Path to sampled sentence CSV")
    parser.add_argument("--pass1", help="Path to Pass 1 CSV")
    parser.add_argument("--pass2", help="Path to Pass 2 CSV")
    parser.add_argument("--pass3", help="Path to Pass 3 CSV")
    args = parser.parse_args()

    if args.taxonomy:
        validate_taxonomy(Path(args.taxonomy))
    if args.sample:
        validate_sample(Path(args.sample))
    if args.pass1:
        validate_pass(Path(args.pass1), PASS1_REQUIRED, "Pass 1")
    if args.pass2:
        validate_pass(Path(args.pass2), PASS2_REQUIRED, "Pass 2")
    if args.pass3:
        validate_pass(Path(args.pass3), PASS3_REQUIRED, "Pass 3")

    if not any([args.taxonomy, args.sample, args.pass1, args.pass2, args.pass3]):
        parser.error("Provide at least one file to validate.")

    print("Validation complete.")


if __name__ == "__main__":
    main()
