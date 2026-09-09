# Pilot validation gates before scaling

Status: proposed feasibility tests for expert review. These are not validated CEFR procedures.

The project should not scale annotation volume, add languages, build a full authenticated review platform or publish Atlas-level CEFR claims merely because the current scripts run. The following small experiments test assumptions the architecture depends on.

## Gate 1 — Cross-language concept alignment challenge

### Research question
Can independently reviewed language-specific senses be aligned to a concept layer without forcing English-centred equivalence?

### Minimum challenge set
Select approximately 10–20 difficult meaning clusters with candidates originating across English, French, Spanish, German and Czech.

Include deliberately:

- straightforward equivalence;
- polysemy;
- multiple lexicalisations of one concept;
- one-to-many mappings;
- partial equivalence;
- a lexical gap;
- an MWE or construction;
- morphology that makes apparently equivalent forms non-parallel.

### Record

- proposed concept membership;
- language-specific sense IDs;
- mapping relation and uncertainty;
- forced versus defensible mappings;
- reviewer disagreement;
- sense-boundary revisions triggered by alignment;
- reviewer time.

### Failure condition
If reviewers repeatedly need to distort language-specific senses to fit shared concepts, revise the concept/alignment model before scaling.

## Gate 2 — Annotation architecture comparison

### Research question
Do informed model review and targeted adjudication improve correctness enough to justify their cost and anchoring risk?

### Minimum sample
Approximately 30–50 varied target occurrences per language, with a difficult subset independently reviewed by two human experts.

Compare:

1. Pass 1 only;
2. informed Pass 2;
3. blind model Pass 2;
4. targeted Pass 3 adjudication.

Also compare sentence-only annotation against a condition with additional context where available.

### Measures

- agreement with blind expert judgement;
- unresolved ambiguity;
- review flags caught/missed;
- changes that improve versus degrade the decision;
- cost/time;
- model agreement reported separately from correctness.

### Failure condition
If informed review mainly increases agreement with Pass 1 without improving expert-aligned correctness, reduce or redesign the cross-conditioned review stage.

## Gate 3 — Target invariance of sentence function

### Research question
Does Function Pass 2 change its whole-sentence function judgement merely because a different sampled lexical target or sense proposal from the same sentence is shown?

### Design
For sentences containing multiple sampled targets, run Function Pass 2 with each target/sense proposal while holding the sentence constant.

### Failure condition
Material function-label changes caused only by target choice indicate that cross-conditioning is contaminating the sentence-level function decision.

## Gate 4 — Does function evidence help CEFR assessment?

### Research question
Do corpus-derived communicative-function profiles improve a defensible language-specific receptive/productive CEFR judgement?

### Minimum design
For a small set of reviewed language-specific senses, have experts make provisional CEFR judgements using an explicit rubric and traceable published evidence under two conditions:

- **A:** lexical/corpus evidence without the function profile;
- **B:** the same evidence plus the function profile.

Where feasible, add independent learner/task observations later.

### Measures

- inter-reviewer agreement;
- confidence;
- quality/traceability of rationale;
- reviewer time;
- whether receptive/productive distinctions become clearer;
- cases where function evidence changes the decision.

### Failure condition
If function profiles do not improve defensibility, reproducibility or efficiency, simplify this part of the architecture rather than scaling exhaustive function tagging.

## Gate 5 — Corpus metric sensitivity

### Research question
How strongly do corpus/source choices and the pilot reduced-frequency metric alter which items appear salient?

### Design
Repeat a small sample under controlled variations in corpus subset, source definition and sampling threshold while keeping the lexical targets traceable.

### Record

- corpus version;
- source definition;
- metric ID/version/formula;
- rank/sample changes;
- qualitative register/domain shifts.

### Failure condition
If minor corpus/metric changes produce large unexplained target-set changes, treat frequency as weaker supporting evidence and adjust sampling/reporting before scaling.

## Gate 6 — Reproducible end-to-end fixture

Publish one small redistributable five-language fixture with expected outputs and a run manifest recording:

- code commit;
- corpus/input version;
- tokenizer/model and version;
- taxonomy version;
- sampling parameters and seed;
- sense inventory version;
- actual LLM model for each pass;
- blind/informed mode;
- dry-run versus real run.

The fixture should contain edge cases for repeated target occurrences, Unicode distinctions, missing Pass-2 rows, sparse adjudication and inventory revision.

## Decision rule for scaling

These gates are intended to falsify assumptions, not to prove the final Atlas valid. Scaling should follow only after failures are understood and the data contract is stable enough that human decisions, provenance and cross-language divergence will survive later pipeline changes.
