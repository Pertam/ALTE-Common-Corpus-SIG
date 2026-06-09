#!/usr/bin/env python3
"""Stage 06: merge sampled sentences, Pass 1, Pass 2 and optional Pass 3.

The final output is still provisional candidate material for expert review. It is
not validated CEFR vocabulary data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def read_csv(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{label} file not found: {path}")
    return pd.read_csv(path, dtype=str).fillna("")


def require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build final merged sentence-level function dataset.")
    parser.add_argument("--samples", help="Original sampled sentence CSV from Stage 04. Recommended.")
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--pass2", required=True)
    parser.add_argument("--pass3", help="Optional Pass 3 CSV")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    p1 = read_csv(Path(args.pass1), "Pass 1")
    p2 = read_csv(Path(args.pass2), "Pass 2")
    require_columns(p1, ["row_id", "sentence", "function_id", "function_label", "confidence", "rationale"], "Pass 1")
    require_columns(p2, ["row_id", "function_id", "function_label", "confidence", "validator_decision", "validation_rationale", "requires_review"], "Pass 2")

    if args.samples:
        base = read_csv(Path(args.samples), "Samples")
        require_columns(base, ["sentence"], "Samples")
        if "row_id" not in base.columns:
            base.insert(0, "row_id", [f"row_{i + 1:06d}" for i in range(len(base))])
            print("WARNING: samples had no row_id column; generated row_000001-style IDs to match Pass 1 if needed.")
    else:
        base = p1[["row_id", "sentence"]].copy()

    p1_small = p1.rename(
        columns={
            "top_level_label": "pass1_top_level_label",
            "subcategory_id": "pass1_subcategory_id",
            "subcategory_label": "pass1_subcategory_label",
            "function_id": "pass1_function_id",
            "function_label": "pass1_function_label",
            "confidence": "pass1_confidence",
            "rationale": "pass1_rationale",
            "alternative_function_id": "pass1_alternative_function_id",
            "ambiguity_note": "pass1_ambiguity_note",
            "requires_review": "pass1_requires_review",
        }
    )[
        [
            "row_id",
            "pass1_top_level_label",
            "pass1_subcategory_id",
            "pass1_subcategory_label",
            "pass1_function_id",
            "pass1_function_label",
            "pass1_confidence",
            "pass1_rationale",
            "pass1_alternative_function_id",
            "pass1_ambiguity_note",
            "pass1_requires_review",
        ]
    ]

    p2_small = p2.rename(
        columns={
            "function_id": "pass2_function_id",
            "function_label": "pass2_function_label",
            "confidence": "pass2_confidence",
            "validation_rationale": "pass2_rationale",
            "requires_review": "pass2_requires_review",
        }
    )[
        [
            "row_id",
            "validator_decision",
            "pass2_function_id",
            "pass2_function_label",
            "pass2_confidence",
            "pass2_rationale",
            "pass2_requires_review",
        ]
    ].copy()

    final = base.merge(p1_small, on="row_id", how="left").merge(p2_small, on="row_id", how="left")

    final["final_function_id"] = final["pass2_function_id"]
    final["final_function_label"] = final["pass2_function_label"]
    final["final_confidence"] = final["pass2_confidence"]
    final["final_source"] = "pass2"
    final["adjudication_rationale"] = ""
    final["human_review_recommended"] = final.get("pass2_requires_review", "")

    if args.pass3 and Path(args.pass3).exists() and Path(args.pass3).stat().st_size > 0:
        p3 = read_csv(Path(args.pass3), "Pass 3")
        require_columns(
            p3,
            [
                "row_id",
                "final_function_id",
                "final_function_label",
                "final_confidence",
                "adjudication_rationale",
                "human_review_recommended",
            ],
            "Pass 3",
        )
        p3_small = p3[
            [
                "row_id",
                "final_function_id",
                "final_function_label",
                "final_confidence",
                "adjudication_rationale",
                "human_review_recommended",
            ]
        ].rename(
            columns={
                "final_function_id": "p3_final_function_id",
                "final_function_label": "p3_final_function_label",
                "final_confidence": "p3_final_confidence",
                "adjudication_rationale": "p3_adjudication_rationale",
                "human_review_recommended": "p3_human_review_recommended",
            }
        )

        final = final.merge(p3_small, on="row_id", how="left")
        has_p3 = final["p3_final_function_id"].fillna("").astype(str).str.strip() != ""
        final.loc[has_p3, "final_function_id"] = final.loc[has_p3, "p3_final_function_id"]
        final.loc[has_p3, "final_function_label"] = final.loc[has_p3, "p3_final_function_label"]
        final.loc[has_p3, "final_confidence"] = final.loc[has_p3, "p3_final_confidence"]
        final.loc[has_p3, "adjudication_rationale"] = final.loc[has_p3, "p3_adjudication_rationale"]
        final.loc[has_p3, "human_review_recommended"] = final.loc[has_p3, "p3_human_review_recommended"]
        final.loc[has_p3, "final_source"] = "pass3"
        final = final.drop(columns=[c for c in final.columns if c.startswith("p3_")])

    final["cefr_source"] = "llm_judgment"
    final["provenance_tier"] = 4
    final["review_status"] = final["human_review_recommended"].astype(str).str.lower().map(
        {"true": "review_required", "1": "review_required", "yes": "review_required"}
    ).fillna("provisional")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Final rows: {len(final):,}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
