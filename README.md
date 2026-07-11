# ALTE Common Corpus SIG
## European CEFR Vocabulary Atlas pilot

A collaborative methodological pilot testing whether corpus evidence, lexical-sense annotation, sentence-level communicative-function tagging and expert judgement can be combined into a transparent multilingual CEFR vocabulary resource.

> **Pilot material — not validated CEFR data.** LLM-generated inventories and labels are provisional Tier 4 candidate material. Human review and empirical validation are required before any CEFR claim is made.

**Project website:** https://pertam.github.io/ALTE-Common-Corpus-SIG/

## Core unit of analysis

Each dataset row represents **one target lemma occurrence in one corpus sentence**.

The row carries two distinct annotations:

- **lexical sense** — what the target lemma means in that sentence;
- **communicative function** — what the whole sentence is doing communicatively.

| Sentence | Target lemma | Lexical sense | Sentence function |
|---|---|---|---|
| `Apply the cream twice daily.` | `apply` | put a substance onto a surface | giving an instruction |
| `The rule applies to all applicants.` | `apply` | be relevant or valid | stating a rule or condition |

## Six-stage workflow

1. **Corpus preparation** — document source, licence, language, date and register.
2. **Processing and lemma statistics** — tokenise, POS-tag, lemmatise and calculate corpus evidence.
3. **Target-occurrence sampling** — sample lemmas and sentences while preserving stable row IDs.
4. **Lexical-sense tagging** — propose a coarse sense inventory, obtain human approval, produce an initial sense annotation and run an informed critical review.
5. **Communicative-function tagging** — produce an initial sentence-function annotation and run an informed critical review using the controlled CEFR-derived taxonomy.
6. **Combined QA and expert review** — adjudicate selected cases, merge sense and function outputs, review them separately, and aggregate by `language + lemma + sense`.

## Annotation design

### Pass 1: initial annotations

Sense Pass 1 and Function Pass 1 are produced as separate decisions. This keeps the basic distinction clear:

- sense belongs to the target lemma occurrence;
- function belongs to the whole sentence.

### Pass 2: informed critical review

Production Pass 2 sees both Pass 1 proposals and rationales:

- Sense Pass 2 reviews the initial sense while also seeing the proposed sentence function.
- Function Pass 2 reviews the initial function while also seeing the proposed lexical sense.

The second pass may use the other annotation as contextual evidence, but must not treat it as determinative. It records whether it accepts, changes or is uncertain about Pass 1, and explains whether sense–function interaction affected the decision. The final sense and function remain separately recorded judgements.

### Blind validation sample

The Pass 2 scripts retain a `--blind` mode for a smaller sampled reliability study. Blind results should be stored separately and compared with informed review and human decisions; they are not the default production workflow.

## Pilot languages

English · French · Spanish · German · Czech

Language-specific sense inventories are created independently. Cross-language concept alignment happens later; English labels are not treated as universal source words.

## Required sampled-sentence columns

```text
row_id
language
sentence_id
sentence
target_token
target_lemma
target_pos
```

A sentence may appear more than once when it contains more than one sampled target occurrence. Each occurrence must have its own stable `row_id`.

## Sense tagging

Create a provisional inventory:

```bash
python scripts/04a_create_sense_inventory.py \
  --samples data/en_sampled_occurrences.csv \
  --output data/en_sense_inventory.csv
```

A human language expert must review it and set retained rows to `inventory_status=approved`.

Run Sense Pass 1 after the inventory is approved:

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

## Optional blind validation sample

Run the same Pass 2 scripts with `--blind` on a separately sampled subset and a separate output path. Do not mix blind and informed rows in the same output file.

```bash
python scripts/04c_run_sense_pass2.py \
  --samples data/en_blind_sample.csv \
  --inventory data/en_sense_inventory.csv \
  --blind \
  --output data/en_sense_pass2_blind.csv
```

## Combined review dataset

```bash
python scripts/06_make_final_dataset.py \
  --samples data/en_sampled_occurrences.csv \
  --sense_pass1 data/en_sense_pass1.csv \
  --sense_pass2 data/en_sense_pass2.csv \
  --sense_pass3 data/en_sense_pass3.csv \
  --function_pass1 data/en_function_pass1.csv \
  --function_pass2 data/en_function_pass2.csv \
  --function_pass3 data/en_function_pass3.csv \
  --output data/en_combined_review.csv
```

## Sense-splitting rule

Create a separate sense only where the distinction could materially affect translation, grammatical construction, learner understanding, CEFR judgement or pedagogical treatment. Prefer a small number of defensible senses over dictionary micro-senses. Every approved inventory includes `OTHER` and `UNCLEAR`.

## Founding participants

The design remains open for collaborative development. Participants can contribute language expertise, sense-inventory review, taxonomy review, annotation, validation, cross-language alignment, corpus methodology or technical development.

## Licence

Code and notebooks are licensed under Apache 2.0. Corpus source material remains under its original licence and is not redistributed here.
