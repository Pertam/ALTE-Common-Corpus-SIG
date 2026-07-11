# CEFR Vocabulary Atlas Pilot — Six-Stage Pipeline

This guide summarises the reproducible workflow for corpus preparation, target-occurrence sampling, lexical-sense tagging, communicative-function tagging and expert review.

## Stage mapping

| Project stage | Main scripts | Purpose |
|---|---|---|
| Stage 1 | `01_prepare_leipzig_sentences.py` | Normalise raw sentence files and preserve source metadata. |
| Stage 2 | `02_tokenise_lemmatise.py`, `03_compute_lemma_stats.py` | Tokenise, lemmatise, POS-tag and compute frequency and dispersion evidence. |
| Stage 3 | `04_sample_lemmas_and_sentences.py` | Select eligible lemmas and create stable target-occurrence rows. |
| Stage 4 | `04a_create_sense_inventory.py`, `04b_run_sense_pass1.py`, `04c_run_sense_pass2.py`, `04d_run_sense_adjudication.py` | Create human-approved sense inventories, initial sense annotations, informed reviews and targeted adjudication. |
| Stage 5 | `05a_run_pass1.py`, `05b_run_pass2.py`, `05c_run_pass3.py` | Create initial sentence-function annotations, informed reviews and targeted adjudication. |
| Stage 6 | `06_make_final_dataset.py` and review tools | Combine evidence, preserve provenance and support expert review and sense-level aggregation. |

## Pilot sampling decision

```text
languages: English, French, Spanish, German, Czech
content POS: NOUN, VERB, ADJ, ADV
minimum ARF per million: 50
lemmas per language: 15
sentences per lemma: 50
random seed: 20260603
```

## Annotation sequence

1. Create and human-approve a language-specific sense inventory for each sampled lemma and POS.
2. Run Sense Pass 1 and Function Pass 1 as separate initial decisions.
3. Run informed Sense Pass 2 with access to Pass 1 sense and function.
4. Run informed Function Pass 2 with access to Pass 1 function and sense.
5. Adjudicate changed, uncertain, low-confidence and flagged rows.
6. Merge outputs for expert review while retaining separate final sense and function decisions.

## Blind-validation sample

The Pass 2 scripts support `--blind`. Use this only on a smaller separately sampled subset, with separate output files. Compare blind, informed and human outcomes to estimate reliability and possible anchoring.

## Important methodological notes

- One row represents one target lemma occurrence in one sentence.
- Sense belongs to the target occurrence; function belongs to the whole sentence.
- Informed review may use the other annotation as contextual evidence but not as proof.
- Language-specific senses are developed before cross-language concept alignment.
- ARF-style values are transparent pilot approximations and are not CEFR levels.
- All model-generated outputs remain provisional Tier 4 candidate material until expert review and validation.
