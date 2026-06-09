"""Quality checks for Stage 5 function-tagging outputs."""
from pathlib import Path
import argparse
import pandas as pd


def run(pass1: Path, pass2: Path, taxonomy: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    p1 = pd.read_csv(pass1)
    p2 = pd.read_csv(pass2)
    tax = pd.read_csv(taxonomy)
    valid = set(tax["function_id"])
    checks = []
    checks.append({"check": "pass1_rows", "value": len(p1)})
    checks.append({"check": "pass2_rows", "value": len(p2)})
    checks.append({"check": "pass1_invalid_function_ids", "value": len(set(p1["function_id"]) - valid)})
    checks.append({"check": "pass2_invalid_function_ids", "value": len(set(p2["final_function_id"]) - valid)})
    checks.append({"check": "pass2_review_required_rows", "value": int((p2["review_status"] == "review_required").sum())})
    checks.append({"check": "pass2_replacement_rows", "value": int((p2["pass2_decision"] == "replace_pass1").sum())})
    pd.DataFrame(checks).to_csv(output_dir / "qa_summary.csv", index=False)
    p2.groupby(["language_code", "lemma", "pos", "final_function_id", "final_function_label"], as_index=False).size().rename(columns={"size": "sentence_n"}).to_csv(output_dir / "function_distribution_by_lemma.csv", index=False)
    p2.groupby(["final_function_id", "final_function_label"], as_index=False).size().rename(columns={"size": "sentence_n"}).sort_values("sentence_n", ascending=False).to_csv(output_dir / "function_distribution_overall.csv", index=False)
    print(f"Saved QA reports to {output_dir}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pass1", required=True)
    p.add_argument("--pass2", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--output_dir", default="data/outputs/qa")
    args = p.parse_args()
    run(Path(args.pass1), Path(args.pass2), Path(args.taxonomy), Path(args.output_dir))
