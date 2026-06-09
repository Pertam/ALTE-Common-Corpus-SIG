from pathlib import Path
import pandas as pd

REQUIRED_TAXONOMY_COLUMNS = {
    "top_level_label", "subcategory_id", "subcategory_label",
    "function_id", "function_label", "definition",
    "cefr_function_level_min_provisional", "cefr_function_level_core_provisional"
}

REQUIRED_SENTENCE_COLUMNS = {
    "language_code", "language", "lemma", "pos", "raw_frequency",
    "frequency_per_million", "sentence_count", "arf_per_million",
    "sentence_id", "sentence_uid", "sentence"
}

def validate_csv(path: Path, required_cols: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {sorted(missing)}")
    return df

if __name__ == "__main__":
    taxonomy_path = Path("data/processed/cefr_function_taxonomy.csv")
    sample_path = Path("data/processed/stage5_sample_sentences.csv")
    taxonomy = validate_csv(taxonomy_path, REQUIRED_TAXONOMY_COLUMNS)
    sample = validate_csv(sample_path, REQUIRED_SENTENCE_COLUMNS)
    if taxonomy["function_id"].duplicated().any():
        dupes = taxonomy.loc[taxonomy["function_id"].duplicated(), "function_id"].tolist()
        raise ValueError(f"Duplicate function IDs found: {dupes[:10]}")
    if sample["sentence_uid"].duplicated().any():
        raise ValueError("sentence_uid must be unique in the sample file")
    print(f"OK: taxonomy rows={len(taxonomy):,}; sample rows={len(sample):,}")
