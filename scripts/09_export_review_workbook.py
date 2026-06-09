"""Export a human-readable Excel workbook for SIG review.
Uses pandas + xlsxwriter; formulas are avoided so the file is simple and portable.
"""
from pathlib import Path
import argparse
import pandas as pd


def run(pass2_csv: Path, profile_csv: Path, qa_dir: Path, output_xlsx: Path) -> None:
    pass2 = pd.read_csv(pass2_csv)
    profiles = pd.read_csv(profile_csv)
    qa_summary = pd.read_csv(qa_dir / "qa_summary.csv") if (qa_dir / "qa_summary.csv").exists() else pd.DataFrame()
    overall = pd.read_csv(qa_dir / "function_distribution_overall.csv") if (qa_dir / "function_distribution_overall.csv").exists() else pd.DataFrame()
    output_xlsx.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
        qa_summary.to_excel(writer, sheet_name="QA summary", index=False)
        profiles.to_excel(writer, sheet_name="Lemma profiles", index=False)
        overall.to_excel(writer, sheet_name="Overall functions", index=False)
        cols = [c for c in ["row_id", "language_code", "lemma", "pos", "sentence", "function_id", "function_label", "final_function_id", "final_function_label", "pass2_decision", "confidence", "review_status", "validation_rationale"] if c in pass2.columns]
        pass2[cols].to_excel(writer, sheet_name="Sentence review", index=False)
        for sheet in writer.sheets.values():
            sheet.freeze_panes(1, 0)
            sheet.autofilter(0, 0, 0, 20)
            sheet.set_column(0, 20, 18)
            sheet.set_column(4, 4, 70)
            sheet.set_column(12, 12, 60)
    print(f"Saved workbook to {output_xlsx}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pass2", required=True)
    p.add_argument("--profiles", required=True)
    p.add_argument("--qa_dir", default="data/outputs/qa")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(Path(args.pass2), Path(args.profiles), Path(args.qa_dir), Path(args.output))
