# Colab run commands for the Drive-aware sense-and-function pilot

The project already contains a completed June 2026 **function-only legacy run** in Google Drive. Do not delete, rename, move or overwrite those files.

The current sense-aware workflow:

- reads the corrected June Stage 4 samples;
- reuses the June Function Pass 1 annotations where compatible;
- retains the June Function Pass 2, Pass 3 and Stage 6 files as historical comparison data;
- writes every new file under `sense_aware_v2/`.

The recommended entry point is:

```text
notebooks/00_main_project_runner_colab.ipynb
```

That notebook begins with a read-only audit and keeps write operations disabled until `ALLOW_NEW_WRITES = True` is set deliberately.

## Drive roots

```python
from pathlib import Path

REPO = Path('/content/ALTE-Common-Corpus-SIG')
DRIVE = Path('/content/drive/MyDrive/ALTE-Common-Corpus-SIG')
V2 = DRIVE / 'sense_aware_v2'

# Prefer the reviewed Drive taxonomy, which includes the full function_guidance field.
TAXONOMY = DRIVE / 'taxonomy' / 'cefr_function_taxonomy_v0_2.csv'
```

## Existing files that are reused

For each language code `en`, `fr`, `es`, `de`, and `cs`:

```python
LANG = 'en'
LEGACY = DRIVE / LANG

FULL_SAMPLE = LEGACY / 'stage04_samples' / f'stage04_{LANG}_random_15_lemmas_all_sentences.csv'
TEST50 = LEGACY / 'stage04_samples' / f'stage04_{LANG}_dispersed_test50_normalised_for_stage05.csv'
FUNCTION_PASS1 = LEGACY / 'stage05_llm_tagging' / f'stage05_{LANG}_pass1_dispersed_test50.csv'
```

`FULL_SAMPLE` supplies evidence for the provisional sense inventory. `TEST50` is copied non-destructively into the v2 area with explicit target aliases. `FUNCTION_PASS1` is reused because the current Function Pass 1 remains independent of lexical-sense annotation.

## Read-only alignment audit

```bash
python scripts/00_audit_drive_outputs.py \
  --drive_root "/content/drive/MyDrive/ALTE-Common-Corpus-SIG" \
  --repo_root "/content/ALTE-Common-Corpus-SIG"
```

Optional timestamped reports may be written to `audit_reports/`; no project data are changed.

## V2 output layout

```text
sense_aware_v2/
  en/
    inputs/en_test50_target_occurrences.csv
    sense_inventory/en_sense_inventory_v1.csv
    sense_pass1/en_sense_pass1_test50.csv
    sense_pass2/en_sense_pass2_informed_test50.csv
    function_pass2/en_function_pass2_informed_test50.csv
    adjudication/en_sense_pass3_problem_cases.csv
    adjudication/en_function_pass3_problem_cases.csv
    combined_review/en_combined_sense_function_test50.csv
    blind_validation/...
  fr/
  es/
  de/
  cs/
```

## Create a v2-compatible target-occurrence copy

Do not edit the June source CSV. Create a new copy that makes the legacy aliases explicit:

```python
import pandas as pd

lang = 'en'
source = DRIVE / lang / 'stage04_samples' / f'stage04_{lang}_dispersed_test50_normalised_for_stage05.csv'
output = V2 / lang / 'inputs' / f'{lang}_test50_target_occurrences.csv'

if not output.exists():
    frame = pd.read_csv(source, dtype=str, encoding='utf-8-sig').fillna('')
    frame['target_token'] = ''
    frame['target_lemma'] = frame['lemma']
    frame['target_pos'] = frame['pos']
    frame['source_pipeline'] = 'legacy_june_2026_function_only_run'
    frame['source_file'] = str(source)
    frame['target_token_status'] = 'not_recorded_in_legacy_sample'
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
else:
    print('Keeping existing file:', output)
```

The exact target surface token was not retained in the June samples. This is recorded explicitly rather than silently inferred.

## Propose a sense inventory

Use the corrected full sample because the inventory should be informed by up to 50 examples for each selected lemma:

```bash
python scripts/04a_create_sense_inventory.py \
  --samples "$DRIVE/en/stage04_samples/stage04_en_random_15_lemmas_all_sentences.csv" \
  --output "$V2/en/sense_inventory/en_sense_inventory_v1.csv" \
  --max_examples 50
```

A language expert must revise the inventory and mark retained rows `inventory_status=approved` before production tagging.

## Sense Pass 1

```bash
python scripts/04b_run_sense_pass1.py \
  --samples "$V2/en/inputs/en_test50_target_occurrences.csv" \
  --inventory "$V2/en/sense_inventory/en_sense_inventory_v1.csv" \
  --output "$V2/en/sense_pass1/en_sense_pass1_test50.csv"
```

## Informed Pass 2 reviews

```bash
python scripts/04c_run_sense_pass2.py \
  --samples "$V2/en/inputs/en_test50_target_occurrences.csv" \
  --inventory "$V2/en/sense_inventory/en_sense_inventory_v1.csv" \
  --pass1 "$V2/en/sense_pass1/en_sense_pass1_test50.csv" \
  --function_pass1 "$DRIVE/en/stage05_llm_tagging/stage05_en_pass1_dispersed_test50.csv" \
  --output "$V2/en/sense_pass2/en_sense_pass2_informed_test50.csv"

python scripts/05b_run_pass2.py \
  --sentences "$V2/en/inputs/en_test50_target_occurrences.csv" \
  --taxonomy "$TAXONOMY" \
  --pass1 "$DRIVE/en/stage05_llm_tagging/stage05_en_pass1_dispersed_test50.csv" \
  --sense_pass1 "$V2/en/sense_pass1/en_sense_pass1_test50.csv" \
  --output "$V2/en/function_pass2/en_function_pass2_informed_test50.csv"
```

## Targeted adjudication

```bash
python scripts/04d_run_sense_adjudication.py \
  --pass1 "$V2/en/sense_pass1/en_sense_pass1_test50.csv" \
  --pass2 "$V2/en/sense_pass2/en_sense_pass2_informed_test50.csv" \
  --inventory "$V2/en/sense_inventory/en_sense_inventory_v1.csv" \
  --only_problem_cases \
  --output "$V2/en/adjudication/en_sense_pass3_problem_cases.csv"

python scripts/05c_run_pass3.py \
  --pass1 "$DRIVE/en/stage05_llm_tagging/stage05_en_pass1_dispersed_test50.csv" \
  --pass2 "$V2/en/function_pass2/en_function_pass2_informed_test50.csv" \
  --taxonomy "$TAXONOMY" \
  --only_problem_cases \
  --output "$V2/en/adjudication/en_function_pass3_problem_cases.csv"
```

Pass 3 is API-backed and has no `--dry_run` option.

## Combined review dataset

```bash
python scripts/06_make_final_dataset.py \
  --samples "$V2/en/inputs/en_test50_target_occurrences.csv" \
  --sense_pass1 "$V2/en/sense_pass1/en_sense_pass1_test50.csv" \
  --sense_pass2 "$V2/en/sense_pass2/en_sense_pass2_informed_test50.csv" \
  --sense_pass3 "$V2/en/adjudication/en_sense_pass3_problem_cases.csv" \
  --function_pass1 "$DRIVE/en/stage05_llm_tagging/stage05_en_pass1_dispersed_test50.csv" \
  --function_pass2 "$V2/en/function_pass2/en_function_pass2_informed_test50.csv" \
  --function_pass3 "$V2/en/adjudication/en_function_pass3_problem_cases.csv" \
  --output "$V2/en/combined_review/en_combined_sense_function_test50.csv"
```

Omit either Pass 3 argument when no adjudication file has yet been created.

## Legacy files that must remain untouched

These remain useful evidence of the earlier function-only experiment but are not inputs to the current combined builder:

```text
<lang>/stage05_llm_tagging/stage05_<lang>_pass2_dispersed_test50.csv
<lang>/stage05_llm_tagging/stage05_<lang>_pass3_dispersed_test50.csv
<lang>/stage06_final_dataset/stage06_<lang>_final_dispersed_test50.csv
```

Repeat the v2 commands for `fr`, `es`, `de`, and `cs`. The notebook automates those loops and is safer than editing the commands manually.
