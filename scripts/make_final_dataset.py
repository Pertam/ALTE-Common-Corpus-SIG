
import argparse
from pathlib import Path
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--pass2", required=True)
    parser.add_argument("--pass3", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    p1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    p2 = pd.read_csv(args.pass2, dtype=str).fillna("")

    final = p1.copy()
    final = final.rename(columns={
        "function_id": "pass1_function_id",
        "function_label": "pass1_function_label",
        "confidence": "pass1_confidence",
        "rationale": "pass1_rationale",
    })

    p2_small = p2.rename(columns={
        "function_id": "pass2_function_id",
        "function_label": "pass2_function_label",
        "confidence": "pass2_confidence",
        "validation_rationale": "pass2_rationale",
    })[
        ["row_id", "pass2_function_id", "pass2_function_label", "pass2_confidence", "validator_decision", "pass2_rationale", "requires_review"]
    ]

    final = final.merge(p2_small, on="row_id", how="left")

    final["final_function_id"] = final["pass2_function_id"]
    final["final_function_label"] = final["pass2_function_label"]
    final["final_confidence"] = final["pass2_confidence"]
    final["final_source"] = "pass2"

    if args.pass3 and Path(args.pass3).exists() and Path(args.pass3).stat().st_size > 0:
        p3 = pd.read_csv(args.pass3, dtype=str).fillna("")
        p3_small = p3[["row_id", "final_function_id", "final_function_label", "final_confidence", "adjudication_rationale", "human_review_recommended"]]
        final = final.merge(p3_small, on="row_id", how="left", suffixes=("", "_p3"))

        mask = final["final_function_id_p3"].fillna("") != ""
        final.loc[mask, "final_function_id"] = final.loc[mask, "final_function_id_p3"]
        final.loc[mask, "final_function_label"] = final.loc[mask, "final_function_label_p3"]
        final.loc[mask, "final_confidence"] = final.loc[mask, "final_confidence_p3"]
        final.loc[mask, "final_source"] = "pass3"

        drop_cols = [c for c in final.columns if c.endswith("_p3")]
        final = final.drop(columns=drop_cols)

    final.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Saved final dataset to {args.output}")

if __name__ == "__main__":
    main()
