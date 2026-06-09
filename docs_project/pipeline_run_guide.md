# CEFR Vocabulary Atlas Pilot — Stage 1–5 Pipeline Additions

This folder contains the GitHub-ready scripts, configuration and templates needed to make the early corpus stages of the European CEFR Vocabulary Atlas pilot reproducible.

## What this adds

```text
scripts/
  00_validate_inputs.py
  01_prepare_leipzig_sentences.py
  02_tokenise_lemmatise.py
  03_compute_lemma_stats.py
  04_sample_lemmas_and_sentences.py
  05_run_pass1_function_tagging.py
  06_run_pass2_blind_validation.py
  07_build_lemma_function_profiles.py
  08_quality_checks.py
  09_export_review_workbook.py

config/
  project_config.yaml

taxonomy/
  cefr_function_taxonomy_v0_2.csv

templates/
  raw_leipzig_sentence_format.txt
  stage1_sentences_schema.csv
  tokens_schema.csv
  lemma_sentence_index_schema.csv
  lemma_stats_schema.csv
  stage3_sampled_sentences_schema.csv
  review_workbook_columns.csv
  drive_folder_structure.md
  colab_run_commands.md
```

## Stage mapping

| Project stage | Script(s) | Purpose |
|---|---|---|
| Stage 1 | `01_prepare_leipzig_sentences.py` | Normalise raw Leipzig sentence files into stable sentence tables. |
| Stage 2 | `02_tokenise_lemmatise.py`, `03_compute_lemma_stats.py` | Tokenise, lemmatise, POS-tag and compute frequency/dispersion/ARF-style lemma evidence. |
| Stage 3 | `04_sample_lemmas_and_sentences.py` | Select eligible lemmas and sample sentences for function tagging. |
| Stage 4 | `05_run_pass1_function_tagging.py`, `06_run_pass2_blind_validation.py` | LLM-assisted sentence-level function tagging and blind validation. |
| Stage 5 | `07_build_lemma_function_profiles.py`, `08_quality_checks.py`, `09_export_review_workbook.py` | Aggregate lemma functional profiles, QA and reviewer workbook export. |

## Final sampling decision used in the pilot

The final pilot sampling decision was:

```text
languages: English, French, Spanish, German, Czech
content POS: NOUN, VERB, ADJ, ADV
minimum ARF per million: 50
lemmas per language: 15
sentences per lemma: 50
random seed: 20260603
```

The important methodological change was that we moved away from trying to tag huge batches of 750+ rows directly in chat. Instead, the workflow creates reproducible sample CSVs and then sends rows through the API in resumable batches with explicit validation.

## Important methodological note

The ARF-style value implemented here is a transparent pilot approximation. It is not claimed as externally validated ARF evidence and is not a CEFR level. It is a reproducible filtering and sampling aid.
