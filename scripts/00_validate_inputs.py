#!/usr/bin/env python3
"""Stage 00: validate key pipeline data contracts.

The validator is deliberately conservative: it checks only files supplied on the
command line.  It now covers occurrence identity, sense inventories and both
sense/function review chains.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

TAXONOMY_REQUIRED = {
    "top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label",
}

SAMPLE_REQUIRED = {
    "row_id", "observation_id", "language_code", "lemma", "pos",
    "target_token", "target_char_start", "target_char_end",
    "sentence_uid", "sentence",
}

FUNCTION_PASS1_REQUIRED = {
    "row_id", "sentence", "top_level_label", "subcategory_id", "subcategory_label",
    "function_id", "function_label", "confidence", "rationale",
    "alternative_function_id", "ambiguity_note", "requires_review",
}

FUNCTION_PASS2_REQUIRED = {
    "row_id", "sentence", "pass1_function_id", "validator_decision",
    "function_id", "function_label", "confidence", "rationale",
    "interaction_note", "requires_review", "review_mode",
}

FUNCTION_PASS3_REQUIRED = {
    "row_id", "sentence", "pass1_function_id", "pass2_function_id",
    "final_function_id", "final_function_label", "final_function_confidence",
    "adjudication_rationale", "human_review_recommended",
}

SENSE_INVENTORY_REQUIRED = {
    "inventory_id", "inventory_version", "language", "target_lemma", "target_pos",
    "sense_id", "sense_role", "sense_gloss", "inventory_status",
}

SENSE_PASS1_REQUIRED = {
    "row_id", "sentence", "language", "target_lemma", "target_pos", "inventory_id",
    "sense_id", "sense_gloss", "confidence", "rationale", "requires_review",
}

SENSE_PASS2_REQUIRED = {
    "row_id", "sentence", "language", "target_lemma", "target_pos", "inventory_id",
    "pass1_sense_id", "validator_decision", "sense_id", "sense_gloss",
    "confidence", "rationale", "interaction_note", "requires_review", "review_mode",
}

SENSE_PASS3_REQUIRED = {
    "row_id", "sentence", "language", "target_lemma", "target_pos", "inventory_id",
    "pass1_sense_id", "pass2_sense_id", "final_sense_id", "final_sense_gloss",
    "final_sense_confidence", "adjudication_rationale", "human_review_recommended",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path, dtype=str).fillna("")


def check_columns(df: pd.DataFrame, required: Iterable[str], label: str, path: Path) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{label} file {path} is missing required columns: {sorted(missing)}")


def check_unique_ids(df: pd.DataFrame, label: str) -> None:
    if "row_id" not in df.columns:
        return
    if (df["row_id"].astype(str).str.strip() == "").any():
        raise ValueError(f"{label} contains blank row_id values.")
    if df["row_id"].duplicated().any():
        dupes = df.loc[df["row_id"].duplicated(), "row_id"].head(20).tolist()
        raise ValueError(f"Duplicate row_id values in {label}: {dupes}")


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
    check_columns(df, SAMPLE_REQUIRED, "Sample", path)
    check_unique_ids(df, "sample")
    mismatch = df["row_id"].astype(str) != df["observation_id"].astype(str)
    if mismatch.any():
        raise ValueError("Sample row_id must equal stable observation_id.")
    if df["observation_id"].duplicated().any():
        raise ValueError("Sample contains duplicate observation_id values.")
    if (df["sentence"].str.strip() == "").any():
        raise ValueError("Sample contains blank sentence values.")

    # Verify that occurrence spans point to the recorded surface token.
    for _, row in df.iterrows():
        try:
            start = int(row["target_char_start"])
            end = int(row["target_char_end"])
        except ValueError as exc:
            raise ValueError(f"Non-integer target span for {row['row_id']}.") from exc
        sentence = str(row["sentence"])
        if start < 0 or end <= start or end > len(sentence):
            raise ValueError(f"Invalid target span for {row['row_id']}: {start}:{end}")
        if sentence[start:end] != str(row["target_token"]):
            raise ValueError(
                f"Target span mismatch for {row['row_id']}: sentence[{start}:{end}]="
                f"{sentence[start:end]!r} but target_token={row['target_token']!r}"
            )
    print(f"OK occurrence sample: {path} ({len(df):,} rows)")


def validate_pass(path: Path, required: set[str], label: str) -> None:
    df = read_csv(path)
    check_columns(df, required, label, path)
    check_unique_ids(df, label)
    print(f"OK {label}: {path} ({len(df):,} rows)")


def validate_sense_inventory(path: Path) -> None:
    df = read_csv(path)
    check_columns(df, SENSE_INVENTORY_REQUIRED, "Sense inventory", path)
    if (df["inventory_id"].str.strip() == "").any() or (df["sense_id"].str.strip() == "").any():
        raise ValueError("Sense inventory contains blank inventory_id or sense_id values.")
    if df["sense_id"].duplicated().any():
        dupes = df.loc[df["sense_id"].duplicated(), "sense_id"].head(20).tolist()
        raise ValueError(f"Duplicate sense_id values: {dupes}")
    grouped = df.groupby(["language", "target_lemma", "target_pos"])["inventory_id"].nunique()
    if (grouped > 1).any():
        raise ValueError(
            "Inventory file contains multiple inventory versions for the same language/lemma/POS. "
            "Use one explicit inventory version per tagging run."
        )
    print(f"OK sense inventory: {path} ({len(df):,} senses, {df['inventory_id'].nunique():,} inventories)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CEFR Vocabulary Atlas pipeline input/output files.")
    parser.add_argument("--taxonomy", help="Path to taxonomy CSV")
    parser.add_argument("--sample", help="Path to sampled target-occurrence CSV")
    parser.add_argument("--pass1", help="Path to Function Pass 1 CSV")
    parser.add_argument("--pass2", help="Path to Function Pass 2 CSV")
    parser.add_argument("--pass3", help="Path to Function Pass 3 CSV")
    parser.add_argument("--sense_inventory", help="Path to sense inventory CSV")
    parser.add_argument("--sense_pass1", help="Path to Sense Pass 1 CSV")
    parser.add_argument("--sense_pass2", help="Path to Sense Pass 2 CSV")
    parser.add_argument("--sense_pass3", help="Path to Sense Pass 3 CSV")
    args = parser.parse_args()

    if args.taxonomy: validate_taxonomy(Path(args.taxonomy))
    if args.sample: validate_sample(Path(args.sample))
    if args.pass1: validate_pass(Path(args.pass1), FUNCTION_PASS1_REQUIRED, "Function Pass 1")
    if args.pass2: validate_pass(Path(args.pass2), FUNCTION_PASS2_REQUIRED, "Function Pass 2")
    if args.pass3: validate_pass(Path(args.pass3), FUNCTION_PASS3_REQUIRED, "Function Pass 3")
    if args.sense_inventory: validate_sense_inventory(Path(args.sense_inventory))
    if args.sense_pass1: validate_pass(Path(args.sense_pass1), SENSE_PASS1_REQUIRED, "Sense Pass 1")
    if args.sense_pass2: validate_pass(Path(args.sense_pass2), SENSE_PASS2_REQUIRED, "Sense Pass 2")
    if args.sense_pass3: validate_pass(Path(args.sense_pass3), SENSE_PASS3_REQUIRED, "Sense Pass 3")

    if not any(vars(args).values()):
        parser.error("Provide at least one file to validate.")
    print("Validation complete.")


if __name__ == "__main__":
    main()
