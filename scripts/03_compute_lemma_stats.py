"""Compute lemma frequency, dispersion and ARF-like reduced frequency.

The ARF implementation here is a practical, transparent approximation for the pilot.
It rewards lemmas distributed across many sentence/source units and penalises bursty lemmas.
Keep the raw components so the SIG can replace the formula if it adopts a different ARF definition.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np


def compute(lang: str, token_path: Path, lemma_sentence_path: Path, out_path: Path) -> None:
    tokens = pd.read_parquet(token_path)
    idx = pd.read_parquet(lemma_sentence_path)
    total_tokens = len(tokens)
    total_sentences = tokens["sentence_uid"].nunique()
    total_sources = tokens["source_id"].nunique()

    freq = (tokens.loc[tokens["is_alpha"]]
            .groupby(["language_code", "lemma", "pos"], as_index=False)
            .size()
            .rename(columns={"size": "raw_frequency"}))
    sent = (idx.groupby(["language_code", "lemma", "pos"], as_index=False)
            .agg(sentence_count=("sentence_uid", "nunique"), source_count=("source_id", "nunique")))
    stats = freq.merge(sent, on=["language_code", "lemma", "pos"], how="left")
    stats["frequency_per_million"] = stats["raw_frequency"] / total_tokens * 1_000_000
    stats["sentence_dispersion"] = stats["sentence_count"] / max(total_sentences, 1)
    stats["source_dispersion"] = stats["source_count"] / max(total_sources, 1)
    # Reduced frequency: raw frequency adjusted by square-root of sentence dispersion.
    # This is not claimed as external evidence; it is a reproducible pilot measure.
    stats["arf_reduced_frequency"] = stats["raw_frequency"] * np.sqrt(stats["sentence_dispersion"].clip(lower=0))
    stats["arf_per_million"] = stats["arf_reduced_frequency"] / total_tokens * 1_000_000
    stats["frequency_band"] = pd.cut(
        stats["arf_per_million"],
        bins=[-1, 10, 50, 100, 500, np.inf],
        labels=["very_low", "low", "medium", "high", "very_high"]
    ).astype(str)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stats.sort_values("arf_per_million", ascending=False).to_csv(out_path, index=False)
    print(f"Saved {len(stats):,} lemma rows to {out_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lang", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--lemma_sentence", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    compute(args.lang, Path(args.tokens), Path(args.lemma_sentence), Path(args.output))
