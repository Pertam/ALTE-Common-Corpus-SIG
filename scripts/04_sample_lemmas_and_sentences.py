#!/usr/bin/env python3
"""Stage 04: sample lemmas and collect target-occurrence examples.

Current pilot setting
---------------------
- Random 15 eligible lemmas per language
- Eligible = content POS and pilot ARF-style metric >= 50
- All available target occurrences for each selected lemma by default

Each output row represents one precise corpus occurrence. ``row_id`` is retained
for downstream compatibility but is now an alias of the stable ``observation_id``.
Repeated occurrences of the same lemma in one sentence remain distinct.
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
    "frequency_metric_id",
    "frequency_metric_version",
    "frequency_metric_formula",
    "source_dispersion_unit",
]


def set_stable_row_ids(df: pd.DataFrame) -> pd.DataFrame:
    out = df.reset_index(drop=True).copy()
    if "observation_id" not in out.columns:
        raise ValueError("Occurrence-level input must contain observation_id. Rerun Stage 02 with the current data contract.")
    if (out["observation_id"].astype(str).str.strip() == "").any():
        raise ValueError("Blank observation_id found in occurrence index.")
    if out["observation_id"].duplicated().any():
        dupes = out.loc[out["observation_id"].duplicated(), "observation_id"].head(20).tolist()
        raise ValueError(f"Duplicate observation_id values in sampled output: {dupes}")
    if "row_id" in out.columns:
        out = out.drop(columns=["row_id"])
    out.insert(0, "row_id", out["observation_id"].astype(str))
    return out


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
        raise FileNotFoundError(f"Target-occurrence index file not found: {lemma_sentence_path}")
    if not sentence_path.exists():
        raise FileNotFoundError(f"Prepared sentence file not found: {sentence_path}")

    stats = pd.read_csv(stats_path, dtype={"language_code": str, "lemma": str, "pos": str}).fillna("")
    index = pd.read_parquet(lemma_sentence_path)
    sentences = pd.read_parquet(sentence_path)

    stats_required = {"language_code", "lemma", "pos", "arf_per_million"}
    index_required = {
        "observation_id", "language_code", "lemma", "pos", "sentence_id", "sentence_uid", "source_id",
        "target_token_index", "target_token", "target_char_start", "target_char_end",
    }
    sentence_required = {"sentence_uid", "sentence"}
    for label, df, required in [
        ("stats", stats, stats_required),
        ("target_occurrence", index, index_required),
        ("sentences", sentences, sentence_required),
    ]:
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"{label} file is missing columns: {sorted(missing)}. "
                "For occurrence fields, rerun Stage 02 with the current data contract."
            )

    if index["observation_id"].duplicated().any():
        raise ValueError("Target-occurrence index contains duplicate observation_id values.")

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
        ].copy()

        if candidates.empty:
            print(f"WARNING: no target occurrences for {lang} {lemma}/{pos}")
            continue

        if all_sentences:
            chosen = candidates.copy()
            sample_size_requested = "all_occurrences"
            sampling_method = "all_occurrences_for_selected_lemmas"
        else:
            take = min(int(sentences_n), len(candidates))
            chosen = candidates.sample(n=take, random_state=int(rng.integers(1, 2**31 - 1))).copy()
            sample_size_requested = sentences_n
            sampling_method = "random_occurrence_sample_for_selected_lemmas"

        merged = chosen.merge(sentences[["sentence_uid", "sentence"]], on="sentence_uid", how="left", validate="many_to_one")
        if merged["sentence"].astype(str).str.strip().eq("").any():
            raise ValueError(f"Sentence join failed for one or more sampled occurrences of {lang} {lemma}/{pos}.")

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
    out = set_stable_row_ids(out)

    ordered = [
        "row_id",
        "observation_id",
        "language_code",
        "lemma",
        "pos",
        "target_token",
        "target_token_index",
        "target_char_start",
        "target_char_end",
        "tokenizer_model",
        "tokenizer_model_version",
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
    print(f"Output target occurrences: {len(out):,}")
    print(f"Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample eligible lemmas and collect target-occurrence examples.")
    parser.add_argument("--lang", required=True)
    parser.add_argument("--stats", required=True)
    parser.add_argument("--lemma_sentence", required=True, help="Occurrence-level index from Stage 02; legacy filename retained")
    parser.add_argument("--sentences", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min_arf", type=float, default=50)
    parser.add_argument("--lemmas_n", type=int, default=15)
    parser.add_argument("--sentences_n", type=int, default=50, help="Number of target occurrences per lemma when not using --all_sentences")
    parser.add_argument("--all_sentences", action="store_true", help="Legacy flag name: include all target occurrences for each selected lemma")
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
