#!/usr/bin/env python3
"""Stage 02: tokenise, POS-tag and lemmatise prepared sentences.

This script uses spaCy models. Install the appropriate model first, for example:

python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download es_core_news_sm
python -m spacy download de_core_news_sm

For Czech, use a model that is available in your environment and pass it with --model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}
DEFAULT_MODELS = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm",
    "es": "es_core_news_sm",
    "de": "de_core_news_sm",
    "cs": "cs_core_news_sm",
}


def load_spacy_model(model_name: str):
    try:
        import spacy
    except ImportError as exc:
        raise SystemExit("spaCy is not installed. Run: pip install spacy") from exc

    try:
        return spacy.load(model_name, disable=["ner"])
    except OSError as exc:
        raise SystemExit(
            f"spaCy model not installed: {model_name}\n"
            f"Install it first, e.g. python -m spacy download {model_name}\n"
            "For Czech, pass the exact installed model name with --model."
        ) from exc


def clean_lemma(lemma: str, token_text: str) -> str:
    lemma = (lemma or "").strip().lower()
    if not lemma or lemma == "-pron-":
        lemma = token_text.strip().lower()
    return lemma


def process(lang: str, model: str, input_path: Path, out_dir: Path, batch_size: int, n_process: int) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Prepared sentence parquet not found: {input_path}")

    nlp = load_spacy_model(model)
    sentences = pd.read_parquet(input_path)

    required = {"language_code", "sentence_id", "sentence_uid", "sentence", "source_id"}
    missing = required - set(sentences.columns)
    if missing:
        raise ValueError(f"Input sentence file is missing columns: {sorted(missing)}")

    token_rows: list[dict[str, object]] = []
    lemma_sentence_rows: list[dict[str, object]] = []

    texts = sentences["sentence"].astype(str).tolist()
    meta = sentences[["language_code", "sentence_id", "sentence_uid", "source_id"]].to_dict("records")

    pipe_kwargs = {"batch_size": batch_size}
    if n_process and n_process > 1:
        pipe_kwargs["n_process"] = n_process

    for doc, m in tqdm(zip(nlp.pipe(texts, **pipe_kwargs), meta), total=len(texts), desc=f"Tokenising {lang}"):
        seen_lemma_pos_in_sentence: set[tuple[str, str]] = set()

        for token_index, tok in enumerate(doc):
            if tok.is_space or tok.is_punct:
                continue

            lemma = clean_lemma(tok.lemma_, tok.text)
            pos = tok.pos_
            is_alpha = bool(tok.is_alpha)
            is_stop = bool(tok.is_stop)

            token_rows.append(
                {
                    **m,
                    "token_index": token_index,
                    "token": tok.text,
                    "lemma": lemma,
                    "pos": pos,
                    "is_alpha": is_alpha,
                    "is_stop": is_stop,
                }
            )

            if is_alpha and not is_stop and pos in CONTENT_POS and lemma:
                key = (lemma, pos)
                if key not in seen_lemma_pos_in_sentence:
                    lemma_sentence_rows.append(
                        {
                            "language_code": lang,
                            "lemma": lemma,
                            "pos": pos,
                            "sentence_id": m["sentence_id"],
                            "sentence_uid": m["sentence_uid"],
                            "source_id": m["source_id"],
                        }
                    )
                    seen_lemma_pos_in_sentence.add(key)

    out_dir.mkdir(parents=True, exist_ok=True)
    token_path = out_dir / f"{lang}_tokens.parquet"
    lemma_sentence_path = out_dir / f"{lang}_lemma_sentence_index.parquet"

    pd.DataFrame(token_rows).to_parquet(token_path, index=False)
    pd.DataFrame(lemma_sentence_rows).to_parquet(lemma_sentence_path, index=False)

    print(f"Tokens saved: {len(token_rows):,} -> {token_path}")
    print(f"Lemma-sentence rows saved: {len(lemma_sentence_rows):,} -> {lemma_sentence_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tokenise, POS-tag and lemmatise sentences with spaCy.")
    parser.add_argument("--lang", required=True)
    parser.add_argument("--input", required=True, help="Prepared sentence parquet from Stage 01")
    parser.add_argument("--out_dir", default="data/interim")
    parser.add_argument("--model", help="spaCy model name. If omitted, a default is used for known languages.")
    parser.add_argument("--batch_size", type=int, default=1000)
    parser.add_argument("--n_process", type=int, default=1)
    args = parser.parse_args()

    model = args.model or DEFAULT_MODELS.get(args.lang)
    if not model:
        raise ValueError(f"No default spaCy model for language {args.lang}. Pass --model explicitly.")

    process(
        lang=args.lang,
        model=model,
        input_path=Path(args.input),
        out_dir=Path(args.out_dir),
        batch_size=args.batch_size,
        n_process=args.n_process,
    )


if __name__ == "__main__":
    main()
