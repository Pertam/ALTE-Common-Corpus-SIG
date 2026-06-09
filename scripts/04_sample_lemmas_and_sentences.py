"""Randomly select eligible lemmas and sample all required sentences for each lemma.
Designed to reproduce the Stage 5 pilot sample: 15 lemmas x 50 sentences = 750 rows per language.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np


def sample(lang: str, stats_path: Path, lemma_sentence_path: Path, sentence_path: Path,
           out_path: Path, min_arf: float, lemmas_n: int, sentences_n: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    stats = pd.read_csv(stats_path)
    idx = pd.read_parquet(lemma_sentence_path)
    sentences = pd.read_parquet(sentence_path)
    eligible = stats[(stats["arf_per_million"] >= min_arf) & (stats["pos"].isin(["NOUN", "VERB", "ADJ", "ADV"]))].copy()
    if len(eligible) < lemmas_n:
        raise ValueError(f"Only {len(eligible)} eligible lemmas; requested {lemmas_n}")
    selected = eligible.sample(n=lemmas_n, random_state=seed)
    outputs = []
    for _, lemma_row in selected.iterrows():
        lemma, pos = lemma_row["lemma"], lemma_row["pos"]
        candidates = idx[(idx["lemma"] == lemma) & (idx["pos"] == pos)].drop_duplicates("sentence_uid")
        take = min(sentences_n, len(candidates))
        chosen = candidates.sample(n=take, random_state=int(rng.integers(1, 2**31 - 1)))
        merged = chosen.merge(sentences[["sentence_uid", "sentence"]], on="sentence_uid", how="left")
        for c in ["raw_frequency", "frequency_per_million", "sentence_count", "sentence_dispersion", "source_count", "source_dispersion", "arf_reduced_frequency", "arf_per_million", "frequency_band"]:
            merged[c] = lemma_row[c]
        merged["sample_size_requested"] = sentences_n
        merged["sample_size_available"] = len(candidates)
        merged["sample_size_taken"] = take
        merged["has_full_requested_sample"] = take == sentences_n
        merged["min_arf_per_million"] = min_arf
        merged["sampling_method"] = "random_sample_from_eligible_lemma_sentences"
        merged["random_seed"] = seed
        outputs.append(merged)
    out = pd.concat(outputs, ignore_index=True)
    out = out[["language_code", "lemma", "pos", "raw_frequency", "frequency_per_million", "sentence_count", "sentence_dispersion", "source_count", "source_dispersion", "arf_reduced_frequency", "arf_per_million", "frequency_band", "sample_size_requested", "sample_size_available", "sample_size_taken", "has_full_requested_sample", "min_arf_per_million", "sampling_method", "random_seed", "sentence_id", "sentence_uid", "sentence"]]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Saved {len(out):,} sampled sentence rows to {out_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lang", required=True)
    p.add_argument("--stats", required=True)
    p.add_argument("--lemma_sentence", required=True)
    p.add_argument("--sentences", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--min_arf", type=float, default=50)
    p.add_argument("--lemmas_n", type=int, default=15)
    p.add_argument("--sentences_n", type=int, default=50)
    p.add_argument("--seed", type=int, default=20260603)
    args = p.parse_args()
    sample(args.lang, Path(args.stats), Path(args.lemma_sentence), Path(args.sentences), Path(args.output), args.min_arf, args.lemmas_n, args.sentences_n, args.seed)
