"""Prepare raw Leipzig sentence files into a normalised sentence table.

Expected input per language: data/raw/<lang>/<lang>_sentences.txt
Typical Leipzig sentence line is: <sentence_id>\t<sentence>
Output: data/interim/<lang>_sentences.parquet
"""
from pathlib import Path
import argparse
import hashlib
import pandas as pd


def uid(language_code: str, sentence: str) -> str:
    digest = hashlib.sha1(sentence.encode("utf-8")).hexdigest()[:12]
    return f"{language_code}_{digest}"


def prepare(language_code: str, in_path: Path, out_path: Path) -> None:
    rows = []
    with in_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if "\t" in line:
                sid, sentence = line.split("\t", 1)
            else:
                sid, sentence = None, line
            sentence = sentence.strip()
            if sentence:
                rows.append({
                    "language_code": language_code,
                    "sentence_id": int(sid) if sid and sid.isdigit() else len(rows) + 1,
                    "sentence_uid": uid(language_code, sentence),
                    "sentence": sentence,
                    "source_id": "leipzig_1m_news"
                })
    df = pd.DataFrame(rows).drop_duplicates("sentence_uid")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df):,} sentences to {out_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lang", required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    prepare(args.lang, Path(args.input), Path(args.output))
