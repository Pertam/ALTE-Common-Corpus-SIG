#!/usr/bin/env python3
"""Stage 03: compute lemma frequency, dispersion and pilot ARF-style statistics.

Important methodological note
-----------------------------
The ARF value here is a transparent pilot measure based on raw token frequency
and sentence dispersion. It is not external CEFR evidence and should not be
reported as validated corpus evidence outside this pilot workflow.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}


def compute_stats(lang: str, token_path: Path, lemma_sentence_path: Path, output_path: Path) -> None:
    if not token_path.exists():
        raise FileNotFoundError(f"Token file not found: {token_path}")
    if not lemma_sentence_path.exists():
        raise FileNotFoundError(f"Lemma-sentence index file not found: {lemma_sentence_path}")

    tokens = pd.read_parquet(token_path)
    lemma_sentence = pd.read_parquet(lemma_sentence_path)

    token_required = {"language_code", "lemma", "pos", "is_alpha", "sentence_uid", "source_id"}
    index_required = {"language_code", "lemma", "pos", "sentence_uid", "source_id"}
    missing_tokens = token_required - set(tokens.columns)
    missing_index = index_required - set(lemma_sentence.columns)
    if missing_tokens:
        raise ValueError(f"Token file is missing columns: {sorted(missing_tokens)}")
    if missing_index:
        raise ValueError(f"Lemma-sentence index is missing columns: {sorted(missing_index)}")

    tokens = tokens[tokens["language_code"].astype(str) == lang].copy()
    lemma_sentence = lemma_sentence[lemma_sentence["language_code"].astype(str) == lang].copy()

    if tokens.empty:
        raise ValueError(f"No token rows for language {lang}")

    total_tokens = len(tokens)
    total_sentences = max(tokens["sentence_uid"].nunique(), 1)
    total_sources = max(tokens["source_id"].nunique(), 1)

    frequency_base = tokens[
        (tokens["is_alpha"].astype(bool))
        & (tokens["pos"].isin(CONTENT_POS))
        & (tokens["lemma"].astype(str).str.strip() != "")
    ].copy()

    freq = (
        frequency_base.groupby(["language_code", "lemma", "pos"], as_index=False)
        .size()
        .rename(columns={"size": "raw_frequency"})
    )

    dispersion = (
        lemma_sentence.groupby(["language_code", "lemma", "pos"], as_index=False)
        .agg(
            sentence_count=("sentence_uid", "nunique"),
            source_count=("source_id", "nunique"),
        )
    )

    stats = freq.merge(dispersion, on=["language_code", "lemma", "pos"], how="left")
    stats["sentence_count"] = stats["sentence_count"].fillna(0).astype(int)
    stats["source_count"] = stats["source_count"].fillna(0).astype(int)

    stats["frequency_per_million"] = stats["raw_frequency"] / total_tokens * 1_000_000
    stats["sentence_dispersion"] = stats["sentence_count"] / total_sentences
    stats["source_dispersion"] = stats["source_count"] / total_sources

    # Practical pilot reduced frequency: raw frequency penalised if sentence dispersion is low.
    stats["arf_reduced_frequency"] = stats["raw_frequency"] * np.sqrt(stats["sentence_dispersion"].clip(lower=0))
    stats["arf_per_million"] = stats["arf_reduced_frequency"] / total_tokens * 1_000_000

    stats["frequency_band"] = pd.cut(
        stats["arf_per_million"],
        bins=[-1, 10, 50, 100, 500, np.inf],
        labels=["very_low", "low", "medium", "high", "very_high"],
    ).astype(str)

    stats = stats.sort_values(["arf_per_million", "raw_frequency", "lemma"], ascending=[False, False, True])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(output_path, index=False)

    print(f"Language: {lang}")
    print(f"Total tokens used as denominator: {total_tokens:,}")
    print(f"Lemma rows saved: {len(stats):,}")
    print(f"Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute lemma frequency and pilot ARF-style statistics.")
    parser.add_argument("--lang", required=True)
    parser.add_argument("--tokens", required=True, help="Token parquet from Stage 02")
    parser.add_argument("--lemma_sentence", required=True, help="Lemma-sentence parquet from Stage 02")
    parser.add_argument("--output", required=True, help="Output lemma stats CSV")
    args = parser.parse_args()

    compute_stats(
        lang=args.lang,
        token_path=Path(args.tokens),
        lemma_sentence_path=Path(args.lemma_sentence),
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()
