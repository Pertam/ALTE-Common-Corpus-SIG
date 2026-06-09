"""Stage 04: sample lemmas and collect sentence examples.

This script selects a reproducible random sample of eligible lemmas and then
collects sentence examples for each selected lemma.

Eligibility:
- content POS only: NOUN, VERB, ADJ, ADV
- arf_per_million >= configured threshold

Sampling modes:
1. --all_sentences
   Keep all available sentence examples for each selected lemma.

2. --sentences_n N
   Keep up to N randomly sampled sentence examples for each selected lemma.

This is part of the ALTE Common Corpus SIG / European CEFR Vocabulary Atlas
pilot workflow. Outputs are methodological pilot data, not validated CEFR data.
"""

from pathlib import Path
import argparse
import pandas as pd
import numpy as np


CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}


STATS_COLUMNS_TO_KEEP = [
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


def sample_lemmas_and_sentences(
    lang: str,
    stats_path: Path,
    lemma_sentence_path: Path,
    sentence_path: Path,
    out_path: Path,
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
        raise FileNotFoundError(f"Sentence file not found: {sentence_path}")

    stats = pd.read_csv(stats_path)
    idx = pd.read_parquet(lemma_sentence_path)
    sentences = pd.read_parquet(sentence_path)

    required_stats_cols = {"language_code", "lemma", "pos", "arf_per_million"}
    missing_stats_cols = required_stats_cols - set(stats.columns)
    if missing_stats_cols:
        raise ValueError(f"Stats file is missing required columns: {sorted(missing_stats_cols)}")

    required_idx_cols = {"language_code", "lemma", "pos", "sentence_uid", "sentence_id", "source_id"}
    missing_idx_cols = required_idx_cols - set(idx.columns)
    if missing_idx_cols:
        raise ValueError(f"Lemma-sentence index is missing required columns: {sorted(missing_idx_cols)}")

    required_sentence_cols = {"sentence_uid", "sentence"}
    missing_sentence_cols = required_sentence_cols - set(sentences.columns)
    if missing_sentence_cols:
        raise ValueError(f"Sentence file is missing required columns: {sorted(missing_sentence_cols)}")

    stats_lang = stats[stats["language_code"] == lang].copy()

    eligible = stats_lang[
        (stats_lang["arf_per_million"] >= min_arf)
        & (stats_lang["pos"].isin(CONTENT_POS))
    ].copy()

    if len(eligible) < lemmas_n:
        raise ValueError(
            f"Only {len(eligible)} eligible lemmas for {lang}; requested {lemmas_n}. "
            f"Try lowering --lemmas_n or --min_arf."
        )

    selected = eligible.sample(n=lemmas_n, random_state=seed).copy()
    selected = selected.sort_values(["pos", "lemma"]).reset_index(drop=True)

    outputs = []

    for _, lemma_row in selected.iterrows():
        lemma = lemma_row["lemma"]
        pos = lemma_row["pos"]

        candidates = idx[
            (idx["language_code"] == lang)
            & (idx["lemma"] == lemma)
            & (idx["pos"] == pos)
        ].drop_duplicates("sentence_uid").copy()

        if candidates.empty:
            continue

        if all_sentences:
            chosen = candidates.copy()
            sample_size_requested = "all_sentences"
        else:
            take = min(sentences_n, len(candidates))
            random_state = int(rng.integers(1, 2**31 - 1))
            chosen = candidates.sample(n=take, random_state=random_state).copy()
            sample_size_requested = sentences_n

        merged = chosen.merge(
            sentences[["sentence_uid", "sentence"]],
            on="sentence_uid",
            how="left",
        )

        for col in STATS_COLUMNS_TO_KEEP:
            if col in lemma_row.index:
                merged[col] = lemma_row[col]
            else:
                merged[col] = None

        merged["sample_size_requested"] = sample_size_requested
        merged["sample_size_available"] = len(candidates)
        merged["sample_size_taken"] = len(chosen)
        merged["has_full_requested_sample"] = True if all_sentences else len(chosen) == min(sentences_n, len(candidates))
        merged["min_arf_per_million"] = min_arf
        merged["sampling_method"] = "all_sentences_for_selected_lemmas" if all_sentences else "random_sentence_sample_for_selected_lemmas"
        merged["random_seed"] = seed

        outputs.append(merged)

    if not outputs:
        raise ValueError(f"No sentence rows were produced for language {lang}.")

    out = pd.concat(outputs, ignore_index=True)

    ordered_cols = [
        "language_code",
        "lemma",
        "pos",
        "raw_frequency",
        "frequency_per_million",
        "sentence_count",
        "sentence_dispersion",
        "source_count",
        "source_dispersion",
        "arf_reduced_frequency",
        "arf_per_million",
        "frequency_band",
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

    existing_ordered_cols = [c for c in ordered_cols if c in out.columns]
    remaining_cols = [c for c in out.columns if c not in existing_ordered_cols]
    out = out[existing_ordered_cols + remaining_cols]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    print(f"Language: {lang}")
    print(f"Selected lemmas: {lemmas_n}")
    print(f"Sentence rows saved: {len(out):,}")
    print(f"Output: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--lang", required=True, help="Language code, e.g. en, fr, es, de, cs")
    parser.add_argument("--stats", required=True, help="Path to lemma stats CSV")
    parser.add_argument("--lemma_sentence", required=True, help="Path to lemma-sentence index parquet")
    parser.add_argument("--sentences", required=True, help="Path to prepared sentence parquet")
    parser.add_argument("--output", required=True, help="Output CSV path")

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
        out_path=Path(args.output),
        min_arf=args.min_arf,
        lemmas_n=args.lemmas_n,
        sentences_n=args.sentences_n,
        all_sentences=args.all_sentences,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
