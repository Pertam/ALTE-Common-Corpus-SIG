# Contributing to the ALTE Common Corpus SIG pilot

This is a collaborative methodological pilot. Contributions are welcome from language experts, corpus linguists, assessment specialists, CEFR researchers, NLP developers and review-methodology specialists.

## Ways to contribute

- develop and approve language-specific sense inventories;
- review the communicative-function taxonomy;
- annotate or adjudicate sentence rows;
- test inter-reviewer agreement;
- improve corpus processing or register coverage;
- develop cross-language concept alignment;
- improve scripts, documentation and QA;
- propose validation studies and report limitations.

Coding experience is not required for language or methodology review.

## Methodological commitments

1. One row represents one target lemma occurrence in one sentence.
2. Lexical sense belongs to the target occurrence.
3. Communicative function belongs to the whole sentence.
4. Sense and function are annotated independently.
5. Language-specific senses are not forced to copy English distinctions.
6. Model output remains provisional until human review.
7. Evidence and uncertainty must not be invented or hidden.

## Reviewing sense inventories

Use this operational rule:

> Split senses only where the distinction could materially affect translation, grammatical construction, learner understanding, CEFR judgement or pedagogical treatment.

Reviewers may merge, split, rename, add or remove provisional senses. Retain `OTHER` and `UNCLEAR`, then mark retained rows `inventory_status=approved`.

## Proposing changes

Open an issue describing the problem, affected language or stage, proposed change, risks and supporting examples. Prompt changes must remain version-controlled because they affect reproducibility and interpretation.

Formal governance, attribution, authorship, data licensing and release conditions must be agreed before any validated public dataset is published.
