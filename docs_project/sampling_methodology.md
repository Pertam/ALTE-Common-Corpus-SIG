# Methodology summary: lemma and sentence sampling

## What we were trying to achieve

The aim was to create a manageable but methodologically useful Stage 5 sample for LLM-assisted sentence-level function tagging.

The sample needed to preserve enough corpus evidence to support later analysis:

- language
- lemma
- POS
- raw frequency
- frequency per million
- sentence count
- dispersion evidence
- ARF-style reduced frequency
- sentence ID
- sentence UID
- sentence text

## Options considered

### Option 1: Tag very large numbers of rows directly in ChatGPT

This was rejected because very large batches encourage truncation, shortcutting and inconsistent checking. It is also not reproducible enough for a SIG workflow.

### Option 2: Small number of examples per lemma

This was not enough to describe the functional environment of a lemma. A few sentences may show only one use and miss other communicative functions.

### Option 3: Systematic sample of lemmas with sentence evidence

This became the preferred approach. It gives a reproducible test set that can be processed through API scripts, checked and rerun.

## Final pilot decision

```text
Languages: English, French, Spanish, German, Czech
Eligible POS: NOUN, VERB, ADJ, ADV
Minimum ARF per million: 50
Random lemmas per language: 15
Sentence examples per lemma: 50
Random seed: 20260603
```

This produces up to:

```text
15 lemmas × 50 sentences = 750 rows per language
```

For the five-language pilot, the full design would therefore produce up to:

```text
5 languages × 750 rows = 3,750 sampled sentence rows
```

## Why ARF >= 50?

The ARF threshold was used as a practical filtering rule to avoid sampling very rare or highly bursty items. It was not used as a CEFR level assignment.

The project position is:

```text
ARF supports sampling and corpus description.
ARF does not determine CEFR level.
```

## Why content POS only?

The initial pilot focused on lexical content items:

```text
NOUN, VERB, ADJ, ADV
```

This avoided mixing the first pilot with function words, discourse markers and grammatical constructions, although those may be added later as separate entry types.

## Why 15 lemmas?

Fifteen lemmas per language was a feasibility sample. It was large enough to test the workflow across different lexical items but small enough to inspect manually and process through LLM passes.

## Why 50 sentences per lemma?

Fifty sentences per lemma was chosen to give enough sentence-level evidence to observe a distribution of communicative functions. This supports lemma-level functional environment profiles.

## Final conclusion

The final method was not to ask the LLM to assign CEFR vocabulary levels directly from a word list. Instead, the project created a corpus-driven sentence sample, preserved lemma frequency evidence, tagged the communicative function of each sentence, and then aggregated those tags into lemma-level functional profiles for expert review.

This makes the workflow more robust because it separates:

1. corpus evidence,
2. sentence-level function tagging,
3. lemma-level functional environment profiling,
4. later concept/sense-level CEFR judgement,
5. expert review and validation.
