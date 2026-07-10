# Independent audit of the ALTE Common Corpus SIG European CEFR Vocabulary Atlas pilot

## 1. Audit basis

### 1.1 Review scope and runtime

| Item | Audit record |
|---|---|
| **Review date** | **24 June 2026** |
| **Website** | `https://pertam.github.io/ALTE-Common-Corpus-SIG/` |
| **Repository** | `https://github.com/Pertam/ALTE-Common-Corpus-SIG` |
| **Repository branch inspected** | `main` |
| **Commit SHA** | **Not reliably retrievable in this runtime.** The GitHub history request returned HTTP 429, and the web interface did not expose the current full SHA. This report therefore refers to the public state of `main` retrieved on the review date, not to a cryptographically fixed revision. |
| **Repository status** | Not checked. No shell was available, so `git status`, working-tree state and untracked files could not be inspected. |
| **Audit type** | Public-web static audit of the rendered site and publicly accessible repository files. It is **not** an execution audit. |

The repository page identified `main` as the active branch and showed 62 commits, but its latest-commit field did not expose a full SHA in the retrieved page. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG))

### 1.2 Rendered website pages inspected

The following rendered pages were opened and inspected:

1. `https://pertam.github.io/ALTE-Common-Corpus-SIG/`
2. `https://pertam.github.io/ALTE-Common-Corpus-SIG/rationale-and-use-cases.html`
3. `https://pertam.github.io/ALTE-Common-Corpus-SIG/workflow.html`
4. `https://pertam.github.io/ALTE-Common-Corpus-SIG/technical-setup.html`
5. `https://pertam.github.io/ALTE-Common-Corpus-SIG/reviewer-area.html`
6. `https://pertam.github.io/ALTE-Common-Corpus-SIG/methodology.html`
7. `https://pertam.github.io/ALTE-Common-Corpus-SIG/faq.html`
8. `https://pertam.github.io/ALTE-Common-Corpus-SIG/further-reading.html`
9. `https://pertam.github.io/ALTE-Common-Corpus-SIG/stage1-corpus-preparation.html`
10. `https://pertam.github.io/ALTE-Common-Corpus-SIG/stage2-processing.html`
11. `https://pertam.github.io/ALTE-Common-Corpus-SIG/stage3-sampling.html`
12. `https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html`
13. `https://pertam.github.io/ALTE-Common-Corpus-SIG/stage5-qa-review.html`

The repository also contains `docs/links.html`, but it is not included in the main navigation. Its repository source was opened; it was not separately inspected as a rendered public page.

All internal navigation and stage links listed above resolved. The public Colab URL resolved to the project notebook. The Google Drive link could not be substantively inspected, so its permissions, folder contents and access route remain unverified. The site itself describes GitHub as the code/documentation store, Drive as the working-data store and Colab as the execution environment. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html))

### 1.3 Web-visible repository manifest

The following structure was observed through GitHub. Because no shell or recursive tree API was available, this is a **web-visible manifest**, not a filesystem-verified clone manifest.

```text
/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── config/
│   ├── archive/
│   ├── .gitkeep
│   ├── languages.yaml
│   ├── pipeline_config.yaml
│   └── project_config.yaml
├── docs/
│   ├── api_guidance/
│   ├── reviewer_guidance/
│   ├── setup/
│   ├── .gitkeep
│   ├── .nojekyll
│   ├── faq.html
│   ├── further-reading.html
│   ├── index.html
│   ├── links.html
│   ├── methodology.html
│   ├── rationale-and-use-cases.html
│   ├── reviewer-area.html
│   ├── stage1-corpus-preparation.html
│   ├── stage2-processing.html
│   ├── stage3-sampling.html
│   ├── stage4-function-tagging.html
│   ├── stage5-qa-review.html
│   ├── style.css
│   ├── technical-setup.html
│   └── workflow.html
├── docs_project/
│   ├── pipeline_run_guide.md
│   └── sampling_methodology.md
├── examples/
│   └── stage5_sample_sentences_en_demo.csv
├── methodology/
│   ├── archive/
│   └── .gitkeep
├── notebooks/
│   └── 00_main_project_runner_colab.ipynb
├── sample_data/
│   ├── demo_outputs/
│   └── stage5/
├── scripts/
│   ├── .gitkeep
│   ├── 00_validate_inputs.py
│   ├── 01_prepare_leipzig_sentences.py
│   ├── 02_tokenise_lemmatise.py
│   ├── 03_compute_lemma_stats.py
│   ├── 04_sample_lemmas_and_sentences.py
│   ├── 05a_run_pass1.py
│   ├── 05b_run_pass2.py
│   ├── 05c_run_pass3.py
│   ├── 06_make_final_dataset.py
│   └── llm_function_tagging_utils.py
├── taxonomy/
│   ├── archive/
│   └── cefr_function_taxonomy_v0_2.csv
└── templates/
    ├── colab_run_commands.md
    ├── drive_folder_structure.md
    ├── lemma_sentence_index_schema.csv
    ├── lemma_stats_schema.csv
    ├── raw_leipzig_sentence_format.txt
    ├── review_workbook_columns.csv
    ├── stage1_sentences_schema.csv
    ├── stage3_sampled_sentences_schema.csv
    └── tokens_schema.csv
```

The top-level and folder manifests are supported by the repository directory pages. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG))

### 1.4 Technical checks completed

The following checks were actually completed:

- opened the rendered project website;
- followed every visible internal navigation link;
- followed all five workflow-stage links;
- opened the public repository and all relevant top-level folders;
- opened the main pipeline scripts and statically inspected their implementation;
- inspected declared input/output fields and structured-output schemas;
- compared actual script filenames with the README and website;
- inspected configuration-file pages, templates, taxonomy page, example page and notebook page;
- inspected `.env.example` and `.gitignore`;
- inspected the README and dependency-file pages;
- checked that the Colab link resolves;
- attempted to open the Drive link;
- attempted to retrieve repository history and a full commit SHA;
- performed static checks for resumability, duplicate handling, prompt design, model selection, provenance, configuration use and merge logic;
- made no paid API calls.

### 1.5 Checks not completed

The following could not be completed because the runtime supplied no shell and no hosted container network:

- cloning the repository;
- `git status`;
- recording a shell-generated recursive manifest;
- Python syntax compilation;
- dependency installation;
- imports;
- `--help` command execution;
- notebook execution;
- sample-data processing;
- schema validation by execution;
- mocked OpenAI calls;
- unit tests or static linters;
- link checking with a crawler;
- mobile/browser accessibility testing;
- local inspection of notebook cells if GitHub failed to render them;
- verification of exact dependency resolution;
- verification of spaCy model installation;
- verification of Drive folder permissions or contents;
- verification of restricted corpora, logs, review workbooks or full outputs.

No claim in this report depends on those checks having been completed.

### 1.6 Inaccessible or permission-controlled resources

| Resource | Access result | Audit consequence |
|---|---|---|
| Google Drive working area | Not inspectable | Corpus files, metadata, licences, full outputs, logs and review workbooks could not be verified. |
| Restricted corpus data | Correctly not exposed publicly | Corpus composition, size, dates, duplication, privacy and licence compliance remain unverified. |
| Actual API account and model calls | Not accessed | Runtime output validity, cost and rate-limit behaviour remain untested. |
| NotebookLM material | No accessible project route was identified | Its stated role cannot be assessed. |
| Full Colab execution | Link resolved, execution not attempted | Notebook reproducibility is unverified. |
| Commit SHA | History endpoint rate-limited | Findings are tied to the observed `main` branch state, not a fixed commit. |

---

# 2. Executive verdict

## 2.1 Does the project make sense as one coherent process?

**Partly.**

The repository contains a recognisable technical sequence:

1. prepare Leipzig-style sentence files;
2. tokenise, POS-tag and lemmatise;
3. compute lemma statistics;
4. sample lemmas and sentences;
5. run three LLM passes;
6. merge outputs.

That sequence is coherent as an **early sentence-level function-tagging prototype**. The script numbering makes its execution order relatively easy to infer. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/tree/main/scripts))

It is **not yet one coherent end-to-end Vocabulary Atlas system**. The website describes concept and sense modelling, receptive/productive CEFR judgements, translation-equivalent alignment, cross-language comparison, expert adjudication and validation. The public implementation ends at a provisional merged sentence-function dataset. No public implementation was found for concept inventories, sense alignment, CEFR-level assignment, reviewer-workbook production, human-decision ingestion, human adjudication, agreement measurement, cross-language validation or publication approval.

## 2.2 Is the methodology defensible as a pilot?

**Defensible only as a narrowly framed feasibility pilot, not yet as a basis for CEFR claims.**

Positive methodological principles include:

- separating concepts and senses;
- distinguishing receptive and productive knowledge;
- treating cross-language divergence as data;
- warning that frequency does not determine CEFR level;
- treating LLM output as provisional;
- asking reviewers to judge the whole sentence.

However:

- the implemented “ARF-style” statistic is explicitly described in the code as a pilot measure, not established ARF;
- the corpus sampling frame is not publicly documented;
- 15 randomly chosen high-frequency/high-dispersion lemmas per language cannot support representative language-level conclusions;
- Pass 2 is not blind in the normal methodological sense;
- Pass 3 is automated resolution, not expert adjudication;
- confidence is uncalibrated model self-report;
- the single-sentence, single-label design may force classifications unsupported by context;
- the connection between sentence functions and concept-level CEFR judgements remains proposed rather than validated.

The statistics script itself cautions that its ARF-style value is a transparent pilot measure rather than validated external corpus evidence. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/03_compute_lemma_stats.py))

## 2.3 Does the technical process appear reproducible?

**Not currently.**

The public code has useful reproducibility intentions—numbered stages, explicit schemas, stable identifiers, random-state support and append/resume behaviour—but current public instructions do not match the repository:

- README commands name `run_pass1.py`, `run_pass2.py`, `run_pass3.py` and `make_final_dataset.py`;
- the repository contains `05a_run_pass1.py`, `05b_run_pass2.py`, `05c_run_pass3.py` and `06_make_final_dataset.py`;
- the README uses input files such as `taxonomy/taxonomy_en.csv` and `sample_data/sentences_en.csv`, which are not present in the public manifest;
- the README’s final merge omits the actual script’s recommended `--samples` argument, risking loss of upstream lemma and provenance fields;
- output records do not visibly preserve the repository SHA, prompt version, taxonomy hash, configuration hash, package versions, spaCy model version or API model snapshot.

The mismatch is directly visible between the README quickstart and the script directory. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG))

## 2.4 Does the website work as a one-stop shop?

**No.**

It works as an accessible **project rationale and methodological overview**, but not as an operational one-stop shop.

A visitor cannot reliably determine:

- the exact current stage;
- what has actually been run;
- how many rows or languages have completed each stage;
- which public outputs exist;
- how to request Drive access;
- which account to use;
- where the correct review workbook is;
- how to make and submit a review copy;
- the expected reviewer workload;
- who owns each stage;
- the distinction between implemented, planned and aspirational components;
- the authoritative filenames and commands;
- what happens after expert review;
- what “Tier 4” means.

The homepage gives a broad overview and infrastructure links, but its “current project focus” is not a status report. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html))

## 2.5 Is it ready to present to the SIG?

**Not in its current form as an operational project site.**

It can be presented after a short, focused correction phase **as an early pilot design and prototype**, provided the presentation explicitly distinguishes:

- implemented components;
- currently available public material;
- restricted resources;
- untested components;
- proposed future workflow;
- provisional model output;
- human-reviewed material;
- validated evidence.

The most urgent credibility problem is that a technically confident SIG member could copy the published commands and immediately encounter missing filenames. A non-technical member would encounter a different problem: they would understand the rationale but not know what to do next.

---

# 3. What is already working well

## 3.1 The provisional-output warning is prominent

The homepage, README, workflow and function-tagging page repeatedly state that LLM outputs are provisional and not validated CEFR data. This is one of the strongest aspects of the public presentation and should be preserved. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html))

## 3.2 The high-level rationale is clear

`docs/rationale-and-use-cases.html` explains why flat headword lists are inadequate and gives understandable examples of polysemy, translation mismatch, productive/receptive differences and function. That material is suitable for a mixed technical and assessment audience. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/rationale-and-use-cases.html))

## 3.3 The concept/sense principle is methodologically appropriate

The methodology page correctly states that English labels should be project labels rather than source words to be translated directly. It also recognises lexical concepts, multiword expressions and constructions. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/methodology.html))

## 3.4 Cross-language divergence is not treated as an error

The public methodology explicitly allows equivalent concepts to differ across languages because of morphology, register, constructional realisation, transparency and polysemy. This is an important principle for the Atlas and should remain central. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/methodology.html))

## 3.5 The reviewer material discourages rubber-stamping

The reviewer page tells experts to review the communicative function of the whole sentence, permits accept/change/uncertain/reject decisions and gives examples of useful comments. This is a sound basis for a fuller reviewer handbook. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/reviewer-area.html))

## 3.6 The pipeline order is visible in filenames

The numbered scripts make the intended sequence substantially clearer than the README’s older names:

- `00_validate_inputs.py`;
- `01_prepare_leipzig_sentences.py`;
- `02_tokenise_lemmatise.py`;
- `03_compute_lemma_stats.py`;
- `04_sample_lemmas_and_sentences.py`;
- `05a`–`05c`;
- `06_make_final_dataset.py`.

([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/tree/main/scripts))

## 3.7 Stable sentence identifiers and duplicate filtering are attempted

`01_prepare_leipzig_sentences.py` constructs a hash-based `sentence_uid`, normalises whitespace and removes exact repeated sentences within the processed input. This is a useful foundation for traceability, although duplicate removal needs an audit log. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/01_prepare_leipzig_sentences.py))

## 3.8 Input validation exists

`00_validate_inputs.py` checks required columns, duplicate `row_id` values, blank sentences and duplicate taxonomy IDs. This is useful defensive programming and should be expanded rather than replaced. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/00_validate_inputs.py))

## 3.9 Resumability is considered

The LLM passes use append-oriented output and completed-`row_id` detection, reducing the risk of losing a long run after interruption. The design is sensible for API processing, although it needs atomicity and run-level provenance.

## 3.10 The repository does not publicly redistribute full corpora

The README states that large corpora and full outputs are kept outside GitHub and that corpus material remains subject to original licences. This is appropriately cautious. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG))

---

# 4. Critical issues before the SIG presentation

| Severity | Category | Evidence | Consequence | Exact correction | Affected location |
|---|---|---|---|---|---|
| **Critical** | Technical documentation | README uses nonexistent script and input filenames; actual files are numbered `05a`–`06`. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | A contributor cannot execute the published quickstart. | Replace every command with an exact command tested against the current tree. Supply a small, public, no-API dry-run fixture. | `README.md`; `docs/stage4-function-tagging.html`; `docs/technical-setup.html` |
| **Critical** | Scope/evidence | Public narrative describes concept, sense, CEFR, cross-language alignment, review and validation, while public code ends at provisional sentence tagging. | SIG members may mistake planned work for implemented infrastructure. | Add an “Implemented now / planned next / not yet started” table on the homepage and workflow page. | Homepage; workflow; methodology; reviewer area |
| **High** | Methodology | Pass 2 sees Pass 1’s function and rationale, so it is not blind independent coding. The site nevertheless calls it “blind validation.” ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/workflow.html)) | Inflated perception of independence; confirmation bias. | Either remove Pass 1 information from Pass 2 and compare afterwards, or rename it “informed validator pass.” | `05b_run_pass2.py`; workflow; FAQ; Stage 4; README |
| **High** | Methodology | Pass 3 is automated model processing but is called “adjudication” and “final moderated decision.” ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html)) | Automated resolution may be confused with human adjudication. | Rename it “automated resolution pass”; reserve “adjudication” for a documented human procedure. | `05c_run_pass3.py`; website; output field names |
| **Critical** | Corpus statistics | Code calls the measure “pilot ARF-style”; the site presents it as ARF without defining the formula. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/03_compute_lemma_stats.py)) | The threshold may be interpreted as a standard ARF threshold when it is not. | Implement a documented standard ARF calculation or rename the field and threshold everywhere to “pilot dispersion-adjusted frequency.” | `03_compute_lemma_stats.py`; config; Stage 2; Stage 3; sampling guide |
| **High** | Reproducibility | Outputs do not visibly record commit SHA, prompt/taxonomy/config hashes, package versions or model snapshot. | Runs cannot be reconstructed after code, taxonomy or model changes. | Add a `run_id` and immutable run manifest; copy its identifiers into every output row. | All scripts; configuration; output schemas |
| **High** | Data access | Drive is described as the working-data location but no permission route, owner, account type or folder guide is publicly explained. | Reviewers and researchers cannot start without a private email or meeting. | Publish a Data and Access page with public/restricted matrix and access-request instructions. | Homepage; new Data and Access page |
| **High** | Reviewer operations | Reviewer page explains judgement principles but not workload, file acquisition, editable fields, saving, submission, adjudication or acknowledgement. | A reviewer cannot complete the task independently. | Publish an operational reviewer start page and fixed workbook data dictionary. | Reviewer area; `templates/review_workbook_columns.csv` |
| **High** | Governance | No public corpus register gives source package, year, version, genre, licence, restrictions or responsibility by language. | Comparability, lawful reuse and publication readiness cannot be assessed. | Add a public corpus-provenance and licence register, even if files remain restricted. | New governance/data page; Stage 1 |
| **High** | Website/code consistency | Stage 4 claims its prompt text is auto-generated from scripts named `run_pass*.py`, which do not exist in the current repository. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html)) | A prominently labelled “exact” record is demonstrably stale. | Generate the page during site build from the actual numbered prompt files and display the source commit SHA. | `docs/stage4-function-tagging.html` |
| **High** | Setup/security | The README instructs users to create `.env`; static inspection found no visible `load_dotenv()` use in the tagging scripts or utility module. | A correct `.env` may not be read during local execution. | Call `load_dotenv()` centrally, document environment precedence and add a no-call key-detection check. | `llm_function_tagging_utils.py`; README |
| **Medium** | Presentation credibility | Website says “Last updated 09 June 2026” but does not display the source commit or build date. | Members cannot tell which repository revision the pages describe. | Add “Built from commit … on …” to every page footer. | All website pages |

---

# 5. Complete findings register

“Confirmed” means supported directly by an inspected public page or file. “Probable” identifies a risk suggested by static inspection but not executable testing.

| ID | Severity | Category | Exact location | Finding | Evidence | Impact | Recommended action | Effort | Timing |
|---|---|---|---|---|---|---|---|---|---|
| F01 | Critical | Technical documentation | `README.md`, Quickstart | **Confirmed error:** published script names do not match repository files. | README lines 306–328 versus `scripts/` manifest. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | Quickstart fails. | Replace and test every command. | Small | Before presentation |
| F02 | Critical | Technical documentation | `README.md`, inputs | **Confirmed error:** `taxonomy/taxonomy_en.csv` and `sample_data/sentences_en.csv` are not in the public manifest. | README lines 300–316; taxonomy contains `cefr_function_taxonomy_v0_2.csv`. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | New users cannot reproduce the example. | Add real fixtures or use actual paths. | Small | Before presentation |
| F03 | High | Traceability | README final command; `06_make_final_dataset.py` | README omits the final script’s recommended `--samples` input. | Actual parser exposes `--samples`; README merge command does not. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/06_make_final_dataset.py)) | Final output may lose lemma, sentence UID and upstream provenance. | Make `--samples` required unless a deliberate reduced export is requested. | Small | Before next run |
| F04 | High | Website consistency | Stage 4, “Scripts used” | **Confirmed error:** website lists obsolete filenames. | Stage 4 lines 12–16; repository manifest. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html)) | Site is not authoritative. | Update from generated manifest. | Small | Before presentation |
| F05 | High | Prompt provenance | Stage 4, “exact prompt instructions” | **Confirmed inconsistency:** page claims exact auto-generation from nonexistent script paths. | Stage 4 lines 62–65. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html)) | Prompt record cannot be trusted. | Generate from actual versioned prompt sources and show hash/SHA. | Medium | Before presentation |
| F06 | High | Configuration | `config/pipeline_config.yaml`; scripts | Configuration appears documentary rather than an enforced runtime source of truth. The scripts use CLI arguments and utility defaults. | Script imports and parsers; no common config loader is visible in the inspected implementations. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/01_prepare_leipzig_sentences.py)) | Website/config values can drift from actual runs. | Add one configuration loader used by every stage. | Medium | Before next run |
| F07 | High | Environment setup | `.env.example`; `llm_function_tagging_utils.py` | Static inspection found no visible `.env` loader despite README instructions. | Utility imports show `os` and API helpers but no visible dotenv loading. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/llm_function_tagging_utils.py)) | Local API setup may fail. | Add `load_dotenv()` and a safe setup diagnostic. | Small | Before presentation |
| F08 | High | Dependency reproducibility | `requirements.txt`; README | No lockfile or fully reproducible environment specification is visible; spaCy model packages are external to the requirement install. | The tokenisation script requires separately downloaded language models. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/02_tokenise_lemmatise.py)) | Different environments can produce different lemmas/POS tags. | Pin Python, packages and exact model wheels/checksums. | Medium | Before next run |
| F09 | Medium | README accuracy | README Requirements | README names only four package categories although pipeline scripts also import `numpy`, `spaCy`, `tqdm` and require Parquet support. | Code imports. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/02_tokenise_lemmatise.py)) | Setup expectations are incomplete. | Derive requirements documentation from the actual environment file. | Small | Before presentation |
| F10 | High | Corpus ingestion | `01_prepare_leipzig_sentences.py`; Stage 1 | Website describes raw corpus preparation; implementation expects one sentence per line or Leipzig sentence format. | Script input contract. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/01_prepare_leipzig_sentences.py)) | General raw documents cannot be processed as described. | State the actual input boundary or implement document-level extraction and sentence segmentation. | Medium | Before next run |
| F11 | High | Provenance | Stage 1 versus `01_prepare_leipzig_sentences.py` | Metadata, register, date and licensing are described, but the script output contains only language, sentence ID/UID, sentence and source ID. | Stage 1 inputs versus script output contract. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage1-corpus-preparation.html)) | Provenance is not propagated into later rows. | Add corpus/document manifest IDs and join them through every stage. | Medium | Before next run |
| F12 | Medium | Duplicate handling | `prepare_sentences()` | Exact normalised duplicate sentences are silently dropped. | `seen_sentences` implementation. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/01_prepare_leipzig_sentences.py)) | Potential data loss cannot be audited. | Write a duplicate report with retained and dropped IDs. | Small | Before next run |
| F13 | High | Corpus design | Public site | No corpus package names, years, versions, token counts, genres or language-specific sampling frames are public. | Stage 1 provides only generic paths and example metadata. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage1-corpus-preparation.html)) | Cross-language comparability cannot be assessed. | Publish a corpus register. | Medium | Before presentation |
| F14 | Critical | Measure validity | `03_compute_lemma_stats.py` | Implementation labels the statistic “pilot ARF-style”; site calls it ARF. | Script methodological note. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/03_compute_lemma_stats.py)) | Threshold has an unclear empirical meaning. | Use standard ARF or rename and validate the custom measure. | Medium | Before next run |
| F15 | High | Dispersion | Stage 2; statistics pipeline | Document/source segmentation supporting dispersion is insufficiently defined publicly. | Stage 2 names dispersion but gives no formula or partition unit. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage2-processing.html)) | Values may not be comparable between corpora. | Specify exact units, partitions and formulas. | Medium | Before next run |
| F16 | High | Sampling | Stage 3; `04_sample_lemmas_and_sentences.py` | The pilot uses 15 random eligible lemmas per language above a threshold. | Stage 3 lines 12–17; script docstring. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage3-sampling.html)) | Suitable for debugging, not representative inference. | Label it as engineering sampling and design a stratified research sample. | Medium | Before further data generation |
| F17 | Medium | Sampling | Stage 3 | “All sentences” can generate radically different workloads per lemma; an optional cap is not methodologically justified. | Stage 3 and script docstring. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage3-sampling.html)) | Frequent lemmas dominate costs and review volume. | Define a stratified per-lemma sentence policy and justification. | Medium | Before next run |
| F18 | Medium | Duplicate API work | Stage 4 input model | A sentence containing several selected lemmas may be classified more than once. | Sampling is lemma-sentence based; row IDs are added after sampling. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/04_sample_lemmas_and_sentences.py)) | Unnecessary cost and correlated duplicate rows. | Classify unique sentence UIDs once and link results to lemma records. | Medium | Before next run |
| F19 | High | Unit of analysis | Website versus public schemas | Website centres concepts/senses, but public processing is lemma+POS and sentence based. | Methodology versus script/template manifest. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/methodology.html)) | Sense-level claims are unsupported by the implemented data model. | Add explicit concept, sense and language-realisation schemas. | Large | Before publication |
| F20 | High | Pass independence | `05b_run_pass2.py`; workflow | Pass 2 sees Pass 1 output and is therefore not blind independent annotation. | Workflow lists Pass 1 ID, label and rationale as inputs; code calls it validation. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/workflow.html)) | Correlated errors and confirmation bias. | Redesign as independent coding or rename accurately. | Medium | Before next run |
| F21 | High | Adjudication terminology | `05c_run_pass3.py` | Model-based Pass 3 is called adjudication. | Prompt and website description. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/stage4-function-tagging.html)) | Human governance is obscured. | Call it automated resolution; add human adjudication later. | Small | Before presentation |
| F22 | High | Classification schema | `05a`–`05c` | Schemas require a single primary function ID; no explicit public evidence of `no applicable function`, insufficient context or proper multilabel output was found. | Pass schemas expose one function ID plus limited alternative fields. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/05a_run_pass1.py)) | Forced or overinterpreted classification. | Add abstention, insufficient-context and optional secondary-function fields. | Medium | Before next run |
| F23 | High | Context | Pass prompts | One isolated sentence is treated as sufficient input. | Workflow states each pass receives one sentence. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/workflow.html)) | Discourse functions, reference and irony may be unrecoverable. | Add context availability and evidence-sufficiency rules. | Medium | Before next run |
| F24 | High | Confidence | Methodology versus scripts | Website methodology uses numeric confidence bands; schemas use `high/medium/low`. | Methodology lines 81–87 and pass schemas. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/methodology.html)) | Meaning is inconsistent and uncalibrated. | Choose one representation; describe it as uncalibrated model self-report until validated. | Small | Before presentation |
| F25 | High | Run provenance | LLM outputs | No row fields visibly record model snapshot, prompt version, taxonomy version, commit, timestamp, seed, token usage or cost. | Pass field lists. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/05a_run_pass1.py)) | Results cannot be reconstructed or cost-audited. | Add run manifest and provenance columns. | Medium | Before next run |
| F26 | Medium | Resumability | CSV append utilities | Append/skip design is useful but CSV appends are vulnerable to concurrent writers or partial final lines. | README’s resumability claim and utility-based append design. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | Duplicates or silent corruption are possible. | Use per-run partitions or SQLite/Parquet checkpoints and atomic consolidation. | Medium | Before next run |
| F27 | High | Merge safety | `06_make_final_dataset.py` | Required columns are checked, but one-to-one merge and duplicate-ID enforcement are not documented as part of the merge. | Script beginning and separate validator. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/blob/main/scripts/06_make_final_dataset.py)) | Duplicate rows could multiply during joins if validation is skipped. | Enforce uniqueness inside the merge with `validate="one_to_one"`. | Small | Before next run |
| F28 | Critical | Missing pipeline stage | `scripts/` versus Stage 5 | Public scripts stop at dataset merge; no public QA-report, review-workbook, review-ingestion or adjudication script exists. | Script manifest versus Stage 5 claims. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/tree/main/scripts)) | Stage 5 is aspirational, not reproducible. | Implement and document Stage 7–10 human-review tooling. | Large | Before expert review |
| F29 | High | Reviewer usability | Reviewer area | No workload, item count, access, saving, submission, review-round or acknowledgement procedure. | Reviewer page. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/reviewer-area.html)) | Reviewer requires private instructions. | Publish complete start-to-submission guidance. | Medium | Before presentation |
| F30 | High | Taxonomy provenance | `taxonomy/cefr_function_taxonomy_v0_2.csv` | A versioned taxonomy exists, but no public source map, release note, validation report or Companion Volume derivation table was found. | Taxonomy manifest and site description. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/tree/main/taxonomy)) | “CEFR-derived” cannot be independently checked. | Add taxonomy metadata, source mapping and change log. | Medium | Before expert review |
| F31 | High | Evidence status | Site-wide | “Tier 4 candidate material” is prominent but the tier scale is not defined. | Homepage and Stage 5. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html)) | Members cannot interpret what Tier 4 permits. | Publish the full evidence-tier framework and permitted claims. | Small | Before presentation |
| F32 | Medium | Status terminology | Stage 4–5 and outputs | Terms such as `final`, `adjudication` and `final dataset` coexist with “provisional.” | Workflow and final-script docstring. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/workflow.html)) | Status may be misunderstood downstream. | Rename to `candidate_combined` and separate process/review/validation status fields. | Small | Before next run |
| F33 | High | Website status | Homepage | No actual progress dashboard or next milestone is supplied, despite README directing users there for status. | README status line and homepage. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | Members cannot tell what has been completed. | Add dated stage-by-language status table. | Small | Before presentation |
| F34 | High | Data access | Homepage/technical setup | Drive and Colab roles are stated, but permission, account and safe-working procedures are absent. | Homepage and technical page. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html)) | Non-technical members cannot start safely. | Add Data and Access page. | Medium | Before presentation |
| F35 | Medium | Information architecture | Site navigation | Navigation is topic-based and lacks Start Here, Current Status, Data and Access, Outputs, Governance and Contact. | Main navigation is identical across pages. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/index.html)) | Operational questions are hard to answer. | Rebuild navigation around member tasks. | Medium | Before presentation |
| F36 | Medium | Repository organisation | `docs/`, `docs_project/`, `methodology/` | Multiple documentation locations compete; some named guidance directories appear to be placeholders while guidance exists elsewhere. | Repository manifests. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG/tree/main/docs)) | Newcomers cannot identify authoritative files. | Consolidate and add a repository map. | Medium | Before next run |
| F37 | High | Licensing | README and taxonomy/docs | Apache 2.0 applies to code/notebooks, while taxonomy and documentation may have separate unspecified terms. | README licence section. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | Reuse rights are unclear. | Add explicit documentation, taxonomy and sample-data licences. | Medium | Before publication |
| F38 | High | Data governance | API processing | No public policy explains whether restricted/licensed corpus sentences may be sent to an external API, or what retention/privacy controls apply. | Technical architecture names OpenAI as the processing engine but gives no governance conditions. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/technical-setup.html)) | Potential licence, confidentiality and privacy risk. | Add approved-data, privacy, vendor-retention and responsibility rules. | Medium | Before next run |
| F39 | High | Validation | Methodology/reviewer area | No public protocol for double coding, agreement measurement, human-model comparison or adjudication sampling. | Reviewer page discusses decisions but not study design. ([pertam.github.io](https://pertam.github.io/ALTE-Common-Corpus-SIG/reviewer-area.html)) | Reliability cannot be reported. | Pre-register the review and validation design. | Medium | Before expert review |
| F40 | Medium | Maintenance | Repository/site | No visible release, change log, model register or data-release register; GitHub reports no releases. | Repository releases section. ([github.com](https://github.com/Pertam/ALTE-Common-Corpus-SIG)) | Version drift is difficult to control. | Add tagged releases and registers. | Medium | Before publication |

## 5.1 Cross-document consistency matrix

| Topic | Website | README | Code/config/templates | Assessment | Recommended authority |
|---|---|---|---|---|
| Project name/scope | Consistent name; broad Atlas scope | Broad Atlas scope | Public code covers corpus-to-function-tag pipeline | **Scope mismatch** | Homepage status table plus formal workflow specification |
| Pilot languages | English, French, Spanish, German, Czech | Same | Defaults include `en`, `fr`, `es`, `de`, `cs` | Consistent at headline level | `config/languages.yaml` |
| Corpus description | Generic raw corpora; Leipzig mentioned in further reading | Large corpora on Drive | Stage 01 specifically expects Leipzig-style sentence files | Incomplete | Corpus register |
| Workflow stages | Five stages | Quickstart focuses on tagging | Scripts are effectively stages 00–06 | Numbering mismatch | Machine-readable workflow manifest |
| Script filenames | Obsolete unnumbered names on Stage 4 | Obsolete unnumbered names | Numbered current names | **Confirmed error** | Repository script manifest |
| Taxonomy filename | Generic controlled taxonomy | `taxonomy_en.csv` example | `cefr_function_taxonomy_v0_2.csv` | **Confirmed error** | Taxonomy release manifest |
| Input schema | Examples use `language`, `sentence_id`, `row_id` | Says only `row_id`, `sentence` minimum | Validator expects `language_code`, `lemma`, `pos`, `sentence_uid`, `sentence` | Inconsistent | Versioned schema files |
| Model selection | No exact model on site | Says config selects model | Code uses utility/CLI environment defaults | Unclear | Run config plus run manifest |
| Prompt versions | Claims exact auto-extraction | Scripts are canonical | Prompt text embedded in numbered scripts | Stale duplication | Versioned prompt files, generated site |
| Pass 1 | Initial whole-sentence tag | Same | Same | Broadly consistent | Prompt specification |
| Pass 2 | Called blind but sees Pass 1 | Called blind validation | Takes Pass 1 as input | **Terminological/methodological error** | Redesign or rename |
| Pass 3 | Called adjudication | Same | Automated model resolution | **Terminological error** | Human adjudication protocol |
| Confidence | Numeric ranges on methodology page; categorical elsewhere | Not fully defined | `high/medium/low` | Inconsistent | Schema and validation protocol |
| ARF threshold | `≥50` | Config claim | Pilot ARF-style implementation | Name overstates measure | Statistical-method specification |
| Lemma sample | 15 per language | Not prominent | Script supports 15 | Consistent as engineering pilot | Sampling protocol |
| Sentence sample | “All sentences”; workflow example says 50 | Not clearly reconciled | Supports all or capped sample | Ambiguous | Sampling protocol |
| Storage | GitHub/Drive/Colab roles | Same | Folder templates exist | Broadly consistent, operationally incomplete | Data and Access page |
| Review procedure | Principles and example decisions | Minimal | Template only; no workflow scripts | Aspirational | Reviewer handbook and review schema |
| Evidence status | Provisional/Tier 4 | Same | Provisional docstrings | Warning consistent; tier undefined | Governance/status framework |
| Licence | General warning | Separate terms may apply | No visible separate licence register | Incomplete | Licence and data-release register |
| Contact | GitHub issues | GitHub issues | No role-specific owner | Too weak for access/support | Contact and responsibility page |
| Last updated | 09 June 2026 | No matching build identifier | Current SHA not displayed | Not auditable | Automated build metadata |

---

# 6. SIG-member journey tests

## 6.1 Non-technical SIG member

**Clear**

- The project’s broad purpose.
- Why simple vocabulary lists are inadequate.
- The five languages.
- The fact that LLM outputs are provisional.
- The idea of a staged corpus-to-review workflow.

**Uncertainty begins**

- At “What has actually been completed?”
- At “Where can I see an output?”
- At “What should I do as a SIG member?”
- At “Who is leading this and whom do I ask?”

**Cannot be found**

- A dated status table.
- A roadmap.
- A public sample output explicitly labelled by status.
- Named roles and responsibilities.
- Access-request instructions.

**Required change**

Add a Start Here page, current-status panel, role-based routes and a plain-language distinction between implemented and planned work.

## 6.2 Language reviewer

**Clear**

- Review the whole sentence.
- Do not rubber-stamp the model.
- Accept, change, mark uncertain or reject.
- Explain corrections briefly.

**Uncertainty begins**

- Which file to open.
- How many items to review.
- Whether the task is sentence-function review or concept/CEFR review.
- Which columns are editable.
- Whether multiple functions are permitted.
- What to do if context is insufficient.
- How to save and submit.

**Access barriers**

- Drive could not be inspected.
- No permission request route is public.
- No review-copy procedure is public.

**Required change**

Provide the complete reviewer start page drafted in section 11, a fixed workbook data dictionary and an actual submission route.

## 6.3 Technical contributor

**Clear**

- The intended script order.
- The broad GitHub/Drive/Colab architecture.
- The existence of validation, configuration and schema files.

**Uncertainty begins**

- Immediately on using the README commands, because filenames and sample paths are stale.
- When determining whether YAML config is actually used.
- When installing exact spaCy models.
- When identifying a no-cost test route.
- When deciding how to record a run.

**Cannot be verified**

- Whether the notebook executes.
- Whether requirements install cleanly.
- Whether scripts compile.
- Whether sample data passes validation.

**Required change**

Repair the quickstart, add public fixtures, provide a mocked test mode and generate a run manifest automatically.

## 6.4 Project lead

**Clear**

- The intended research direction.
- The broad methodological safeguards.
- The main folders and proposed workflow.

**Uncertainty begins**

- Which document is authoritative.
- How current status is recorded.
- Which settings were used for a completed run.
- How human review returns to the pipeline.
- What constitutes approval for publication.

**Required change**

Adopt the source-of-truth model in section 15 and the stage-gate status framework in section 13.

## 6.5 External researcher

**Clear**

- The project is a pilot.
- Code is public.
- Full corpora and outputs are not public.
- CEFR claims have not been validated.

**Cannot be found**

- Fixed release identifier.
- Corpus provenance register.
- Data licence.
- Taxonomy derivation report.
- Citation guidance.
- Public data-release register.
- Reproduction record for any completed run.

**Required change**

Create tagged releases with a citation file, methodology version, corpus manifest, licences and public sample release.

---

# 7. Recommended website architecture

## 7.1 Start here

- **Audience:** Everyone.
- **Purpose:** Orient a first-time visitor in under two minutes.
- **Questions:** What is this? Is it finished? What can I do?
- **Sections:** Overview; warning; current status; role routes; next milestone.
- **Calls to action:** Choose a role; see current status; request access.
- **Links:** Status, workflow, data/access, reviewer start, technical start.
- **Existing material:** Replace homepage with section 9 draft.

## 7.2 Project overview

- **Audience:** SIG members, external readers.
- **Purpose:** Explain the problem, aims, scope and intended outputs.
- **Questions:** Why does the project exist? What will it produce?
- **Sections:** Rationale; pilot languages; intended deliverables; scope boundaries.
- **Calls to action:** Read workflow; view methodology.
- **Existing material:** Merge the strongest parts of the current rationale and homepage.

## 7.3 Current status and roadmap

- **Audience:** All members.
- **Purpose:** State what is complete, in progress, blocked and planned.
- **Questions:** What exists now? What is provisional? What happens next?
- **Sections:** Stage-by-language dashboard; output status; blockers; next milestone; last update.
- **Calls to action:** Volunteer; report blocker.
- **Existing material:** New page.

## 7.4 Choose your role

- **Audience:** SIG member, reviewer, contributor, lead, external researcher.
- **Purpose:** Provide task-based routes.
- **Questions:** Which pages and files apply to me?
- **Sections:** Six role cards with expected knowledge and next action.
- **Calls to action:** Start reviewer task; run technical test; inspect public materials.
- **Existing material:** Expand homepage’s current audience table.

## 7.5 Data and access

- **Audience:** Everyone needing files or tools.
- **Purpose:** Explain GitHub, Drive and Colab and how to obtain access.
- **Questions:** What is public? What is restricted? Which file is correct?
- **Sections:** System roles; access matrix; request process; folder map; file statuses; safe working.
- **Calls to action:** Request access; open repository; open Colab.
- **Existing material:** Replace thin technical-infrastructure descriptions with section 10 draft.

## 7.6 End-to-end workflow

- **Audience:** All roles.
- **Purpose:** Describe each stage, why it exists and its status.
- **Questions:** What enters and leaves each stage? Who is responsible?
- **Sections:** Stage map; status; inputs/outputs; responsible role; quality gate.
- **Calls to action:** Open stage details; view worked example.
- **Existing material:** Retain but revise current workflow and stage pages.

## 7.7 Reviewer start

- **Audience:** Language and assessment experts.
- **Purpose:** Make review possible without a meeting.
- **Questions:** What do I review? How do I decide and submit?
- **Sections:** Prerequisites; access; workload; fields; decisions; worked example; submission.
- **Calls to action:** Open workbook; download taxonomy; submit review.
- **Existing material:** Replace reviewer area with section 11 draft; retain methodological examples.

## 7.8 Technical reproduction

- **Audience:** Technical contributors.
- **Purpose:** Provide tested local and Colab routes.
- **Questions:** How do I run a small test and a real run?
- **Sections:** Prerequisites; environment; fixtures; stage commands; resume; troubleshooting; run manifest.
- **Calls to action:** Run no-API smoke test; open Colab; report issue.
- **Existing material:** Rewrite technical setup and link `pipeline_run_guide.md`.

## 7.9 Methodology

- **Audience:** Researchers, reviewers, leads.
- **Purpose:** Define corpus, units, sampling, taxonomy and validation logic.
- **Questions:** Why are these methods defensible?
- **Sections:** Corpus design; units; statistics; sampling; taxonomy; LLM protocol; human review; limitations.
- **Calls to action:** Download protocol; view decision log.
- **Existing material:** Retain current principles but add implemented details.

## 7.10 Governance and validation

- **Audience:** Leads, SIG, external researchers.
- **Purpose:** Define evidence statuses, responsibilities and permitted claims.
- **Questions:** When does output become reviewed, validated or publishable?
- **Sections:** Status model; roles; adjudication; licences; privacy; model governance; publication gates.
- **Calls to action:** View governance statement; report concern.
- **Existing material:** New page.

## 7.11 Outputs and releases

- **Audience:** All.
- **Purpose:** Make public artefacts discoverable.
- **Questions:** What can I download and what status does it have?
- **Sections:** Public samples; taxonomy releases; code releases; review summaries; validation reports.
- **Calls to action:** Download; cite; inspect change log.
- **Existing material:** New page.

## 7.12 FAQ and troubleshooting

- **Audience:** All.
- **Purpose:** Answer project, access, review and technical questions.
- **Existing material:** Retain FAQ, add access and troubleshooting sections; move extensive reading lists elsewhere.

## 7.13 Contact and support

- **Audience:** All.
- **Purpose:** Give named routes for access, methods, technical issues and review questions.
- **Sections:** Responsibility matrix; access contact; GitHub issues; response expectations.
- **Existing material:** New page.

---

# 8. Page-by-page revision plan

| Existing page | Action | Accurate content to retain | Problems | Exact revision |
|---|---|---|---|---|
| `index.html` | **Replace** | Provisional warning; five languages; high-level infrastructure roles | No real status, access route, outputs or actionable role choices | Use section 9 draft; add build SHA and dated status |
| `rationale-and-use-cases.html` | **Revise** | Polysemy, cross-language mismatch, possible use cases | Long and sometimes shifts from pilot to prospective product without status distinction | Add “possible future use—not current capability” labels; shorten examples |
| `workflow.html` | **Revise** | Five-stage overview and sentence walkthrough | Calls Pass 2 blind and Pass 3 adjudication; worked example uses illustrative values that resemble results | Add implementation status per stage; rename passes; label every example prominently |
| `technical-setup.html` | **Replace/split** | Tool-role table | Too short to support setup; NotebookLM appears without operational explanation | Split into Data and Access plus Technical Reproduction |
| `reviewer-area.html` | **Replace** | Whole-sentence principle; decision examples; good-comment examples | No access, workload, workbook protection, saving or submission | Use section 11; move theory to a reviewer-reference subsection |
| `methodology.html` | **Revise/split** | Concept/sense principles; receptive/productive distinction; cross-language divergence | Mixes implemented function tagging with unimplemented CEFR candidate processes; confidence inconsistent | Add “implemented/planned” labels; move status/governance to separate page; remove numeric confidence bands unless implemented |
| `faq.html` | **Revise** | Plain-language project answers | Omits status, access, licences, costs, API data handling and troubleshooting | Add sections on access, current status, model costs, privacy, broken links and reviewer submission |
| `further-reading.html` | **Retain but demote** | Useful multilingual reading guide | More complete than core operational guidance; several rows point to broad homepages rather than precise sources | Move out of primary navigation; add exact bibliographic references and checked dates |
| `stage1-corpus-preparation.html` | **Revise** | Importance of metadata and licensing | Does not identify actual corpora or explain that code expects pre-segmented Leipzig-style input | Add corpus register and exact input contract |
| `stage2-processing.html` | **Revise** | Token/POS/lemma explanation | Says sentence splitting is performed, but public script accepts prepared sentence rows; statistics undefined | Document actual implementation, model versions, QA samples and formulas |
| `stage3-sampling.html` | **Revise** | Explicit threshold and 15-lemma pilot sample | Does not distinguish engineering sample from research sample; all-versus-50 ambiguity | Explain that current sample is a smoke-test design; publish seed and selection output |
| `stage4-function-tagging.html` | **Correct immediately** | Provisional warning; controlled taxonomy | Obsolete filenames; stale “exact prompt” claim; inaccurate blind/adjudication terminology | Generate content from actual prompts and commit; rename passes |
| `stage5-qa-review.html` | **Split** | Proposed QA checks and status caution | Presents unimplemented activities as an operative stage | Separate “planned Stage 5” from “currently implemented merge”; link actual scripts when available |
| `links.html` | **Merge** | Potential central link register | Not in main navigation; duplicates homepage links | Merge into Data and Access; remove standalone page unless generated automatically |

---

# 9. Complete replacement homepage draft

> The following is paste-ready except for items explicitly marked as project-lead decisions.

---

# ALTE Common Corpus SIG  
## European CEFR Vocabulary Atlas pilot

The ALTE Common Corpus SIG is testing a multilingual research workflow for the European CEFR Vocabulary Atlas.

The pilot combines corpus evidence, lemma statistics, sentence examples, a CEFR-informed communicative-function taxonomy, LLM-assisted candidate classification and expert review. It currently covers:

- English;
- French;
- Spanish;
- German;
- Czech.

The long-term aim is to support vocabulary description at the level of **concepts, senses, language-specific forms and communicative uses**, rather than producing a simple translated word list.

> **Important: pilot material, not validated CEFR data**
>
> All current automated classifications are provisional candidate material. They must not be treated as validated CEFR vocabulary levels, approved Atlas entries or published reference data.
>
> Human review, adjudication, corpus validation, cross-language validation and publication approval are separate later stages.

## Current status

**Last reviewed:** 24 June 2026  
**Repository branch:** `main`  
**Website build commit:** `[PROJECT-LEAD ACTION: insert automatically generated full commit SHA]`

| Component | Current status | What this means |
|---|---|---|
| Public project website | Available | Rationale, workflow and methodological principles can be read publicly |
| Corpus-preparation scripts | Prototype available | Static code is public; full multilingual execution still requires verification |
| Tokenisation, POS and lemmatisation | Prototype available | Language-specific quality evaluation is still required |
| Lemma statistics and pilot dispersion measure | Prototype available | The current measure must not be presented as validated standard ARF without further work |
| Lemma and sentence sampling | Engineering pilot available | Current 15-lemma samples are for workflow testing, not representative language-level inference |
| LLM Pass 1 | Prototype available | Produces provisional sentence-function candidates |
| LLM Pass 2 | Prototype validator available | Currently sees Pass 1 output; it is not independent blind double coding |
| LLM Pass 3 | Prototype automated resolution available | It is not human adjudication |
| Reviewer workbooks and submission workflow | `[PROJECT-LEAD: confirm status]` | Public operational instructions are still required |
| Expert review | `[PROJECT-LEAD: not started / in progress / completed]` | Reviewed rows must remain distinguishable from model output |
| Corpus and cross-language validation | Not completed | No validated CEFR claim should be made |
| Approved Atlas release | Not completed | No current output is approved for publication as Atlas data |

## Choose your route

### I want a quick project overview

Read:

1. [Why the project is needed](rationale-and-use-cases.html)
2. [How the workflow operates](workflow.html)
3. [Current status and roadmap](status.html)

### I am an ALTE Common Corpus SIG member

Start with:

1. [Project overview](project-overview.html)
2. [Current status](status.html)
3. [Choose how to participate](roles.html)

You do not need Python or GitHub experience to contribute as a language, assessment or methodology expert.

### I am a language reviewer

Go to the [Reviewer start page](reviewer-start.html).

It explains:

- what you will review;
- how many items are assigned;
- which spreadsheet columns you may edit;
- how to accept, change, reject or mark an item uncertain;
- how to handle insufficient context and multiple plausible functions;
- how to save and submit your work.

### I am a technical contributor

Go to [Technical reproduction](technical-reproduction.html).

Begin with the public no-API smoke test before using restricted data or making paid model calls.

### I am a project lead or work-package owner

Go to:

- [Current status and roadmap](status.html);
- [Governance and validation](governance.html);
- [Roles and responsibilities](contact.html);
- [Decision and change log](change-log.html).

### I am an external researcher

You may inspect the public website, repository, code, taxonomy releases and public sample data.

See [Data, access and permitted use](data-and-access.html) for restrictions and citation information.

## Where project materials are stored

### GitHub

GitHub contains the public project structure:

- scripts and notebooks;
- configuration;
- taxonomy releases;
- schemas and templates;
- methodology and technical documentation;
- small public examples;
- this website.

[Open the public repository](https://github.com/Pertam/ALTE-Common-Corpus-SIG)

### Google Drive

Google Drive is used for permission-controlled working materials:

- raw and licensed corpora;
- metadata and licence records;
- interim processing files;
- full model outputs;
- QA reports;
- reviewer workbooks;
- review and adjudication records;
- release candidates.

Drive access is not automatic.

[Request or check Drive access](data-and-access.html#requesting-access)

### Google Colab

Colab provides a browser-based environment for running the public code while reading and writing permitted files in Drive.

[Open the project Colab notebook](https://colab.research.google.com/github/Pertam/ALTE-Common-Corpus-SIG/blob/main/notebooks/00_main_project_runner_colab.ipynb)

Using Colab does not itself give access to restricted data.

## Workflow at a glance

1. **Document the corpus**  
   Record the source, language, date, version, genre, licence, restrictions and responsible owner.

2. **Prepare and process sentences**  
   Assign stable identifiers, tokenise, POS-tag and lemmatise with language-appropriate tools.

3. **Compute lemma evidence and create a pilot sample**  
   Calculate frequency and documented dispersion measures, then select a reproducible test sample.

4. **Generate provisional function candidates**  
   Run Pass 1, an informed validator pass and, where necessary, an automated resolution pass.

5. **Run automated QA**  
   Check schemas, identifiers, taxonomy values, missing rows, duplicated rows, disagreement and provenance.

6. **Conduct expert review**  
   Language and assessment experts accept, correct, reject or mark rows uncertain.

7. **Conduct human adjudication and validation**  
   Resolve expert disagreement, evaluate reliability and validate corpus, cross-language and CEFR-related claims.

8. **Approve a release**  
   Publish only material that has passed the project’s documented release gates.

[See the complete workflow](workflow.html)

## Intended outputs

The pilot is intended to prepare:

- documented multilingual corpus evidence;
- lemma-frequency and dispersion tables;
- reproducible lemma and sentence samples;
- a versioned communicative-function taxonomy;
- provisional sentence-function classifications;
- automated QA reports;
- expert-reviewed and adjudicated records;
- cross-language comparison material;
- validation reports;
- clearly labelled public releases.

Not all of these outputs have yet been implemented or completed. See the [current status page](status.html).

## What happens next

The immediate priorities are:

1. align the website, README, scripts and configuration;
2. publish the corpus-provenance and access register;
3. fix and test the technical quickstart;
4. define the taxonomy and evidence-status framework;
5. establish the expert-review and adjudication protocol;
6. run a small, fully recorded multilingual test;
7. review the results before any larger processing run.

## Support and contact

- **Access questions:** `[PROJECT-LEAD DECISION: named contact or access-request form]`
- **Reviewer questions:** `[PROJECT-LEAD DECISION: reviewer coordinator]`
- **Methodology questions:** `[PROJECT-LEAD DECISION: methodology lead]`
- **Technical problems:** [Open a GitHub issue](https://github.com/Pertam/ALTE-Common-Corpus-SIG/issues)
- **Broken website links:** [Report a website issue](https://github.com/Pertam/ALTE-Common-Corpus-SIG/issues)

---

# 10. Complete data-and-access page draft

---

# Data, access and safe working

This page explains where project materials are stored, which materials are public, how to request access and how to work without overwriting master files.

## The three project systems

### GitHub: public code and documentation

Use GitHub to:

- read the public project documentation;
- inspect scripts, notebooks and configuration;
- obtain taxonomy releases and schemas;
- download small public examples;
- report technical or documentation problems;
- identify the repository commit used for a processing run.

GitHub should not contain:

- restricted corpora;
- API keys;
- private reviewer information;
- full licensed outputs;
- files containing personal or sensitive data;
- unpublished master review workbooks.

Public repository:

`https://github.com/Pertam/ALTE-Common-Corpus-SIG`

### Google Drive: permission-controlled working files

Use Drive for:

- raw or licensed corpora;
- corpus metadata and licence records;
- interim processing files;
- full model-generated output;
- QA reports;
- reviewer workbooks;
- completed reviews;
- adjudication records;
- release candidates and exports.

Drive access is controlled because some corpus and review material may not be suitable for public redistribution.

**Drive location:**  
`[PROJECT-LEAD DECISION: insert the approved shared-drive or folder URL]`

### Google Colab: running the pipeline

Use Colab when you need a browser-based Python environment.

The project Colab notebook can:

- clone the public GitHub repository;
- mount your permitted Drive;
- define project paths;
- install dependencies;
- run validation and pipeline commands;
- save outputs back to Drive.

Colab does not automatically provide Drive access. You must sign in with an account that has been granted permission.

**Required account type:**  
`[PROJECT-LEAD DECISION: institutional account / invited Google account / either]`

## What is public and what is restricted?

| Material | Public? | Location | Notes |
|---|---:|---|---|
| Website | Yes | GitHub Pages | Public project information |
| Code and notebooks | Yes | GitHub | Apache 2.0 applies to code/notebooks |
| Configuration examples | Yes | GitHub | Actual run settings must be archived separately |
| Taxonomy | Publicly visible | GitHub | Exact reuse licence must be stated |
| Schemas and templates | Yes | GitHub | Use the version linked from the current release |
| Small illustrative examples | Yes | GitHub | Must be clearly labelled synthetic or redistributable |
| Raw corpora | Usually no | Drive/institutional storage | Original licences continue to apply |
| Full interim files | Usually no | Drive | May contain corpus text |
| Full LLM output | Usually no | Drive | Provisional and potentially licence-restricted |
| QA reports | Permission controlled | Drive | Public summaries may later be released |
| Reviewer workbooks | No, unless approved | Drive | May contain reviewer identities/comments |
| Adjudication records | Permission controlled | Drive | Publication form to be decided |
| Validated public releases | Not yet available | Release area | Requires governance approval |

## Requesting access

1. Identify the role for which you need access:
   - language reviewer;
   - technical contributor;
   - project lead;
   - methodology researcher;
   - external researcher.

2. State:
   - your name;
   - institution;
   - project role;
   - language or work package;
   - the folder or dataset required;
   - why access is needed;
   - whether you need view, comment or edit permission.

3. Send the request to:

   `[PROJECT-LEAD DECISION: access email or form]`

4. The responsible owner should confirm:
   - whether access is approved;
   - the permitted account;
   - the permitted use;
   - whether files may be downloaded;
   - whether derived outputs may be shared;
   - the access expiry date, if applicable.

5. Do not ask another member to forward restricted files outside the approved system.

## Proposed Drive folder map

The project lead should verify this map against the live Drive before publication.

```text
ALTE-Common-Corpus-SIG/
├── 00_governance/
│   ├── corpus_register/
│   ├── licence_register/
│   ├── access_register/
│   ├── decision_log/
│   └── release_approvals/
├── 01_raw/
│   └── {language}/
│       ├── corpus_original/
│       ├── metadata/
│       └── licensing/
├── 02_processed/
│   └── {language}/
│       ├── sentences/
│       ├── tokens/
│       ├── lemma_sentence_index/
│       └── lemma_stats/
├── 03_samples/
│   └── {language}/
│       ├── lemma_samples/
│       └── sentence_samples/
├── 04_model_runs/
│   └── {run_id}/
│       ├── run_manifest/
│       ├── pass1/
│       ├── pass2/
│       ├── pass3_automated_resolution/
│       ├── raw_responses/
│       ├── errors/
│       └── usage/
├── 05_qa/
│   └── {run_id}/
├── 06_review/
│   └── {review_round}/
│       ├── master_read_only/
│       ├── assignments/
│       ├── submitted/
│       └── consolidated/
├── 07_adjudication/
├── 08_validation/
└── 09_releases/
    ├── internal_candidates/
    └── approved_public/
```

## File statuses

Every working file should have an explicit status.

| Status | Meaning | May be cited as validated? |
|---|---|---:|
| `raw` | Original source material | No |
| `processed` | Machine-processed corpus material | No |
| `sampled` | Selected for pilot processing | No |
| `model_generated` | Produced by an LLM | No |
| `automated_qa_passed` | Passed structural checks | No |
| `expert_reviewed` | Reviewed by at least one expert | Not by itself |
| `adjudication_required` | Human disagreement remains | No |
| `adjudicated` | Human disagreement resolved | Not by itself |
| `corpus_validated` | Checked against the defined corpus protocol | Only within stated limits |
| `cross_language_validated` | Cross-language comparison reviewed | Only within stated limits |
| `externally_validated` | Independent validation completed | Subject to report |
| `approved_for_publication` | Formal release gate passed | Yes, within release documentation |

Processing status, review status, validation status and release status should be separate columns rather than one overloaded field.

## Naming and versioning

Use:

```text
{stage}_{language}_{content}_{run_id}_{status}_schema-{version}.{extension}
```

Example:

```text
stage4_en_sentence-functions_20260624T103000Z_a1b2c3d_model-generated_schema-1.0.csv
```

Each `run_id` must link to a manifest containing:

- full repository commit SHA;
- date and UTC time;
- operator;
- source-data version;
- configuration file and hash;
- prompt versions and hashes;
- taxonomy version and hash;
- model name and provider snapshot, where available;
- package and NLP-model versions;
- random seeds;
- input and output checksums;
- row counts;
- errors, retries and exclusions;
- token and cost totals.

## How to locate the correct file

Before opening or editing a file, check:

1. Is it in the correct stage folder?
2. Is the language correct?
3. Does its run ID match the assignment?
4. Is the schema version current?
5. Is its status appropriate?
6. Is it a master file or an assigned copy?
7. Does the file have a README or run manifest?
8. Has the project lead marked it superseded?

Do not select files only because they have words such as `final`, `latest` or `new` in their names.

## Safe working practices

- Never edit a file in `master_read_only`.
- Work only in your assigned copy.
- Do not rename protected identifier columns.
- Do not sort and paste only part of a sheet unless row identifiers remain intact.
- Do not delete machine-generated columns.
- Do not place API keys in notebooks, spreadsheets or Drive text files.
- Do not download restricted corpora to unmanaged devices.
- Do not forward reviewer workbooks outside the approved group.
- Do not overwrite a previous run.
- Do not move a file to a later status folder yourself unless you are the responsible stage owner.
- Report suspected duplication, corruption or personal data immediately.

## Creating and submitting a review copy

1. Open the assignment link supplied by the reviewer coordinator.
2. Confirm that the file name contains your assignment ID.
3. Make a copy only if instructed.
4. Edit only the columns marked `REVIEWER EDITABLE`.
5. Preserve `row_id`, source, model-output and taxonomy columns.
6. Save progress in the assigned folder.
7. When complete, change the submission status field to `submitted`.
8. Move or upload the file to:

   `[PROJECT-LEAD DECISION: submitted-review folder or form]`

9. Notify:

   `[PROJECT-LEAD DECISION: reviewer coordinator]`

10. Do not merge your own decisions into the project master.

## Preventing version conflicts

- One assignment should have one named reviewer copy.
- Master workbooks must be read-only.
- Submitted files must not be reopened for editing without a new revision number.
- Consolidation must be performed by script using `row_id` and assignment ID.
- Duplicate or missing IDs must stop the consolidation process.
- Every consolidation must create a report listing accepted, rejected and conflicting submissions.

## Help and problem reporting

- Access problem: `[PROJECT-LEAD DECISION: contact]`
- Reviewer question: `[PROJECT-LEAD DECISION: contact]`
- Broken link or technical bug: `https://github.com/Pertam/ALTE-Common-Corpus-SIG/issues`
- Suspected data-governance problem: `[PROJECT-LEAD DECISION: governance contact]`
- Urgent accidental sharing or credential exposure: `[PROJECT-LEAD DECISION: incident route]`

---

# 11. Complete reviewer start-page draft

---

# Reviewer start page

## What you are being asked to do

You are reviewing **provisional candidate material** produced by the pilot workflow.

You are not being asked to confirm that an LLM is correct. You are being asked to make an independent expert judgement and record it clearly.

Your assignment may cover one of two tasks:

1. **Sentence-function review**  
   Decide which communicative function best describes what the whole sentence is doing.

2. **Concept or vocabulary review**  
   Check the concept/sense, language-specific form, evidence and provisional receptive/productive CEFR judgement.

Your assignment email or workbook must state which task applies. Do not assign CEFR levels during a sentence-function-only task.

> Model-generated classifications are not validated CEFR data. Your review improves the candidate material, but one review alone does not make a row validated or approved for publication.

## Before you begin

You need:

- expert knowledge of the assigned language;
- sufficient English to read the project guidance and taxonomy labels;
- access to the assigned workbook;
- the correct taxonomy version;
- the assignment instructions;
- approximately `[PROJECT-LEAD DECISION: estimated minutes per item and total workload]`;
- no programming knowledge.

You do not need:

- Python;
- Git;
- an OpenAI account;
- an API key;
- permission to edit the project master file.

## Your assignment

| Item | Assignment value |
|---|---|
| Language | `[insert]` |
| Review type | `[sentence function / concept and CEFR / cross-language alignment]` |
| Number of rows | `[insert]` |
| Taxonomy version | `[insert]` |
| Workbook schema | `[insert]` |
| Review round | `[insert]` |
| Submission deadline | `[insert]` |
| Reviewer coordinator | `[insert]` |
| Submission location | `[insert]` |

If any value is missing, stop and contact the reviewer coordinator.

## Workbook fields

### Protected fields: do not edit

Typical protected fields include:

- `row_id`;
- `language_code`;
- `sentence_uid`;
- `sentence`;
- `lemma`;
- `pos`;
- corpus-source fields;
- Pass 1 fields;
- Pass 2 fields;
- automated-resolution fields;
- model and prompt versions;
- taxonomy version;
- run ID;
- machine-generated confidence and rationale.

### Reviewer-editable fields

The standard reviewer fields should be:

| Field | What to enter |
|---|---|
| `reviewer_id` | Your assigned reviewer code |
| `expert_decision` | One permitted decision |
| `expert_primary_function_id` | Correct function ID if accepting or changing |
| `expert_secondary_function_id` | Optional second function, if allowed |
| `evidence_sufficiency` | `sufficient`, `insufficient_context`, or `unusable` |
| `expert_comment` | Short reason for the decision |
| `taxonomy_problem` | `true` if no available label fits adequately |
| `adjudication_required` | `true` if another expert decision is required |
| `reviewer_confidence` | Optional reviewer confidence using the defined scale |
| `review_status` | `in_progress` or `submitted` |

For concept-level tasks, additional fields may include:

- `expert_concept_id`;
- `sense_split_required`;
- `expert_language_form`;
- `expert_receptive_cefr`;
- `expert_productive_cefr`;
- `evidence_problem`;
- `cross_language_note`.

## Decision options

Use only the options provided in the workbook.

### `accept`

Use when the candidate label is defensible and no clearly better label is available.

You must still read the sentence independently.

### `change`

Use when another taxonomy label is clearly better.

Enter the replacement function ID and a short explanation.

### `uncertain`

Use when two or more interpretations remain reasonably possible.

State what the alternatives are.

### `insufficient_context`

Use when the sentence alone does not provide enough evidence.

Do not guess from the sampled lemma.

### `no_applicable_function`

Use when the sentence is interpretable but no taxonomy function adequately applies.

Set `taxonomy_problem = true` if this suggests a taxonomy gap.

### `reject_technical`

Use when the row is unusable because it is:

- malformed;
- duplicated in error;
- not in the target language;
- severely truncated;
- encoding-corrupted;
- incorrectly segmented;
- otherwise technically unsuitable.

`[PROJECT-LEAD DECISION: If the current workbook retains only accept/change/uncertain/reject, update it before review or publish an explicit mapping from these categories.]`

## Sentence-function review: step by step

### Step 1 — Read the whole sentence

Temporarily ignore the sampled lemma and model label.

Ask:

> What is the sentence doing communicatively?

### Step 2 — Decide whether the evidence is sufficient

Can the function be judged from this sentence alone?

If not, select `insufficient_context`.

### Step 3 — Identify the best primary function

Use the taxonomy definition and examples.

Do not choose a label merely because a particular keyword occurs.

### Step 4 — Consider a secondary function

If the task permits multilabel review, add a secondary function only when it is genuinely realised, not merely implied.

### Step 5 — Compare your judgement with the candidate

- same and defensible: `accept`;
- clearly better alternative: `change`;
- unresolved ambiguity: `uncertain`;
- no fit: `no_applicable_function`;
- unusable row: `reject_technical`.

### Step 6 — Write a short reason

A useful comment explains the communicative evidence.

Avoid comments such as “wrong,” “maybe” or “check.”

### Step 7 — Mark adjudication if needed

Set `adjudication_required = true` when:

- two labels remain plausible;
- another expert is needed;
- context is insufficient but the row might be recoverable;
- the taxonomy appears inadequate;
- a concept/sense disagreement affects multiple languages.

## Worked example

### Source row

- **Sentence:** “Please send the completed form to the address below.”
- **Sampled lemma:** `send`
- **Pass 1 candidate:** `requesting action`
- **Pass 2 validator:** `giving an instruction`
- **Automated resolution:** `giving an instruction`
- **Current status:** `model_generated`

### Independent reviewer reasoning

1. The sentence uses an imperative form.
2. It directs the reader to perform an administrative action.
3. It does not primarily ask whether the reader is willing to act.
4. “Giving an instruction” is therefore a better primary function than “requesting action.”

### Reviewer entry

| Field | Value |
|---|---|
| `expert_decision` | `accept` |
| `expert_primary_function_id` | `[valid taxonomy ID for giving an instruction]` |
| `evidence_sufficiency` | `sufficient` |
| `expert_comment` | `The imperative directs the reader to submit the form; it functions as an instruction rather than a request.` |
| `taxonomy_problem` | `false` |
| `adjudication_required` | `false` |
| `review_status` | `submitted` |

### Status after submission

The row becomes `expert_reviewed`.

It does **not** automatically become:

- adjudicated;
- corpus-validated;
- CEFR-validated;
- approved for publication.

If another reviewer disagrees, the row enters human adjudication.

## Multiple senses

For concept-level review:

- do not merge distinct meanings because they share a lemma;
- mark `sense_split_required = true` when necessary;
- describe the intended sense in plain language;
- check whether the proposed equivalent is natural for that sense;
- distinguish a single word from a multiword expression or construction.

Example:

- `bank` — financial institution;
- `bank` — side of a river.

These require different concept or sense records.

## Receptive and productive CEFR decisions

Only complete these fields if your assignment explicitly includes CEFR review.

Consider:

- communicative usefulness;
- transparency and cognate effects;
- register;
- morphology;
- governed prepositions or cases;
- aspect;
- collocation;
- sense complexity;
- corpus distribution;
- supplied learner or assessment evidence.

Do not assign a CEFR level from frequency alone.

Do not accept invented source evidence. If a source level or count is not supplied, leave it blank and flag the evidence problem.

## Saving progress

- Work only in your assigned copy.
- Do not change the filename unless instructed.
- Save after each review session.
- Keep `review_status = in_progress` until finished.
- Do not delete, reorder or rename protected columns.
- Do not paste values into filtered rows without checking `row_id`.
- Do not move the file outside the approved Drive folder.
- Do not email restricted workbooks as attachments.

## Submitting the review

1. Check that every assigned row has a decision or an explicit reason for being incomplete.
2. Set `review_status = submitted`.
3. Run the reviewer checklist below.
4. Save the workbook.
5. Move or upload it to:

   `[PROJECT-LEAD DECISION: submission folder or form]`

6. Notify:

   `[PROJECT-LEAD DECISION: reviewer coordinator]`

7. Do not edit the submitted file unless the coordinator reopens it as a new revision.

## What happens after submission

1. The project team validates file structure and identifiers.
2. Reviews are consolidated without overwriting model output.
3. Agreement and disagreement are calculated.
4. Rows requiring adjudication are assigned to another expert or panel.
5. Adjudicated decisions are recorded separately.
6. Validation analyses are conducted.
7. Only approved releases are published.

## Acknowledgement, authorship and data use

`[PROJECT-LEAD DECISION REQUIRED]`

Before review begins, the project must state:

- whether reviewers will be named;
- whether contribution qualifies for acknowledgement or authorship;
- how reviewer comments may be quoted or analysed;
- whether reviewer identities are confidential;
- how long review records are retained;
- whether reviewers may use the material in their own research.

## Reviewer checklist

- [ ] I used the assigned workbook and taxonomy version.
- [ ] I reviewed the whole sentence, not only the sampled lemma.
- [ ] I checked whether the evidence was sufficient.
- [ ] I used only permitted decision values.
- [ ] Any replacement function ID exists in the taxonomy.
- [ ] I recorded uncertainty instead of guessing.
- [ ] I flagged possible taxonomy gaps.
- [ ] I did not edit protected fields.
- [ ] My comments explain the decision.
- [ ] I marked adjudication where needed.
- [ ] I saved the file in the approved location.
- [ ] I set the submission status correctly.
- [ ] I did not describe the material as validated CEFR data.

---

# 12. Technical recommendations

## 12.1 Scripts

### `scripts/00_validate_inputs.py`

Add:

- schema-version checks;
- type and allowed-value validation;
- taxonomy hierarchy consistency;
- function-ID/label consistency;
- Pass 2 decision consistency:
  - `accept` must retain Pass 1 ID;
  - `change` must use a different ID;
- confidence-value checks;
- one-to-one `row_id` checks across passes;
- duplicate `sentence_uid` reporting;
- run-manifest validation;
- model/prompt/taxonomy version checks;
- output suitable for machine-readable CI, such as JSON.

### `scripts/01_prepare_leipzig_sentences.py`

Change `prepare_sentences()` to:

- accept a corpus-manifest row or manifest ID;
- preserve source filename, corpus package, year, version, register, document ID and licence ID;
- record the input file checksum;
- distinguish source sentence ID from internal sentence ID;
- log exact duplicates rather than silently discarding them;
- produce a duplicate audit file;
- stream or batch large files instead of retaining all rows in memory;
- record Unicode-normalisation policy;
- preserve the original text separately from normalised text.

### `scripts/02_tokenise_lemmatise.py`

Add output fields for:

- `nlp_tool`;
- `nlp_tool_version`;
- `model_name`;
- `model_version`;
- `model_checksum`;
- token character offsets;
- morphological features;
- dependency information if used later;
- whether the lemma is empty or fallback-generated;
- processing timestamp and run ID.

Add language-specific QA fixtures covering:

- contractions and clitics;
- German compounds;
- separable verbs;
- French elision;
- Spanish clitics;
- Czech case, aspect and diacritics;
- abbreviations and sentence-final punctuation;
- proper nouns and ambiguous forms.

Do not describe sentence splitting as implemented unless this script actually receives documents and performs it.

### `scripts/03_compute_lemma_stats.py`

Choose one option:

1. **Implement standard ARF**, with:
   - formal reference;
   - exact formula;
   - token-position definition;
   - corpus ordering and partition rules;
   - unit tests against known examples.

2. **Retain the custom pilot statistic**, but rename:
   - `arf_reduced_frequency` → `pilot_dispersion_adjusted_frequency`;
   - `arf_per_million` → `pilot_daf_per_million`.

Publish the formula and explain why it is suitable.

Also:

- define document and source dispersion separately;
- avoid computing source dispersion from a single undifferentiated source;
- report confidence intervals or stability under resampling where relevant;
- preserve corpus size and denominator with every output.

### `scripts/04_sample_lemmas_and_sentences.py`

Replace sequential row IDs with stable IDs derived from:

```text
language + lemma + POS + sentence_uid + sampling_protocol_version
```

Add:

- sampling-protocol version;
- random seed in every output;
- eligible-pool checksum;
- selected-lemma rank and selection probability;
- exclusion reason;
- stratification by POS and frequency band;
- optional domain/register balancing;
- sentence-context policy;
- duplicate-sentence policy;
- per-lemma sentence cap justified in the methodology;
- a unique-sentence table separate from lemma-sentence links.

### `scripts/05a_run_pass1.py`

Add explicit output options for:

- `no_applicable_function`;
- `insufficient_context`;
- optional `secondary_function_id`;
- `evidence_span` or brief evidence cue;
- model uncertainty without forcing a taxonomy label.

Do not ask the model to reproduce source identifiers unnecessarily; set identifiers in code after validation.

### `scripts/05b_run_pass2.py`

Make a project-lead decision:

- **Independent Pass 2:** provide the same source evidence and taxonomy but no Pass 1 label or rationale; compare results afterwards.
- **Informed validator Pass 2:** retain current input but remove “blind” everywhere.

If independent coding is selected, consider:

- separate prompt;
- different random seed;
- possibly a different approved model;
- shuffled taxonomy order;
- no shared rationales;
- separate run manifest.

### `scripts/05c_run_pass3.py`

Rename to something such as:

```text
05c_run_automated_resolution.py
```

Do not call the output adjudicated.

Escalation should include:

- different Pass 1/Pass 2 labels;
- either pass selecting insufficient evidence;
- either pass marking review required;
- low confidence;
- taxonomy mismatch;
- multilabel disagreement;
- missing output;
- contradictory validator decision.

Every resolved row should retain both original outputs.

### `scripts/06_make_final_dataset.py`

Rename to:

```text
06_build_candidate_review_dataset.py
```

Make `--samples` required for the research dataset.

Use:

```python
merge(..., validate="one_to_one")
```

Stop on:

- duplicate IDs;
- missing pass rows;
- unexpected additional rows;
- sentence mismatch;
- taxonomy-version mismatch;
- run-ID mismatch.

Do not use `final_*` for unreviewed candidate values. Prefer:

- `candidate_function_id`;
- `candidate_source`;
- `candidate_confidence`;
- `processing_status=model_generated`.

### Add missing scripts

Add:

```text
07_run_automated_qa.py
08_build_reviewer_workbooks.py
09_validate_review_submissions.py
10_consolidate_expert_reviews.py
11_prepare_human_adjudication.py
12_merge_adjudicated_decisions.py
13_build_validation_report.py
14_build_release_candidate.py
```

## 12.2 Notebooks

`notebooks/00_main_project_runner_colab.ipynb` should:

- check out a specified commit or release tag, not floating `main`;
- print the checked-out SHA;
- require the user to choose a test or production mode;
- default to a no-API smoke test;
- validate all paths before processing;
- avoid displaying API keys;
- write a run manifest before any API call;
- estimate rows, tokens and maximum cost;
- require explicit confirmation before paid calls;
- show resume instructions;
- display output locations and row counts;
- include troubleshooting cells;
- stop if data permissions or licence approval are not recorded.

## 12.3 Configuration

Create one schema-validated run configuration:

```yaml
run:
  run_id:
  operator:
  purpose:
  repository_commit:
  environment_lock_hash:

corpus:
  manifest_version:
  permitted_for_external_api: false

nlp:
  models:
    en:
      package:
      version:
    fr:
      package:
      version:

sampling:
  protocol_version:
  seed:
  min_measure:
  lemmas_per_language:
  sentences_per_lemma:

taxonomy:
  version:
  path:
  sha256:

prompts:
  pass1_version:
  pass2_version:
  resolution_version:

llm:
  provider:
  model:
  model_snapshot:
  temperature:
  max_output_tokens:

review:
  schema_version:
  review_round:
```

Document which fields may vary and which must be fixed across languages.

## 12.4 Schemas

Move from example CSV headers to machine-enforced schemas using JSON Schema, Pandera or Pydantic.

Required entities include:

- corpus;
- source/document;
- sentence;
- token;
- lemma statistics;
- lemma-sentence link;
- sampling run;
- taxonomy function;
- model run;
- model classification;
- concept;
- sense;
- language realisation;
- expert review;
- adjudication;
- validation result;
- release record.

## 12.5 Prompts

Create:

```text
prompts/
├── pass1/
│   └── v1.0.txt
├── pass2-independent/
│   └── v1.0.txt
├── automated-resolution/
│   └── v1.0.txt
└── schemas/
```

Each prompt release should include:

- version;
- date;
- purpose;
- input schema;
- output schema;
- permitted labels;
- abstention rules;
- context rules;
- change log;
- hash.

Generate the website prompt display from these files.

## 12.6 Testing

Add:

- `pytest`;
- unit tests for every transformation;
- known-answer tests for the statistical formula;
- tests for duplicate IDs and malformed CSV;
- tests for Pass 2 decision consistency;
- mocked API response tests;
- invalid-taxonomy tests;
- interrupted-write and resume tests;
- one-to-one merge tests;
- language-specific NLP fixtures;
- public end-to-end smoke fixture;
- link-checking CI;
- documentation-command CI.

No CI test should make paid API calls.

## 12.7 Logging and checkpointing

Every stage should produce:

- structured JSONL logs;
- start/end timestamps;
- input and output paths;
- row counts;
- skipped and failed IDs;
- retry counts;
- exception details;
- software/model versions;
- checksums;
- token usage and estimated cost;
- completion marker.

Use immutable per-run output directories. Consolidate only after the run completes.

## 12.8 Security and governance

- Load secrets only from approved environment or secret stores.
- Confirm `.env` is ignored.
- Never log API keys.
- Add a preflight check for whether a corpus may be sent to an external API.
- Define vendor retention and privacy settings.
- Redact or exclude personal/sensitive sentences.
- Record who authorised each production run.
- Establish maximum batch cost and a stop mechanism.
- Do not expose raw API responses publicly without licence and privacy review.

---

# 13. Methodological recommendations

## 13.1 Required before further data generation

1. **Define the actual corpus design.**
   - package, year, version and download date;
   - genre/domain;
   - token and sentence counts;
   - document/source structure;
   - deduplication;
   - licence and API-processing permission.

2. **Resolve the ARF issue.**
   - implement standard ARF or rename the custom measure;
   - justify the threshold empirically.

3. **Define the sampling claim.**
   - Current 15-lemma random samples are engineering tests.
   - Do not use them to characterise language-wide vocabulary behaviour.
   - Develop stratification by POS, frequency, dispersion, polysemy and register.

4. **Fix the unit of analysis.**
   - The current pipeline produces lemma and sentence evidence.
   - Do not call that concept- or sense-level data until a sense model exists.

5. **Redesign or rename Pass 2.**

6. **Rename automated Pass 3.**

7. **Add abstention and insufficient-evidence outcomes.**

8. **Predefine context policy.**
   - sentence only;
   - preceding/following sentence;
   - document metadata;
   - unavailable context.

9. **Record exact run provenance.**

## 13.2 Required before expert review

1. Freeze a taxonomy release.
2. Publish taxonomy definitions and multilingual examples.
3. Run a small calibration exercise in all five languages.
4. Define the review unit and workload.
5. Decide whether multiple functions are allowed.
6. Define insufficient-context and no-fit decisions.
7. Publish a fixed review schema.
8. Train reviewers on shared examples.
9. Use at least partial blind double coding.
10. Define disagreement and adjudication.
11. Measure:
    - raw agreement;
    - chance-corrected agreement where suitable;
    - category-specific agreement;
    - model-human agreement;
    - reviewer confidence;
    - taxonomy-gap rates.
12. Separate reviewer identity from public outputs.
13. State acknowledgement and authorship policy.

## 13.3 Required before CEFR-related claims

1. Do not infer CEFR level directly from sentence function frequency.
2. Define the evidential bridge between:
   - corpus occurrence;
   - communicative usefulness;
   - learner comprehension;
   - learner production;
   - CEFR descriptor interpretation.
3. Validate against relevant Reference Level Descriptions.
4. Include learner-corpus or assessment evidence where permitted.
5. Establish receptive/productive criteria by language.
6. Use language-specific expert panels.
7. Validate concept/sense alignment independently of CEFR assignment.
8. Conduct cross-language adjudication.
9. Obtain external methodological review.
10. Publish uncertainty and limitations.
11. Require formal publication approval.

## 13.4 Useful future research

- Compare spaCy, Stanza and UDPipe outputs.
- Study model-version sensitivity.
- Compare independent versus informed Pass 2.
- Calibrate confidence against expert decisions.
- Test sentence-only versus contextual classification.
- Study multilabel function annotation.
- Analyse taxonomy overlap empirically.
- Develop MWE and construction extraction.
- Investigate German compounds and Czech morphology separately.
- Evaluate active-learning approaches for review prioritisation.
- Compare model-assisted and fully human double coding.
- Study how function distributions relate—or fail to relate—to learner-level evidence.

## 13.5 Recommended evidence-status framework

Use separate status dimensions.

### Processing status

`raw → processed → sampled → model_generated → automated_qa_passed`

### Human-review status

`not_reviewed → single_reviewed → double_reviewed → adjudication_required → adjudicated`

### Validation status

`not_validated → corpus_validated → cross_language_validated → cefr_evidence_validated → externally_validated`

### Release status

`internal → release_candidate → approved_for_publication → published → superseded`

“Tier 4 candidate material” should either be fully defined within this framework or removed.

---

# 14. Missing-content register

| Required addition | Why necessary | Minimum contents |
|---|---|---|
| Current-status dashboard | Distinguishes plans from completed work | Stage × language × status; date; owner; next milestone |
| Roadmap | Explains what happens next | Dependencies, dates or sequence, deliverables |
| Roles and responsibilities | Removes hidden ownership | Responsible, accountable, consulted and informed roles |
| Glossary | Controls blurred terminology | Concept, sense, lemma, lexeme, function, CEFR level, validation |
| Corpus register | Enables provenance and comparison | Source, date, version, size, genre, licence, restrictions |
| Data dictionary | Makes schemas usable | Field, type, definition, allowed values, status |
| File/folder map | Prevents navigation errors | GitHub and Drive locations with examples |
| Access guide | Makes participation possible | Permission route, accounts, owner, expected response |
| Reviewer handbook | Enables independent review | Workload, decisions, examples, submission |
| Troubleshooting guide | Supports mixed technical confidence | Setup, Drive, Colab, API and common errors |
| Model/prompt register | Controls model drift | Version, date, model, prompt hash, purpose |
| Taxonomy release notes | Makes “CEFR-derived” auditable | Source map, changes, known overlaps, validation |
| Data-release register | Makes outputs discoverable | Version, status, licence, DOI/citation, superseded flag |
| Decision log | Records project-lead decisions | Date, decision, rationale, owner |
| Change log | Makes drift visible | Website, code, schema, taxonomy and methodology changes |
| Governance statement | Controls claims and responsibilities | Status gates, approval, privacy, external API use |
| Validation protocol | Supports defensible claims | Human review, agreement, corpus and external validation |
| Licence and permitted-use page | Enables lawful reuse | Code, docs, taxonomy, samples and outputs |
| Citation guidance | Supports external researchers | Preferred citation, version and release identifier |
| Contribution guide | Supports technical participation | Branching, issues, tests, pull requests |
| Issue-reporting routes | Makes support operational | Technical, access, review and governance contacts |

---

# 15. Source-of-truth model

| Topic | Recommended authoritative location | Website treatment |
|---|---|---|
| Methodology | `methodology/methodology.md` plus versioned releases | Generated summary, not independently edited |
| Workflow | `spec/workflow.yaml` or `docs_project/workflow.md` | Diagram and stage pages generated from source |
| Prompts | `prompts/{pass}/{version}.txt` | Exact text generated with hash and commit |
| Taxonomy | `taxonomy/releases/{version}/` | Download and human-readable browser |
| Model settings | Immutable `runs/{run_id}/run_config.yaml` | Current approved defaults displayed |
| Schemas | `schemas/` in JSON Schema/Pandera | Data-dictionary pages generated |
| Reviewer guidance | `review/reviewer_handbook.md` | Reviewer start page generated from handbook |
| Current status | `status/status.yaml` | Homepage and dashboard generated |
| Data releases | `releases/release_registry.csv` | Outputs page generated |
| Access instructions | Website page plus restricted operational contact record | Public instructions without exposing sensitive links |
| Corpus provenance | `governance/corpus_register.csv` | Public summary generated |
| Licences | Root licence files and `governance/licence_register.csv` | Permitted-use page generated |

## Drift control

1. Do not manually copy prompt text into HTML.
2. Generate website tables from machine-readable sources.
3. Fail CI when README commands refer to missing files.
4. Run link checking on every site build.
5. Validate schemas and taxonomy before merge.
6. Require every release to identify a full commit SHA.
7. Tag stable releases.
8. Mark superseded files visibly.
9. Keep public examples tied to a specific schema and taxonomy version.
10. Assign one owner for each source of truth.

---

# 16. Prioritised implementation plan

## Phase A — before the SIG presentation

| Action | Owner/expertise | Page/file | Dependency | Effort | Objective completion criterion |
|---|---|---|---|---:|---|
| Correct all script names and paths | Technical maintainer | README, Stage 4, technical page | Current tree | Small | Every documented path exists |
| Add public no-API quickstart | Python maintainer | README, `sample_data/` | Fixture creation | Medium | Fresh user can complete validation without API |
| Add implemented/planned/status table | Project lead | Homepage, workflow | Owner confirmations | Small | Every stage labelled with dated status |
| Rename Pass 2 or redesign claim | Methodology + technical lead | Site and `05b` | Project decision | Small for rename | No public page calls informed validation blind |
| Rename automated Pass 3 | Methodology + technical lead | Site and `05c` | Project decision | Small | “Adjudication” reserved for human process |
| Correct ARF terminology | Corpus methodologist | Stage 2/3, script docs | Formula decision | Medium | One name and formula used everywhere |
| Publish Data and Access page | Project coordinator | New page | Drive owner/access route | Medium | Member can request access without private explanation |
| Publish Reviewer Start page | Review coordinator | New page | Workbook schema decision | Medium | Reviewer can start and submit independently |
| Define Tier 4/status terms | Governance lead | Homepage/governance | Status decision | Small | Every status has definition and permitted claim |
| Add build SHA/date | Web maintainer | Footer/build | Site build process | Small | Every page shows full source SHA |
| Check all internal and critical external links | Web maintainer | Entire site | Updated links | Small | Automated link report passes |
| Add named support routes | Project lead | Contact/footer | Role assignment | Small | Access, review and technical contacts exist |

## Phase B — before the next full processing run

| Action | Owner/expertise | Page/file | Dependency | Effort | Completion criterion |
|---|---|---|---|---:|---|
| Create corpus manifest | Corpus leads per language | Governance/Drive | Licence review | Medium | Every corpus has source/version/size/licence |
| Implement standard ARF or rename measure | Corpus statistician | `03_compute_lemma_stats.py` | Method decision | Medium | Tested formula and documentation |
| Build unified config loader | Python maintainer | All scripts | Config schema | Medium | Every stage reads one validated config |
| Add run manifest | Reproducibility lead | All scripts | Config loader | Medium | Every output links to complete run record |
| Pin environment and NLP models | Technical maintainer | Lockfile/README | Model selection | Medium | Clean install reproduces versions |
| Fix `.env` loading | Python maintainer | Utility and README | None | Small | Safe key-presence test passes |
| Redesign Pass 2 independence | LLM methodologist | `05b` | Protocol decision | Medium | Pass 2 inputs match declared design |
| Add abstention/multilabel policy | Taxonomy + LLM leads | Taxonomy/schemas/prompts | Taxonomy review | Medium | Schemas support agreed outcomes |
| Add API mocks and unit tests | QA engineer | `tests/` | Fixtures | Medium | CI passes without paid calls |
| Add atomic checkpoints | Data engineer | LLM scripts | Run manifest | Medium | Interruption test resumes without duplicates |
| Enforce one-to-one merges | Python maintainer | `06` | Schema IDs | Small | Duplicate fixture fails loudly |
| Implement QA and workbook scripts | Data/review engineer | New Stage 7–10 scripts | Review schema | Large | Public fixture reaches a review workbook |
| Record token/cost usage | Technical maintainer | API utility | API response handling | Small | Per-run usage report produced |
| Produce language NLP QA report | Language NLP specialists | Stage 2 | Gold fixtures | Large | Error profile exists for all five languages |

## Phase C — before publication or external release

| Action | Owner/expertise | Location | Dependency | Effort | Completion criterion |
|---|---|---|---|---:|---|
| Complete expert double review | Review leads | Review system | Reviewer protocol | Large | Defined coverage and agreement targets met |
| Conduct human adjudication | Expert panel | Adjudication records | Double review | Large | All release rows resolved or explicitly uncertain |
| Validate taxonomy | CEFR/function specialists | Taxonomy report | Reviewed data | Large | Boundaries and gaps evaluated |
| Validate concept/sense model | Lexical semantics leads | Concept dataset | Concept schema | Large | Sense alignment independently reviewed |
| Conduct cross-language validation | Five language panels | Validation report | Language reviews | Large | Divergence decisions documented |
| Validate CEFR-related claims | Assessment researchers | Validation report | Learner/RLD evidence | Large | Claims supported by published protocol |
| Resolve licences and permitted use | Governance/legal support | Licence register | Corpus/output inventory | Medium | Every release artefact has a licence |
| External methodological review | Independent experts | Review report | Internal validation | Medium | Responses to external findings recorded |
| Create tagged release and citation | Maintainer/project lead | GitHub/release page | Approval | Small | Release has tag, SHA, licence and citation |
| Formal publication approval | Project governance | Release record | All prior gates | Medium | Signed approval and scope statement exist |

---

# 17. Presentation-readiness checklist

## Project identity and scope

- [ ] The homepage states plainly what the pilot is.
- [ ] The five languages are visible immediately.
- [ ] Implemented, planned and unstarted components are separated.
- [ ] The intended outputs are listed.
- [ ] The limits of the pilot are explicit.

## Evidence status

- [ ] The provisional-output warning is prominent.
- [ ] “Tier 4” is defined or removed.
- [ ] `final` is not used for unreviewed model output.
- [ ] Automated resolution is not called human adjudication.
- [ ] No page implies that current output is validated CEFR data.

## Current status

- [ ] A dated stage-by-language dashboard exists.
- [ ] The next milestone is stated.
- [ ] Known blockers are stated.
- [ ] The website displays its source commit SHA.
- [ ] Last-updated dates are accurate.

## Technical accuracy

- [ ] Every README command uses a current filename.
- [ ] Every referenced input file exists or is clearly marked restricted.
- [ ] A public no-API smoke test is available.
- [ ] Local and Colab instructions are separate.
- [ ] Dependencies and NLP models are documented.
- [ ] `.env` handling is tested.
- [ ] The actual statistical measure is named accurately.
- [ ] The configuration source of truth is stated.

## Data and access

- [ ] GitHub, Drive and Colab roles are explained.
- [ ] Public and restricted resources are listed.
- [ ] An access-request route exists.
- [ ] The required account type is stated.
- [ ] A folder map is available.
- [ ] Master-file protection and review-copy rules are stated.
- [ ] Broken-link and access-support routes are visible.

## Reviewer readiness

- [ ] The reviewer task is clearly defined.
- [ ] Expected workload and item count are stated.
- [ ] Editable and protected columns are identified.
- [ ] Permitted decision values are fixed.
- [ ] Insufficient context and no-fit cases are supported.
- [ ] Multiple functions and senses are addressed.
- [ ] A complete worked example is available.
- [ ] Saving and submission instructions are explicit.
- [ ] Human adjudication is explained.
- [ ] Acknowledgement/authorship/data-use rules are stated.

## Methodology

- [ ] Corpus sources, dates, versions, sizes and genres are documented.
- [ ] Licensing and API-processing permissions are documented.
- [ ] The frequency/dispersion formula is published.
- [ ] The 15-lemma sample is labelled as an engineering pilot.
- [ ] Pass 2 is accurately described.
- [ ] Confidence is described as calibrated or uncalibrated.
- [ ] Taxonomy derivation and version are documented.
- [ ] The distinction between lemma, sense, concept and function is consistent.
- [ ] The connection to CEFR claims is presented as a validation question, not an established result.

## Governance and publication

- [ ] Roles and responsibilities are named.
- [ ] Review, adjudication, validation and approval are separate stages.
- [ ] Code, documentation, taxonomy and sample licences are explicit.
- [ ] A decision log and change log exist.
- [ ] Public outputs have release identifiers and citation guidance.
- [ ] The presentation states what the SIG is being asked to decide or contribute.

## Final presentation decision

- [ ] The site has been reviewed by one non-technical SIG member.
- [ ] The reviewer journey has been completed by a person who received no verbal instructions.
- [ ] The technical quickstart has been completed in a clean environment.
- [ ] All critical links have been checked.
- [ ] The presentation describes the project as a **prototype and methodological pilot**, unless later evidence justifies a stronger description.