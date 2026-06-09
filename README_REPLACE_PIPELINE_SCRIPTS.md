# Replacement pipeline scripts

This package replaces the placeholder/duplicate scripts with a coherent runnable pipeline:

- `scripts/00_validate_inputs.py`
- `scripts/01_prepare_leipzig_sentences.py`
- `scripts/02_tokenise_lemmatise.py`
- `scripts/03_compute_lemma_stats.py`
- `scripts/04_sample_lemmas_and_sentences.py`
- `scripts/05a_run_pass1.py`
- `scripts/05b_run_pass2.py`
- `scripts/05c_run_pass3.py`
- `scripts/06_make_final_dataset.py`
- `scripts/llm_function_tagging_utils.py`

The Stage 05 scripts support `--dry_run` so the pipeline structure can be tested without making API calls.

## Minimal Stage 05/06 test on an existing sampled sentence file

```bash
python scripts/05a_run_pass1.py --sentences data/stage4_samples/stage4_en_random_15_lemmas_all_sentences.csv --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv --output outputs/pass1_en.csv --dry_run --limit 5
python scripts/05b_run_pass2.py --pass1 outputs/pass1_en.csv --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv --output outputs/pass2_en.csv --dry_run
python scripts/05c_run_pass3.py --pass1 outputs/pass1_en.csv --pass2 outputs/pass2_en.csv --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv --output outputs/pass3_en.csv --dry_run
python scripts/06_make_final_dataset.py --samples data/stage4_samples/stage4_en_random_15_lemmas_all_sentences.csv --pass1 outputs/pass1_en.csv --pass2 outputs/pass2_en.csv --pass3 outputs/pass3_en.csv --output outputs/final_en_sentence_function_dataset.csv
```

Remove `--dry_run` when you are ready to call the OpenAI API and have set `OPENAI_API_KEY`.
