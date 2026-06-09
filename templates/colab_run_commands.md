# Colab run commands for Stage 1–5

Assumption:

```python
from pathlib import Path
REPO = Path('/content/ALTE-Common-Corpus-SIG')
DRIVE = Path('/content/drive/MyDrive/ALTE_Common_Corpus_SIG')
```

## Stage 1: prepare sentences

```bash
python scripts/01_prepare_leipzig_sentences.py \
  --lang en \
  --input "$DRIVE/data/raw/en/en_sentences.txt" \
  --output "$DRIVE/data/interim/en/en_sentences.parquet"
```

## Stage 2a: tokenise, POS-tag and lemmatise

```bash
python scripts/02_tokenise_lemmatise.py \
  --lang en \
  --model en_core_web_sm \
  --input "$DRIVE/data/interim/en/en_sentences.parquet" \
  --out_dir "$DRIVE/data/interim/en"
```

## Stage 2b: compute lemma statistics

```bash
python scripts/03_compute_lemma_stats.py \
  --lang en \
  --tokens "$DRIVE/data/interim/en/en_tokens.parquet" \
  --lemma_sentence "$DRIVE/data/interim/en/en_lemma_sentence_index.parquet" \
  --output "$DRIVE/data/processed/en/en_lemma_stats.csv"
```

## Stage 3: sample lemmas and sentences

```bash
python scripts/04_sample_lemmas_and_sentences.py \
  --lang en \
  --stats "$DRIVE/data/processed/en/en_lemma_stats.csv" \
  --lemma_sentence "$DRIVE/data/interim/en/en_lemma_sentence_index.parquet" \
  --sentences "$DRIVE/data/interim/en/en_sentences.parquet" \
  --output "$DRIVE/data/processed/en/en_stage5_random_15_lemmas_50_sentences.csv" \
  --min_arf 50 \
  --lemmas_n 15 \
  --sentences_n 50 \
  --seed 20260603
```

Repeat the same commands for `fr`, `es`, `de`, and `cs`, changing the language code and spaCy model.
