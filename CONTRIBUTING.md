# Contributing to the ALTE Common Corpus SIG pilot

This is a collaborative methodological pilot. Contributions are welcome from language experts, corpus linguists, assessment specialists, CEFR researchers, NLP developers and review-methodology specialists.

## Ways to contribute

- develop and approve language-specific sense inventories;
- review the communicative-function taxonomy;
- annotate or adjudicate sentence rows;
- test inter-reviewer agreement;
- compare informed and blind review conditions;
- improve corpus processing or register coverage;
- develop cross-language concept alignment;
- improve scripts, documentation and QA;
- propose validation studies and report limitations.

Coding experience is not required for language or methodology review.

## Methodological commitments

1. One row represents one target lemma occurrence in one sentence.
2. Lexical sense belongs to the target occurrence.
3. Communicative function belongs to the whole sentence.
4. Pass 1 produces distinct sense and function proposals.
5. Production Pass 2 critically reviews both proposals with access to both labels and rationales.
6. The other annotation may be used as contextual evidence but must not determine the decision.
7. A separate blind-validation sample is retained to study reliability and anchoring.
8. Language-specific senses are not forced to copy English distinctions.
9. Model output remains provisional until human review.
10. Evidence and uncertainty must not be invented or hidden.

## Reviewing sense inventories

Use this operational rule:

> Split senses only where the distinction could materially affect translation, grammatical construction, learner understanding, CEFR judgement or pedagogical treatment.

Reviewers may merge, split, rename, add or remove provisional senses. Retain `OTHER` and `UNCLEAR`, then mark retained rows `inventory_status=approved`.

## Reviewing Pass 2 decisions

Check whether Pass 2 genuinely evaluated Pass 1 rather than merely repeating it. Review interaction notes carefully where the proposed function influenced the sense decision, or the proposed sense influenced the function decision.

## Proposing changes

Open an issue describing the problem, affected language or stage, proposed change, risks and supporting examples. Prompt changes must remain version-controlled because they affect reproducibility and interpretation.

Formal governance, attribution, authorship, data licensing and release conditions must be agreed before any validated public dataset is published.
