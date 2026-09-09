#!/usr/bin/env python3
"""Stage 06: combine sampled rows, lexical senses and sentence functions.

This file is a generated review view, not the durable store of human decisions.
Use --expert_decisions to join a separately maintained reviewer-decision file.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

EXPERT_COLUMNS = [
    "expert_sense_decision", "expert_sense_id", "expert_sense_comment",
    "expert_function_decision", "expert_function_id", "expert_function_comment",
    "adjudication_required",
]


def read(path: str, label: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"{label} not found: {source}")
    return pd.read_csv(source, dtype=str).fillna("")


def require(df: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [x for x in columns if x not in df.columns]
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")


def bool_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"])


def assert_unique_rows(df: pd.DataFrame, label: str) -> None:
    require(df, ["row_id"], label)
    if df["row_id"].astype(str).str.strip().eq("").any():
        raise ValueError(f"{label} contains blank row_id values.")
    if df["row_id"].duplicated().any():
        dupes = df.loc[df["row_id"].duplicated(), "row_id"].head(20).tolist()
        raise ValueError(f"{label} contains duplicate row_id values: {dupes}")


def merge_family(base, p1, p2, p3, family, id_col, label_col):
    required = ["row_id", id_col, label_col, "confidence", "rationale", "requires_review"]
    require(p1, required, f"{family} Pass 1")
    require(p2, required, f"{family} Pass 2")
    assert_unique_rows(p1, f"{family} Pass 1")
    assert_unique_rows(p2, f"{family} Pass 2")

    def slim(df: pd.DataFrame, prefix: str, extra: list[str] | None = None) -> pd.DataFrame:
        keep = list(required)
        for column in extra or []:
            if column in df.columns and column not in keep:
                keep.append(column)
        return df[keep].rename(columns={x: f"{prefix}_{x}" for x in keep if x != "row_id"})

    p2_extra = ["validator_decision", "interaction_note", "review_mode"]
    result = base.merge(slim(p1, f"{family}_pass1"), on="row_id", how="left", validate="one_to_one")
    result = result.merge(slim(p2, f"{family}_pass2", p2_extra), on="row_id", how="left", validate="one_to_one")

    p1_id = result[f"{family}_pass1_{id_col}"].fillna("")
    p2_id = result[f"{family}_pass2_{id_col}"].fillna("")
    p1_label = result[f"{family}_pass1_{label_col}"].fillna("")
    p2_label = result[f"{family}_pass2_{label_col}"].fillna("")
    p1_conf = result[f"{family}_pass1_confidence"].fillna("")
    p2_conf = result[f"{family}_pass2_confidence"].fillna("")

    has_p2 = p2_id.astype(str).str.strip().ne("")
    result[f"final_{family}_id"] = p2_id.where(has_p2, p1_id)
    result[f"final_{family}_label"] = p2_label.where(has_p2, p1_label)
    result[f"final_{family}_confidence"] = p2_conf.where(has_p2, p1_conf)
    result[f"final_{family}_source"] = has_p2.map({True: "pass2", False: "pass1"})

    review = (
        (p1_id != p2_id) & has_p2
        | p1_conf.eq("low")
        | p2_conf.eq("low")
        | bool_series(result[f"{family}_pass1_requires_review"])
        | bool_series(result[f"{family}_pass2_requires_review"])
    )
    validator_col = f"{family}_pass2_validator_decision"
    if validator_col in result.columns:
        validator = result[validator_col].fillna("").astype(str).str.strip().str.lower()
        review = review | (validator.ne("") & validator.ne("accept"))
    result[f"{family}_human_review_recommended"] = review.astype(bool)

    if p3 is not None and not p3.empty:
        assert_unique_rows(p3, f"{family} Pass 3")
        p3_id = f"final_{family}_id"
        p3_label = "final_sense_gloss" if family == "sense" else "final_function_label"
        p3_conf = f"final_{family}_confidence"
        require(p3, ["row_id", p3_id, p3_label, p3_conf, "human_review_recommended"], f"{family} Pass 3")
        extra = p3[["row_id", p3_id, p3_label, p3_conf, "human_review_recommended"]].rename(
            columns={p3_id: "_id", p3_label: "_label", p3_conf: "_confidence", "human_review_recommended": "_review"}
        )
        result = result.merge(extra, on="row_id", how="left", validate="one_to_one")
        has = result["_id"].notna() & result["_id"].astype(str).str.strip().ne("")
        result.loc[has, f"final_{family}_id"] = result.loc[has, "_id"]
        result.loc[has, f"final_{family}_label"] = result.loc[has, "_label"]
        result.loc[has, f"final_{family}_confidence"] = result.loc[has, "_confidence"]
        p3_review = bool_series(result["_review"])
        result.loc[has, f"{family}_human_review_recommended"] = (
            result.loc[has, f"{family}_human_review_recommended"].astype(bool) | p3_review.loc[has]
        )
        result.loc[has, f"final_{family}_source"] = "pass3"
        result = result.drop(columns=["_id", "_label", "_confidence", "_review"])
    return result


def merge_expert_decisions(final: pd.DataFrame, path: str | None) -> pd.DataFrame:
    if not path:
        for column in EXPERT_COLUMNS:
            final[column] = ""
        return final

    expert = read(path, "Expert decisions")
    assert_unique_rows(expert, "Expert decisions")
    keep = ["row_id"] + [c for c in EXPERT_COLUMNS if c in expert.columns]
    if len(keep) == 1:
        raise ValueError(f"Expert decisions file must contain at least one of: {EXPERT_COLUMNS}")
    result = final.merge(expert[keep], on="row_id", how="left", validate="one_to_one")
    for column in EXPERT_COLUMNS:
        if column not in result.columns:
            result[column] = ""
        else:
            result[column] = result[column].fillna("")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build combined sense-and-function review dataset.")
    parser.add_argument("--samples", required=True)
    parser.add_argument("--sense_pass1", required=True); parser.add_argument("--sense_pass2", required=True); parser.add_argument("--sense_pass3")
    parser.add_argument("--function_pass1", "--pass1", dest="function_pass1", required=True)
    parser.add_argument("--function_pass2", "--pass2", dest="function_pass2", required=True)
    parser.add_argument("--function_pass3", "--pass3", dest="function_pass3")
    parser.add_argument("--expert_decisions", help="Separate durable human-decision CSV keyed by row_id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    base = read(args.samples, "Samples")
    require(base, ["row_id", "sentence"], "Samples")
    assert_unique_rows(base, "Samples")
    if "observation_id" in base.columns and not (base["row_id"].astype(str) == base["observation_id"].astype(str)).all():
        raise ValueError("Samples row_id must match observation_id under the current data contract.")

    final = merge_family(
        base,
        read(args.sense_pass1, "Sense Pass 1"),
        read(args.sense_pass2, "Sense Pass 2"),
        read(args.sense_pass3, "Sense Pass 3") if args.sense_pass3 else None,
        "sense", "sense_id", "sense_gloss",
    )
    final = merge_family(
        final,
        read(args.function_pass1, "Function Pass 1"),
        read(args.function_pass2, "Function Pass 2"),
        read(args.function_pass3, "Function Pass 3") if args.function_pass3 else None,
        "function", "function_id", "function_label",
    )

    final["cefr_source"] = "llm_judgment"
    final["provenance_tier"] = 4
    final["review_status"] = (
        final["sense_human_review_recommended"].astype(bool)
        | final["function_human_review_recommended"].astype(bool)
    ).map({True: "review_required", False: "provisional"})
    final = merge_expert_decisions(final, args.expert_decisions)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output, index=False, encoding="utf-8")
    print(f"Combined rows: {len(final):,} | Output: {output}")
    if not args.expert_decisions:
        print("NOTE: expert columns are blank placeholders. Keep durable human decisions in a separate file and pass --expert_decisions on regeneration.")


if __name__ == "__main__":
    main()
