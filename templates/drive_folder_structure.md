# Recommended Google Drive folder structure

```text
ALTE-Common-Corpus-SIG/
  data/
    raw/
      en/
      fr/
      es/
      de/
      cs/
    interim/
    processed/
    outputs/
      en/
        sense_inventory/
        pass1/
        pass2_informed/
        pass2_blind/
        adjudication/
      fr/
      es/
      de/
      cs/
  logs/
  review/
    informed/
    blind_validation/
    expert_decisions/
  exports/
  archive/
  secrets/
```

GitHub should hold code, taxonomy, configuration, prompts and small examples.

Drive or institutional storage should hold raw data, processed corpus outputs, model outputs, logs, review workbooks and bulky files.

Blind-validation and informed-review outputs must be stored separately because the review condition is part of the provenance. API keys must remain in protected secrets or environment variables and must never be committed to GitHub.
