# Google Drive data manifest and compatibility status

This manifest records how the existing June 2026 Google Drive outputs relate to the current sense-aware GitHub pipeline.

## Preservation rule

The folders below are a completed historical run and are treated as **frozen legacy data**:

```text
en/
fr/
es/
de/
cs/
```

No current notebook or script should delete, rename, move or overwrite files in those folders. New sense-aware outputs belong under:

```text
sense_aware_v2/
```

## Existing layout

Each language folder contains:

```text
stage00_raw_sentences/
stage01_prepared_sentences/
stage02_tokenise_lemmatise/
stage03_lemma_stats/
stage04_samples/
stage05_llm_tagging/
stage06_final_dataset/
```

The five-language 50-row test chain is complete. For each language there is:

```text
stage04_<lang>_dispersed_test50_normalised_for_stage05.csv
stage05_<lang>_pass1_dispersed_test50.csv
stage05_<lang>_pass2_dispersed_test50.csv
stage05_<lang>_pass3_dispersed_test50.csv
stage06_<lang>_final_dispersed_test50.csv
```

## Compatibility classification

| Existing artefact | Status in current workflow | Reason |
|---|---|---|
| Raw, prepared, lemma-index and lemma-statistics data | Preserved and reusable | They remain valid corpus evidence and are not affected by the added sense layer. |
| Corrected full Stage 4 sample | Reusable | Supplies broad sentence evidence for provisional sense-inventory development. |
| Normalised Stage 4 `dispersed_test50` sample | Reusable through a non-destructive v2 copy | It contains stable row IDs, language, lemma, POS and sentence; aliases must be made explicit. |
| June Function Pass 1 | Reusable | Current Function Pass 1 is still an independent whole-sentence annotation and its required columns match. |
| June Function Pass 2 | Legacy reference only | It is a function-only validator and lacks Pass 1 sense context, `interaction_note`, `review_mode`, and the current rationale schema. |
| June Function Pass 3 | Legacy reference only | It adjudicates the old function-only Pass 2 rather than the informed sense-aware review. |
| June Stage 6 final | Legacy reference only | It is a valid merged function-only dataset but contains no lexical-sense layer. |

## Known limitations retained in provenance

The June Stage 4 samples identify the target lemma and POS but do not store the exact target surface token. V2 input copies therefore use:

```text
target_token = ""
target_token_status = "not_recorded_in_legacy_sample"
```

The workflow must not silently invent a token value.

## Taxonomy authority

The reviewed Drive taxonomy contains the same 248 function IDs as the repository copy and also contains a populated `function_guidance` column. The Drive copy was the taxonomy used for the June annotation work and should be preferred by the Colab runner. The repository copy should be synchronised with it so local and Drive runs use the same prompts.

## V2 layout

```text
sense_aware_v2/
  <lang>/
    inputs/
    sense_inventory/
    sense_pass1/
    sense_pass2/
    function_pass2/
    adjudication/
    combined_review/
    blind_validation/
```

The v2 workflow reuses the legacy Function Pass 1 but creates new sense inventories, sense annotations, informed Pass 2 reviews, targeted adjudication and combined review files.

## Audit tool

Run:

```bash
python scripts/00_audit_drive_outputs.py \
  --drive_root /content/drive/MyDrive/ALTE-Common-Corpus-SIG \
  --repo_root /content/ALTE-Common-Corpus-SIG
```

The audit is read-only. Optional report arguments create new audit files; they do not alter existing project data.
