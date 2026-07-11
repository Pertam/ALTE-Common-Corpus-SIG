# Colab run commands for the six-stage pilot

Assumption:

```python
from pathlib import Path
REPO = Path('/content/ALTE-Common-Corpus-SIG')
DRIVE = Path('/content/drive/MyDrive/ALTE-Common-Corpus-SIG')
```

## Stages 1–3: corpus preparation, processing and sampling

Run the existing corpus scripts for each language, preserving stable `row_id`, `sentence`, `target_token`, `target_lemma` and `target_pos` columns in the sampled output.

```bash
python scripts/01_prepare_leipzig_sentences.py --lang en --input "$DRIVE/data/raw/en/en_sentences.txt" --output "$DRIVE/data/interim/en/en_sentences.parquet"
python scripts/02_tokenise_lemmatise.py --lang en --model en_core_web_sm --input "$DRIVE/data/interim/en/en_sentences.parquet" --out_dir "$DRIVE/data/interim/en"
python scripts/03_compute_lemma_stats.py --lang en --tokens "$DRIVE/data/interim/en/en_tokens.parquet" --lemma_sentence "$DRIVE/data/interim/en/en_lemma_sentence_index.parquet" --output "$DRIVE/data/processed/en/en_lemma_stats.csv"
python scripts/04_sample_lemmas_and_sentences.py --lang en --stats "$DRIVE/data/processed/en/en_lemma_stats.csv" --lemma_sentence "$DRIVE/data/interim/en/en_lemma_sentence_index.parquet" --sentences "$DRIVE/data/interim/en/en_sentences.parquet" --output "$DRIVE/data/processed/en/en_sampled_occurrences.csv" --min_arf 50 --lemmas_n 15 --sentences_n 50 --seed 20260603
```

## Stage 4A: provisional sense inventory

```bash
python scripts/04a_create_sense_inventory.py \
  --samples "$DRIVE/data/processed/en/en_sampled_occurrences.csv" \
  --output "$DRIVE/data/outputs/en/en_sense_inventory.csv"
```

A language expert must revise the inventory and mark retained rows `approved` before production tagging.

## Pass 1: initial sense and function annotations

```bash
python scripts/04b_run_sense_pass1.py \
  --samples "$DRIVE/data/processed/en/en_sampled_occurrences.csv" \
  --inventory "$DRIVE/data/outputs/en/en_sense_inventory.csv" \
  --output "$DRIVE/data/outputs/en/en_sense_pass1.csv"

python scripts/05a_run_pass1.py \
  --sentences "$DRIVE/data/processed/en/en_sampled_occurrences.csv" \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --output "$DRIVE/data/outputs/en/en_function_pass1.csv"
```

## Pass 2: informed critical reviews

```bash
python scripts/04c_run_sense_pass2.py \
  --samples "$DRIVE/data/processed/en/en_sampled_occurrences.csv" \
  --inventory "$DRIVE/data/outputs/en/en_sense_inventory.csv" \
  --pass1 "$DRIVE/data/outputs/en/en_sense_pass1.csv" \
  --function_pass1 "$DRIVE/data/outputs/en/en_function_pass1.csv" \
  --output "$DRIVE/data/outputs/en/en_sense_pass2_informed.csv"

python scripts/05b_run_pass2.py \
  --sentences "$DRIVE/data/processed/en/en_sampled_occurrences.csv" \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --pass1 "$DRIVE/data/outputs/en/en_function_pass1.csv" \
  --sense_pass1 "$DRIVE/data/outputs/en/en_sense_pass1.csv" \
  --output "$DRIVE/data/outputs/en/en_function_pass2_informed.csv"
```

## Optional blind-validation sample

Use a separately sampled CSV and separate output files:

```bash
python scripts/04c_run_sense_pass2.py --samples "$DRIVE/data/processed/en/en_blind_sample.csv" --inventory "$DRIVE/data/outputs/en/en_sense_inventory.csv" --blind --output "$DRIVE/data/outputs/en/en_sense_pass2_blind.csv"
python scripts/05b_run_pass2.py --sentences "$DRIVE/data/processed/en/en_blind_sample.csv" --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv --blind --output "$DRIVE/data/outputs/en/en_function_pass2_blind.csv"
```

## Targeted adjudication and combined review dataset

```bash
python scripts/04d_run_sense_adjudication.py --pass1 "$DRIVE/data/outputs/en/en_sense_pass1.csv" --pass2 "$DRIVE/data/outputs/en/en_sense_pass2_informed.csv" --inventory "$DRIVE/data/outputs/en/en_sense_inventory.csv" --only_problem_cases --output "$DRIVE/data/outputs/en/en_sense_pass3.csv"
python scripts/05c_run_pass3.py --pass1 "$DRIVE/data/outputs/en/en_function_pass1.csv" --pass2 "$DRIVE/data/outputs/en/en_function_pass2_informed.csv" --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv --only_problem_cases --output "$DRIVE/data/outputs/en/en_function_pass3.csv"
python scripts/06_make_final_dataset.py --samples "$DRIVE/data/processed/en/en_sampled_occurrences.csv" --sense_pass1 "$DRIVE/data/outputs/en/en_sense_pass1.csv" --sense_pass2 "$DRIVE/data/outputs/en/en_sense_pass2_informed.csv" --sense_pass3 "$DRIVE/data/outputs/en/en_sense_pass3.csv" --function_pass1 "$DRIVE/data/outputs/en/en_function_pass1.csv" --function_pass2 "$DRIVE/data/outputs/en/en_function_pass2_informed.csv" --function_pass3 "$DRIVE/data/outputs/en/en_function_pass3.csv" --output "$DRIVE/review/en_combined_review.csv"
```

Repeat for `fr`, `es`, `de` and `cs`, using the appropriate language models and paths.
