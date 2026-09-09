# Data contract v0.2 — occurrence, sense and review identity

Status: pilot working contract. This is a methodological/technical contract, not validated CEFR data.

## Why this revision exists

The previous pipeline retained token positions upstream but collapsed the lemma–sentence index to one lemma/POS row per sentence and generated sampled `row_id` values from output order. It also used ASCII-folded sense identifiers and allowed review outputs to drop or overwrite some upstream review metadata.

Version 0.2 corrects those issues before further annotation scaling.

## 1. Corpus observation identity

One sampled row represents **one exact target occurrence**.

Required identity fields:

- `observation_id` — collision-resistant stable identifier derived from language, `sentence_uid`, target character span, lemma and POS;
- `row_id` — compatibility alias; must equal `observation_id` in newly generated data;
- `sentence_uid` — stable prepared-corpus sentence identity;
- `target_token_index` — tokenizer position;
- `target_char_start` / `target_char_end` — exact character span in the stored sentence;
- `target_token` — surface realization at that span;
- `tokenizer_model` / `tokenizer_model_version` — processing provenance.

Repeated occurrences of the same lemma/POS in one sentence must remain separate observations.

A validation failure occurs if `sentence[target_char_start:target_char_end] != target_token`.

## 2. Language-specific lexical inventory identity

Human-readable labels and identifiers are separate.

- Unicode is NFC-normalised and retained.
- Identifiers must not depend on ASCII transliteration.
- `inventory_id` is collision-resistant and includes the explicit `inventory_version` in its identity.
- `sense_id` is scoped to one inventory version.
- `sense_role` distinguishes ordinary senses from `OTHER` and `UNCLEAR`.

If expert review changes sense boundaries by split or merge, create a new `inventory_version`. Do not silently reuse an existing sense ID for a different meaning.

Use `templates/sense_inventory_lineage_schema.csv` to record relationships between old and new inventory versions when revision begins.

## 3. Cross-language concept identity

Concept IDs are a later alignment layer. They must not replace language-specific sense IDs.

The intended relation is:

`corpus observation -> language-specific sense -> cross-language concept alignment`

A concept may align with zero, one or multiple lexical realizations in a language. Partial equivalence and lexical gaps must remain representable.

No universal CEFR level belongs to the concept by default. Later CEFR assessments should attach to a language-specific lexical realization/sense, assessment mode (receptive/productive), scope and evidence.

## 4. Communicative-function identity

Sentence function is an annotation of the utterance/context, not a permanent lexical property.

Function IDs come from the versioned controlled taxonomy. Taxonomy hierarchy labels are deterministic metadata derived by code from `function_id`; models should not generate or rewrite those labels.

Sense–function profiles may later be aggregated as corpus-dependent summaries, but the function of an individual usage instance must remain recoverable.

## 5. Review assertions

Each model pass is an assertion, not evidence of independent truth.

Pass 1 and Pass 2 retain separate:

- selected ID;
- confidence;
- rationale;
- explicit `requires_review` flag.

Pass 2 additionally retains:

- `validator_decision`;
- `interaction_note`;
- `review_mode`.

Pass 3 cannot erase an upstream explicit review flag. `human_review_recommended` is therefore the logical OR of relevant upstream flags plus any new adjudication concern.

Sense adjudication writes `final_sense_confidence`; function adjudication writes `final_function_confidence`.

Pipeline identifiers (`row_id`, Pass 1/2 IDs) and taxonomy labels are reattached deterministically after the model response rather than requested from the model.

## 6. Human decisions

Generated combined-review files are reproducible views and may be regenerated. Durable human decisions therefore live separately in a file based on `templates/expert_decisions_schema.csv`.

At minimum, reviewer records should preserve:

- `row_id`;
- reviewer identity;
- timestamp;
- reviewed input/version;
- expert sense decision/comment;
- expert function decision/comment;
- adjudication requirement.

The generated combined view may join these decisions, but must not be their only storage location.

## 7. Corpus metric provenance

The current `arf_per_million` is a pilot reduced-frequency proxy, not a standard ARF implementation and not CEFR evidence.

New statistic outputs therefore carry:

- `frequency_metric_id`;
- `frequency_metric_version`;
- `frequency_metric_formula`;
- `source_dispersion_unit`.

Do not compare historical and current fields merely because they share the name `arf_per_million`.

`source_dispersion` currently operates over the `source_id` values provided to corpus preparation. It should not be described as document dispersion unless those identifiers genuinely represent documents/sources at that granularity.

## 8. Migration rule

Legacy outputs are not silently rewritten. They remain historical pilot artifacts.

Fresh v0.2 runs should rerun Stage 02 onward so exact occurrence identity is available. Any adapter for older outputs must label the limitation explicitly; it must not invent precise token spans that were never retained.

## 9. Validation

`python scripts/00_validate_inputs.py` checks the new occurrence, inventory and review contracts. GitHub Actions additionally compiles all scripts and runs stable-ID regression tests.
