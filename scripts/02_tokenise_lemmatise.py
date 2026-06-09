"""Tokenise, POS-tag and lemmatise prepared sentences with spaCy.
Outputs one token table and one lemma-sentence index.
"""
from pathlib import Path
import argparse
import pandas as pd
import spacy
from tqdm import tqdm

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}


def load_model(model_name: str):
    try:
        return spacy.load(model_name, disable=["ner"])
    except OSError as e:
        raise SystemExit(
            f"spaCy model {model_name} is not installed. Install it, e.g. python -m spacy download {model_name}"
        ) from e


def process(lang: str, model: str, input_path: Path, out_dir: Path, batch_size: int = 1000) -> None:
    nlp = load_model(model)
    sents = pd.read_parquet(input_path)
    token_rows = []
    lemma_sentence_rows = []
    texts = sents["sentence"].astype(str).tolist()
    meta = sents[["language_code", "sentence_id", "sentence_uid", "source_id"]].to_dict("records")
    for doc, m in tqdm(zip(nlp.pipe(texts, batch_size=batch_size), meta), total=len(texts)):
        seen_lemma_pos = set()
        for i, tok in enumerate(doc):
            if tok.is_space or tok.is_punct:
                continue
            lemma = tok.lemma_.strip().lower()
            pos = tok.pos_
            row = {
                **m,
                "token_index": i,
                "token": tok.text,
                "lemma": lemma,
                "pos": pos,
                "is_alpha": tok.is_alpha,
                "is_stop": tok.is_stop
            }
            token_rows.append(row)
            if tok.is_alpha and not tok.is_stop and pos in CONTENT_POS and lemma:
                key = (lemma, pos)
                if key not in seen_lemma_pos:
                    lemma_sentence_rows.append({
                        "language_code": lang,
                        "lemma": lemma,
                        "pos": pos,
                        "sentence_id": m["sentence_id"],
                        "sentence_uid": m["sentence_uid"],
                        "source_id": m["source_id"]
                    })
                    seen_lemma_pos.add(key)
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(token_rows).to_parquet(out_dir / f"{lang}_tokens.parquet", index=False)
    pd.DataFrame(lemma_sentence_rows).to_parquet(out_dir / f"{lang}_lemma_sentence_index.parquet", index=False)
    print(f"Saved token and lemma-sentence files for {lang}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lang", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--out_dir", default="data/interim")
    args = p.parse_args()
    process(args.lang, args.model, Path(args.input), Path(args.out_dir))
