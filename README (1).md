# ALTE Common Corpus SIG

Reproducible code, configuration, and methodological documentation for the
**ALTE Common Corpus SIG** pilot, supporting the **European CEFR Vocabulary Atlas**.

The project develops a transparent, repeatable workflow for corpus preparation,
lemmatisation, ARF-based sampling, sentence-level CEFR communicative-function
tagging, and expert review across English, French, Spanish, German, and Czech.

> **Pilot material — not validated CEFR data.**
> This project is methodological and exploratory. All LLM-generated outputs are
> **provisional Tier 4 candidate material** that require expert review and corpus
> validation before any CEFR claim is made.

**Project website:** https://pertam.github.io/ALTE-Common-Corpus-SIG/

## Pilot languages

English · French · Spanish · German · Czech

## What lives where

| Location | Holds |
| --- | --- |
| **GitHub** (this repo) | Code, scripts, notebooks, taxonomy files, configuration, documentation, small samples. Prompt instructions are version-controlled inside the tagging scripts. |
| **Google Drive** | Raw corpora, interim files, full LLM outputs, QA reports, logs, review workbooks. |
| **Colab** | Execution environment that clones this repo, mounts Drive, and runs the pipeline. |

Large corpora and full outputs are kept **outside** GitHub (e.g. in
`MyDrive/ALTE-Common-Corpus-SIG/` or institutional storage).

## Quickstart

The fastest route is the Colab runner, which handles cloning, Drive mounting, and
path checks for you:

[Open the main project runner in Colab](https://colab.research.google.com/github/Pertam/ALTE-Common-Corpus-SIG/blob/main/notebooks/00_main_project_runner_colab.ipynb)

To run the function-tagging scripts locally instead:

### 1. Install

```bash
git clone https://github.com/Pertam/ALTE-Common-Corpus-SIG.git
cd ALTE-Common-Corpus-SIG
pip install -r requirements.txt
```

### 2. Add your API key

```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
```

### 3. Prepare two input files

- A **taxonomy** CSV in `taxonomy/` with the columns `top_level_label`,
  `subcategory_id`, `subcategory_label`, `function_id`, `function_label`,
  `function_guidance`.
- A **sentences** CSV with at least the columns `row_id` and `sentence`.

### 4. Run the three tagging passes, then build the final dataset

```bash
# Pass 1 — first-pass function tagging
python scripts/run_pass1.py \
  --sentences sample_data/sentences_en.csv \
  --taxonomy  taxonomy/taxonomy_en.csv \
  --output    sample_data/pass1_en.csv

# Pass 2 — blind validation of Pass 1
python scripts/run_pass2.py \
  --pass1    sample_data/pass1_en.csv \
  --taxonomy taxonomy/taxonomy_en.csv \
  --output   sample_data/pass2_en.csv

# Pass 3 — adjudication (run where Pass 1 and Pass 2 disagree or confidence is low)
python scripts/run_pass3.py \
  --pass1    sample_data/pass1_en.csv \
  --pass2    sample_data/pass2_en.csv \
  --taxonomy taxonomy/taxonomy_en.csv \
  --output   sample_data/pass3_en.csv

# Merge into one reviewable dataset (--pass3 is optional)
python scripts/make_final_dataset.py \
  --pass1  sample_data/pass1_en.csv \
  --pass2  sample_data/pass2_en.csv \
  --pass3  sample_data/pass3_en.csv \
  --output sample_data/final_en.csv
```

Each script appends to its output file and skips `row_id`s already processed, so an
interrupted run can be safely restarted. Model choices and sampling thresholds are
set in `config/pipeline_config.yaml`.

## How the tagging works

| Pass | Purpose |
| --- | --- |
| **Pass 1** | Assigns an initial sentence-level communicative function from the controlled taxonomy. |
| **Pass 2** | Blindly validates Pass 1 — accepts, changes, or flags it as uncertain. |
| **Pass 3** | Adjudicates disagreements and low-confidence cases to produce a final candidate label. |

The exact prompt instructions are embedded in the scripts in `scripts/`, which are
the canonical record of what each run sent to the model.

## Requirements

- Python 3.10+
- An OpenAI API key (`OPENAI_API_KEY`)
- Packages in `requirements.txt`: `openai`, `pandas`, `tenacity`, `python-dotenv`

## Status

Pilot / methodological development. See the
[project website](https://pertam.github.io/ALTE-Common-Corpus-SIG/) for current stage,
data status, and next milestone.

## Licence

Code and notebooks in this repository are licensed under the **Apache License 2.0** —
see [`LICENSE`](LICENSE). Documentation, the taxonomy, and any corpus-derived data
may be subject to separate terms; corpus source material remains under its original
licence and is not redistributed here.

## Contact

Questions and feedback:
[open an issue](https://github.com/Pertam/ALTE-Common-Corpus-SIG/issues).
