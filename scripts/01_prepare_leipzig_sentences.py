#!/usr/bin/env python3
"""Stage 01: prepare raw Leipzig sentence files.

Input
-----
A text file with either:
- Leipzig format: <sentence_id> TAB <sentence>
- or one sentence per line.

Output
------
A parquet file with:
- language_code
- sentence_id
- sentence_uid
- sentence
- source_id
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


def make_sentence_uid(language_code: str, source_id: str, sentence_id: int, sentence: str) -> str:
    digest = hashlib.sha1(f"{language_code}|{source_id}|{sentence_id}|{sentence}".encode("utf-8")).hexdigest()[:16]
    return f"{language_code}_{digest}"


def parse_line(line: str, fallback_id: int) -> tuple[int, str]:
    line = line.rstrip("\n\r")
    if "\t" in line:
        left, sentence = line.split("\t", 1)
        left = left.strip()
        sentence = sentence.strip()
        if left.isdigit():
            return int(left), sentence
    return fallback_id, line.strip()


def prepare_sentences(language_code: str, input_path: Path, output_path: Path, source_id: str) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows: list[dict[str, object]] = []
    seen_sentences: set[str] = set()

    with input_path.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            sentence_id, sentence = parse_line(line, fallback_id=i)
            if not sentence:
                continue
            normalised = " ".join(sentence.split())
            if normalised in seen_sentences:
                continue
            seen_sentences.add(normalised)
            rows.append(
                {
                    "language_code": language_code,
                    "sentence_id": sentence_id,
                    "sentence_uid": make_sentence_uid(language_code, source_id, sentence_id, normalised),
                    "sentence": normalised,
                    "source_id": source_id,
                }
            )

    if not rows:
        raise ValueError(f"No usable sentences found in {input_path}")

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Language: {language_code}")
    print(f"Sentences saved: {len(df):,}")
    print(f"Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare raw Leipzig sentence text as parquet.")
    parser.add_argument("--lang", required=True, help="Language code, e.g. en, fr, es, de, cs")
    parser.add_argument("--input", required=True, help="Raw Leipzig sentence text file")
    parser.add_argument("--output", required=True, help="Output parquet path")
    parser.add_argument("--source_id", default="leipzig_1m_news", help="Source identifier stored in output")
    args = parser.parse_args()

    prepare_sentences(
        language_code=args.lang,
        input_path=Path(args.input),
        output_path=Path(args.output),
        source_id=args.source_id,
    )


if __name__ == "__main__":
    main()
