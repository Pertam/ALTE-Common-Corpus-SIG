#!/usr/bin/env python3
"""Stage 04: sample lemmas and collect sentence examples.

Current pilot setting
---------------------
- Random 15 eligible lemmas per language
- Eligible = content POS and ARF per million >= 50
- All available sentence examples for each selected lemma

The script also supports a capped sentence sample, e.g. --sentences_n 50,
when a smaller LLM batch is needed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}
STATS_COLUMNS = [
    "raw_frequency",
    "frequency_per_million",
    "sentence_count",
    "sentence_dispersion",
    "source_count",
    "source_dispersion",
    "arf_reduced_frequency",
    "arf_per_million",
    "frequency_band",
]


def add_row_ids(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    df = df.reset_index(drop=True).copy()
    df.insert(0, "row_id", [f"{lang}_{i + 1:06d}" for i in range(len(df))])
    return df


def sample_lemmas_and_sentences(
    lang: str,
    stats_path: Path,
    lemma_sentence_path: Path,
    sentence_path: Path,
    output_path: Path,
    min_arf: float,
    lemmas_n: int,
    sentences_n: int,
    all_sentences: bool,
    seed: int,
) -> None:
    rng = np.random.default_rng(seed)

    if not stats_path.exists():
        raise FileNotFoundError(f"Lemma stats file not found: {stats_path}")
    if not lemma_sentence_path.exists():
        raise FileNotFoundError(f"Lemma-sentence index file not found: {lemma_sentence_path}")
    if not sentence_path.exists():
        raise FileNotFoundError(f"Prepared sentence file not found: {sentence_path}")

    stats = pd.read_csv(stats_path, dtype={"language_code": str, "lemma": str, "pos": str}).fillna("")
    index = pd.read_parquet(lemma_sentence_path)
    sentences = pd.read_parquet(sentence_path)

    stats_required = {"language_code", "lemma", "pos", "arf_per_million"}
    index_required = {"language_code", "lemma", "pos", "sentence_id", "sentence_uid", "source_id"}
    sentence_required = {"sentence_uid", "sentence"}
    for label, df, required in [
        ("stats", stats, stats_required),
        ("lemma_sentence", index, index_required),
        ("sentences", sentences, sentence_required),
    ]:
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{label} file is missing columns: {sorted(missing)}")

    stats["arf_per_million"] = pd.to_numeric(stats["arf_per_million"], errors="coerce").fillna(0)
    stats_lang = stats[stats["language_code"].astype(str) == lang].copy()

    eligible = stats_lang[
        (stats_lang["pos"].isin(CONTENT_POS))
        & (stats_lang["arf_per_million"] >= float(min_arf))
    ].copy()

    if len(eligible) < lemmas_n:
        raise ValueError(
            f"Only {len(eligible)} eligible lemmas for {lang}; requested {lemmas_n}. "
            f"Lower --lemmas_n or --min_arf."
        )

    selected = eligible.sample(n=lemmas_n, random_state=seed).sort_values(["pos", "lemma"]).reset_index(drop=True)

    output_parts: list[pd.DataFrame] = []

    for _, lemma_row in selected.iterrows():
        lemma = str(lemma_row["lemma"])
        pos = str(lemma_row["pos"])

        candidates = index[
            (index["language_code"].astype(str) == lang)
            & (index["lemma"].astype(str) == lemma)
            & (index["pos"].astype(str) == pos)
        ].drop_duplicates("sentence_uid")

        if candidates.empty:
            print(f"WARNING: no sentence examples for {lang} {lemma}/{pos}")
            continue

        if all_sentences:
            chosen = candidates.copy()
            sample_size_requested = "all_sentences"
            sampling_method = "all_sentences_for_selected_lemmas"
        else:
            take = min(int(sentences_n), len(candidates))
            chosen = candidates.sample(n=take, random_state=int(rng.integers(1, 2**31 - 1))).copy()
            sample_size_requested = sentences_n
            sampling_method = "random_sentence_sample_for_selected_lemmas"

        merged = chosen.merge(sentences[["sentence_uid", "sentence"]], on="sentence_uid", how="left")

        for col in STATS_COLUMNS:
            merged[col] = lemma_row[col] if col in lemma_row.index else ""

        merged["sample_size_requested"] = sample_size_requested
        merged["sample_size_available"] = len(candidates)
        merged["sample_size_taken"] = len(chosen)
        merged["has_full_requested_sample"] = True if all_sentences else len(chosen) == min(sentences_n, len(candidates))
        merged["min_arf_per_million"] = min_arf
        merged["sampling_method"] = sampling_method
        merged["random_seed"] = seed

        output_parts.append(merged)

    if not output_parts:
        raise ValueError(f"No sampled rows produced for {lang}")

    out = pd.concat(output_parts, ignore_index=True)
    out = add_row_ids(out, lang)

    ordered = [
        "row_id",
        "language_code",
        "lemma",
        "pos",
        *STATS_COLUMNS,
        "sample_size_requested",
        "sample_size_available",
        "sample_size_taken",
        "has_full_requested_sample",
        "min_arf_per_million",
        "sampling_method",
        "random_seed",
        "sentence_id",
        "sentence_uid",
        "source_id",
        "sentence",
    ]
    ordered = [c for c in ordered if c in out.columns]
    out = out[ordered + [c for c in out.columns if c not in ordered]]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Language: {lang}")
    print(f"Selected lemmas: {lemmas_n}")
    print(f"Output rows: {len(out):,}")
    print(f"Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample eligible lemmas and collect sentence examples.")
    parser.add_argument("--lang", required=True)
    parser.add_argument("--stats", required=True)
    parser.add_argument("--lemma_sentence", required=True)
    parser.add_argument("--sentences", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min_arf", type=float, default=50)
    parser.add_argument("--lemmas_n", type=int, default=15)
    parser.add_argument("--sentences_n", type=int, default=50)
    parser.add_argument("--all_sentences", action="store_true")
    parser.add_argument("--seed", type=int, default=20260603)
    args = parser.parse_args()

    sample_lemmas_and_sentences(
        lang=args.lang,
        stats_path=Path(args.stats),
        lemma_sentence_path=Path(args.lemma_sentence),
        sentence_path=Path(args.sentences),
        output_path=Path(args.output),
        min_arf=args.min_arf,
        lemmas_n=args.lemmas_n,
        sentences_n=args.sentences_n,
        all_sentences=args.all_sentences,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
