# ALTE Common Corpus SIG
## European CEFR Vocabulary Atlas pilot

A collaborative methodological pilot testing whether corpus evidence, lexical-sense annotation, sentence-level communicative-function tagging and expert judgement can be combined into a transparent multilingual CEFR vocabulary resource.

> **Pilot material — not validated CEFR data.** LLM-generated inventories and labels are provisional Tier 4 candidate material. Human review and empirical validation are required before any CEFR claim is made.

**Project website:** https://pertam.github.io/ALTE-Common-Corpus-SIG/

## Core analytical layers

The project deliberately separates three levels that must not be conflated:

1. **Corpus occurrence** — one precise target occurrence in one sentence.
2. **Language-specific lexical sense** — what that target means in that language and context.
3. **Cross-language concept alignment** — a later mapping between reviewed language-specific senses.

The English `concept_label_en` is a project-management label, not a source word to be translated.

Each sampled row also carries a separate **sentence-level communicative-function** annotation. Function belongs to the utterance/context, not permanently to the lexical concept.

| Sentence | Target lemma | Lexical sense | Sentence function |
|---|---|---|---|
| `Apply the cream twice daily.` | `apply` | put a substance onto a surface | giving an instruction |
| `The rule applies to all applicants.` | `apply` | be relevant or valid | stating a rule or condition |

## Six-stage workflow

1. **Corpus preparation** — document source, licence, language, date and register.
2. **Processing and lemma statistics** — tokenise, POS-tag, lemmatise and calculate versioned pilot corpus measures.
3. **Target-occurrence sampling** — sample lemmas while preserving exact occurrence identity and target spans.
4. **Lexical-sense tagging** — propose a coarse language-specific sense inventory, obtain human approval, produce an initial sense annotation and run an informed critical review.
5. **Communicative-function tagging** — produce an initial sentence-function annotation and run an informed critical review using the controlled CEFR-derived taxonomy.
6. **Combined QA and expert review** — adjudicate selected cases and assemble a generated review view while keeping durable human decisions separately.

Cross-language concept alignment and language-specific receptive/productive CEFR assessment are later pilot layers. They are not treated as already implemented merely because multilingual annotation exists.

## Stable occurrence identity

Stage 02 now preserves every eligible target occurrence rather than collapsing a lemma/POS to one row per sentence. Repeated occurrences of the same lemma in one sentence therefore remain distinguishable.

Each occurrence carries:

```text
observation_id
sentence_uid
target_token
target_token_index
target_char_start
target_char_end
```

`row_id` is retained for downstream compatibility and must equal `observation_id`. IDs are derived from stable corpus identity and character span rather than dataframe order or random sampling order.

The validator checks that the stored character span reproduces the recorded surface token.

## Pilot frequency measures

The current `arf_per_million` field is a transparent pilot reduced-frequency proxy, not a standard ARF implementation and not CEFR evidence. New outputs therefore also record:

```text
frequency_metric_id
frequency_metric_version
frequency_metric_formula
source_dispersion_unit
```

Artifacts should not be compared under the same metric name unless these definitions and versions match. `source_dispersion` currently means dispersion over the `source_id` values present in the prepared input; it must not be described as document dispersion unless `source_id` genuinely represents documents.

## Sense inventories and multilingual identifiers

Sense inventories are language-specific and created before cross-language alignment. IDs use collision-resistant hashes of NFC-normalised Unicode values; diacritics are never stripped to create identifiers.

Inventories have an explicit `inventory_version`. If expert review changes sense boundaries by splitting or merging senses, create a new inventory version rather than silently reusing old IDs. A lineage template is provided at `templates/sense_inventory_lineage_schema.csv`.

Every approved inventory includes special `OTHER` and `UNCLEAR` choices. Selecting either deterministically carries a human-review requirement forward.

## Annotation design

### Pass 1: independent candidate annotations

Sense Pass 1 and Function Pass 1 are separate decisions. IDs, source text and taxonomy labels are deterministic pipeline data and are reattached by code; the LLM is not asked to reproduce them.

### Pass 2: informed critical review

Production Pass 2 sees both Pass 1 proposals and rationales:

- Sense Pass 2 reviews the initial sense while also seeing the proposed sentence function.
- Function Pass 2 reviews the initial function while also seeing the proposed lexical sense.

The other annotation may provide context but must not determine the decision. Pass 2 records whether it accepts, changes or is uncertain about Pass 1, plus an interaction note and explicit review flag.

### Blind validation sample

Both Pass 2 scripts retain a `--blind` mode for sampled reliability experiments. Blind and informed outputs must be kept separately. Model agreement is not treated as validation evidence.

### Pass 3: targeted adjudication

Adjudication is intended for disagreement, low-confidence and explicitly flagged cases. Upstream review flags are preserved deterministically and cannot be erased by an adjudicator returning `false`.

Function adjudication writes `final_function_confidence`; sense adjudication writes `final_sense_confidence`. The model selects controlled IDs; pipeline code reattaches row IDs, labels and provenance.

## Pilot languages

English · French · Spanish · German · Czech

No English sense inventory is used as the source for other languages. Cross-language alignment remains an empirical pilot question.

For Czech, the pipeline no longer assumes a non-verified default spaCy package. Pass the exact working Czech pipeline with `--model` and record its name/version in the run manifest and output.

## Required sampled-occurrence columns

The current minimum contract is represented in `templates/stage3_sampled_sentences_schema.csv` and includes:

```text
row_id
observation_id
language_code
lemma
pos
target_token
target_token_index
target_char_start
target_char_end
sentence_uid
source_id
sentence
```

A sentence may appear multiple times, including repeated occurrences of the same lemma. Each precise occurrence must have its own stable `observation_id`.

## Sense tagging

Create a versioned provisional inventory:

```bash
python scripts/04a_create_sense_inventory.py \
  --samples data/en_sampled_occurrences.csv \
  --inventory_version v1 \
  --output data/en_sense_inventory.csv
```

A human language expert must review it and set retained rows to `inventory_status=approved`.

Run Sense Pass 1 after approval:

```bash
python scripts/04b_run_sense_pass1.py \
  --samples data/en_sampled_occurrences.csv \
  --inventory data/en_sense_inventory.csv \
  --output data/en_sense_pass1.csv
```

## Function Pass 1

```bash
python scripts/05a_run_pass1.py \
  --sentences data/en_sampled_occurrences.csv \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --output data/en_function_pass1.csv
```

The taxonomy loader includes available decision rules, exclusions, confusions and calibration examples rather than silently using only a short definition field.

## Informed Pass 2 reviews

```bash
python scripts/04c_run_sense_pass2.py \
  --samples data/en_sampled_occurrences.csv \
  --inventory data/en_sense_inventory.csv \
  --pass1 data/en_sense_pass1.csv \
  --function_pass1 data/en_function_pass1.csv \
  --output data/en_sense_pass2.csv

python scripts/05b_run_pass2.py \
  --sentences data/en_sampled_occurrences.csv \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --pass1 data/en_function_pass1.csv \
  --sense_pass1 data/en_sense_pass1.csv \
  --output data/en_function_pass2.csv
```

## Targeted adjudication

```bash
python scripts/04d_run_sense_adjudication.py \
  --pass1 data/en_sense_pass1.csv \
  --pass2 data/en_sense_pass2.csv \
  --inventory data/en_sense_inventory.csv \
  --only_problem_cases \
  --output data/en_sense_pass3.csv

python scripts/05c_run_pass3.py \
  --pass1 data/en_function_pass1.csv \
  --pass2 data/en_function_pass2.csv \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --only_problem_cases \
  --output data/en_function_pass3.csv
```

## Combined review dataset and durable human decisions

`06_make_final_dataset.py` creates a regenerated review view. Human decisions should be maintained separately using `templates/expert_decisions_schema.csv` and joined when the view is rebuilt.

```bash
python scripts/06_make_final_dataset.py \
  --samples data/en_sampled_occurrences.csv \
  --sense_pass1 data/en_sense_pass1.csv \
  --sense_pass2 data/en_sense_pass2.csv \
  --sense_pass3 data/en_sense_pass3.csv \
  --function_pass1 data/en_function_pass1.csv \
  --function_pass2 data/en_function_pass2.csv \
  --function_pass3 data/en_function_pass3.csv \
  --expert_decisions data/en_expert_decisions.csv \
  --output data/en_combined_review.csv
```

Generated LLM rows remain `cefr_source=llm_judgment`, `provenance_tier=4` and either `provisional` or `review_required`.

## Validation

Run schema/identity checks before annotation or merging:

```bash
python scripts/00_validate_inputs.py \
  --taxonomy taxonomy/cefr_function_taxonomy_v0_2.csv \
  --sample data/en_sampled_occurrences.csv \
  --sense_inventory data/en_sense_inventory.csv
```

Pull requests also run syntax compilation and stable-ID regression tests in GitHub Actions.

## Pilot gates before scaling

Before large annotation batches, adding languages, building a collaborative backend or publishing Atlas-level CEFR claims, the project should test three assumptions explicitly:

1. **Cross-language alignment challenge:** 10–20 difficult meaning clusters across all five languages, including polysemy, multiple lexicalisations, an MWE/construction, partial equivalence and a lexical gap.
2. **Annotation architecture comparison:** blind human judgements versus initial annotation, informed review, blind model annotation and targeted adjudication on a small varied sample.
3. **Function-value experiment:** compare expert receptive/productive CEFR judgements with and without corpus-derived function profiles to test whether function evidence actually improves defensibility, reproducibility or efficiency.

These are failure-finding feasibility experiments, not final validation studies.

## Sense-splitting rule

Create a separate sense only where the distinction could materially affect translation, grammatical construction, learner understanding, CEFR judgement or pedagogical treatment. Prefer a small number of defensible senses over dictionary micro-senses.

## Founding participants

The design remains open for collaborative development. Participants can contribute language expertise, sense-inventory review, taxonomy review, annotation, validation, cross-language alignment, corpus methodology or technical development.

## Licence

Code and notebooks are licensed under Apache 2.0. Corpus source material remains under its original licence and is not redistributed here.
