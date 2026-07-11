#!/usr/bin/env python3
"""Stage 06: combine sampled rows, lexical senses and sentence functions."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def read(path: str, label: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists(): raise FileNotFoundError(f"{label} not found: {source}")
    return pd.read_csv(source, dtype=str).fillna("")


def require(df: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [x for x in columns if x not in df.columns]
    if missing: raise ValueError(f"{label} missing columns: {missing}")


def merge_family(base, p1, p2, p3, family, id_col, label_col):
    required = ["row_id", id_col, label_col, "confidence", "rationale", "requires_review"]
    require(p1, required, f"{family} Pass 1"); require(p2, required, f"{family} Pass 2")
    def slim(df, prefix):
        return df[required].rename(columns={x:f"{prefix}_{x}" for x in required if x != "row_id"})
    result = base.merge(slim(p1, f"{family}_pass1"), on="row_id", how="left").merge(slim(p2, f"{family}_pass2"), on="row_id", how="left")
    result[f"final_{family}_id"] = result[f"{family}_pass2_{id_col}"].where(result[f"{family}_pass2_{id_col}"] != "", result[f"{family}_pass1_{id_col}"])
    result[f"final_{family}_label"] = result[f"{family}_pass2_{label_col}"].where(result[f"{family}_pass2_{label_col}"] != "", result[f"{family}_pass1_{label_col}"])
    result[f"final_{family}_confidence"] = result[f"{family}_pass2_confidence"].where(result[f"{family}_pass2_confidence"] != "", result[f"{family}_pass1_confidence"])
    result[f"final_{family}_source"] = "pass2"
    result[f"{family}_human_review_recommended"] = ((result[f"{family}_pass1_{id_col}"] != result[f"{family}_pass2_{id_col}"]) | (result[f"{family}_pass1_confidence"] == "low") | (result[f"{family}_pass2_confidence"] == "low"))
    if p3 is not None and not p3.empty:
        p3_id, p3_label = f"final_{family}_id", f"final_{family}_{'sense_gloss' if family == 'sense' else 'function_label'}"
        if p3_label not in p3.columns: p3_label = f"final_{family}_label"
        require(p3, ["row_id", p3_id, p3_label, f"final_{family}_confidence", "human_review_recommended"], f"{family} Pass 3")
        extra = p3[["row_id", p3_id, p3_label, f"final_{family}_confidence", "human_review_recommended"]].rename(columns={p3_id:"_id", p3_label:"_label", f"final_{family}_confidence":"_confidence", "human_review_recommended":"_review"})
        result = result.merge(extra, on="row_id", how="left"); has = result["_id"] != ""
        result.loc[has, f"final_{family}_id"] = result.loc[has, "_id"]; result.loc[has, f"final_{family}_label"] = result.loc[has, "_label"]
        result.loc[has, f"final_{family}_confidence"] = result.loc[has, "_confidence"]; result.loc[has, f"{family}_human_review_recommended"] = result.loc[has, "_review"].str.lower().isin(["true","1","yes"])
        result.loc[has, f"final_{family}_source"] = "pass3"; result = result.drop(columns=["_id","_label","_confidence","_review"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build combined sense-and-function review dataset.")
    parser.add_argument("--samples", required=True); parser.add_argument("--sense_pass1", required=True); parser.add_argument("--sense_pass2", required=True); parser.add_argument("--sense_pass3")
    parser.add_argument("--function_pass1", "--pass1", dest="function_pass1", required=True); parser.add_argument("--function_pass2", "--pass2", dest="function_pass2", required=True); parser.add_argument("--function_pass3", "--pass3", dest="function_pass3")
    parser.add_argument("--output", required=True); args = parser.parse_args()
    base = read(args.samples, "Samples"); require(base, ["row_id", "sentence"], "Samples")
    final = merge_family(base, read(args.sense_pass1,"Sense Pass 1"), read(args.sense_pass2,"Sense Pass 2"), read(args.sense_pass3,"Sense Pass 3") if args.sense_pass3 else None, "sense", "sense_id", "sense_gloss")
    final = merge_family(final, read(args.function_pass1,"Function Pass 1"), read(args.function_pass2,"Function Pass 2"), read(args.function_pass3,"Function Pass 3") if args.function_pass3 else None, "function", "function_id", "function_label")
    final["provenance_tier"] = 4
    final["review_status"] = (final["sense_human_review_recommended"].astype(bool) | final["function_human_review_recommended"].astype(bool)).map({True:"review_required", False:"provisional"})
    for column in ["expert_sense_decision","expert_sense_id","expert_sense_comment","expert_function_decision","expert_function_id","expert_function_comment","adjudication_required"]: final[column] = ""
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True); final.to_csv(output, index=False)
    print(f"Combined rows: {len(final):,} | Output: {output}")

if __name__ == "__main__": main()
