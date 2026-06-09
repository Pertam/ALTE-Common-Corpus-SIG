"""Pass 3: aggregate sentence-level function tags into lemma-level functional profiles.
No extra LLM is required here; this creates transparent numeric profiles for expert review.
"""
from pathlib import Path
import argparse
import pandas as pd


def run(input_csv: Path, taxonomy_csv: Path, output_csv: Path) -> None:
    df = pd.read_csv(input_csv)
    taxonomy = pd.read_csv(taxonomy_csv)[[
        "function_id", "function_label", "top_level_label", "subcategory_id", "subcategory_label",
        "cefr_function_level_min_provisional", "cefr_function_level_core_provisional"
    ]].drop_duplicates("function_id")
    if "final_function_id" not in df.columns:
        raise ValueError("Pass 2 input must include final_function_id")
    group_cols = ["language_code", "lemma", "pos", "final_function_id"]
    counts = (df.groupby(group_cols, as_index=False)
              .agg(sentence_n=("sentence_uid", "nunique"),
                   mean_confidence=("confidence", "mean"),
                   review_required_n=("review_status", lambda s: (s == "review_required").sum())))
    totals = counts.groupby(["language_code", "lemma", "pos"], as_index=False)["sentence_n"].sum().rename(columns={"sentence_n": "lemma_sentence_n"})
    prof = counts.merge(totals, on=["language_code", "lemma", "pos"], how="left")
    prof["function_share"] = prof["sentence_n"] / prof["lemma_sentence_n"]
    prof = prof.merge(taxonomy, left_on="final_function_id", right_on="function_id", how="left")
    prof = prof.sort_values(["language_code", "lemma", "pos", "function_share"], ascending=[True, True, True, False])
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    prof.to_csv(output_csv, index=False)
    print(f"Saved lemma profiles to {output_csv}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(Path(args.input), Path(args.taxonomy), Path(args.output))
