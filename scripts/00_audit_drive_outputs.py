#!/usr/bin/env python3
"""Read-only audit of the ALTE Common Corpus SIG Drive outputs.

The audit recognises the June 2026 function-only run as legacy data and checks
whether it can be safely reused by the current sense-aware workflow. It never
moves, renames, overwrites or deletes project data. Optional report paths create
new CSV/JSON audit files only.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

LANGUAGES = ("en", "fr", "es", "de", "cs")

SAMPLE_COLUMNS = {
    "row_id", "language_code", "language", "lemma", "pos", "sentence_id",
    "sentence_uid", "sentence", "source_id",
}
FUNCTION_PASS1_COLUMNS = {
    "row_id", "sentence", "function_id", "function_label", "confidence",
    "rationale", "requires_review",
}
LEGACY_PASS2_COLUMNS = {
    "row_id", "sentence", "pass1_function_id", "validator_decision",
    "function_id", "function_label", "confidence", "validation_rationale",
    "requires_review",
}
CURRENT_PASS2_COLUMNS = {
    "row_id", "sentence", "pass1_function_id", "pass1_sense_id",
    "validator_decision", "function_id", "function_label", "confidence",
    "rationale", "interaction_note", "requires_review", "review_mode",
}
LEGACY_PASS3_COLUMNS = {
    "row_id", "sentence", "pass1_function_id", "pass2_function_id",
    "final_function_id", "final_function_label", "final_confidence",
    "adjudication_rationale", "human_review_recommended",
}
SENSE_INVENTORY_COLUMNS = {
    "inventory_id", "language", "target_lemma", "target_pos", "sense_id",
    "sense_gloss", "inventory_status",
}
SENSE_PASS_COLUMNS = {
    "row_id", "sentence", "language", "target_lemma", "target_pos",
    "sense_id", "sense_gloss", "confidence", "rationale",
    "requires_review",
}


@dataclass
class Finding:
    section: str
    language: str
    item: str
    status: str
    message: str
    path: str


def add(findings: list[Finding], section: str, language: str, item: str,
        status: str, message: str, path: Path) -> None:
    findings.append(Finding(section, language, item, status, message, str(path)))


def csv_columns(path: Path) -> set[str]:
    return set(pd.read_csv(path, nrows=0, dtype=str, encoding="utf-8-sig").columns)


def csv_small_profile(path: Path) -> tuple[int, int, int]:
    frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    row_count = len(frame)
    unique_ids = frame["row_id"].nunique() if "row_id" in frame.columns else -1
    duplicate_ids = int(frame["row_id"].duplicated().sum()) if "row_id" in frame.columns else -1
    return row_count, unique_ids, duplicate_ids


def check_csv(findings: list[Finding], section: str, language: str, item: str,
              path: Path, required: Iterable[str], *, expected_rows: int | None = None,
              small_profile: bool = False, ok_status: str = "OK") -> set[str]:
    if not path.exists():
        add(findings, section, language, item, "MISSING", "file not found", path)
        return set()
    try:
        columns = csv_columns(path)
    except Exception as exc:  # pragma: no cover - environment dependent
        add(findings, section, language, item, "ERROR", f"cannot read CSV header: {exc}", path)
        return set()
    missing = sorted(set(required) - columns)
    if missing:
        add(findings, section, language, item, "ERROR", f"missing columns: {missing}", path)
        return columns
    detail = f"schema OK ({len(columns)} columns)"
    if small_profile:
        try:
            rows, unique_ids, duplicates = csv_small_profile(path)
            detail += f"; rows={rows}; unique_row_ids={unique_ids}; duplicate_row_ids={duplicates}"
            if expected_rows is not None and rows != expected_rows:
                add(findings, section, language, item, "WARNING", detail + f"; expected_rows={expected_rows}", path)
                return columns
            if duplicates > 0:
                add(findings, section, language, item, "WARNING", detail, path)
                return columns
        except Exception as exc:  # pragma: no cover
            add(findings, section, language, item, "WARNING", f"schema OK; profiling failed: {exc}", path)
            return columns
    add(findings, section, language, item, ok_status, detail, path)
    return columns


def check_exists(findings: list[Finding], section: str, language: str, item: str,
                 path: Path, *, status: str = "OK", message: str = "exists") -> None:
    add(findings, section, language, item, status if path.exists() else "MISSING",
        message if path.exists() else "not found", path)


def legacy_paths(root: Path, lang: str) -> dict[str, Path]:
    base = root / lang
    return {
        "raw": base / "stage00_raw_sentences" / f"{lang}_sentences.txt",
        "prepared": base / "stage01_prepared_sentences" / f"stage01_{lang}_sentences.parquet",
        "lemma_index": base / "stage02_tokenise_lemmatise" / f"{lang}_lemma_sentence_index.parquet",
        "token_parts": base / "stage02_tokenise_lemmatise" / "token_parts",
        "stats": base / "stage03_lemma_stats" / f"stage03_{lang}_lemma_frequencies.csv",
        "full_sample": base / "stage04_samples" / f"stage04_{lang}_random_15_lemmas_all_sentences.csv",
        "test50": base / "stage04_samples" / f"stage04_{lang}_dispersed_test50_normalised_for_stage05.csv",
        "function_pass1": base / "stage05_llm_tagging" / f"stage05_{lang}_pass1_dispersed_test50.csv",
        "function_pass2": base / "stage05_llm_tagging" / f"stage05_{lang}_pass2_dispersed_test50.csv",
        "function_pass3": base / "stage05_llm_tagging" / f"stage05_{lang}_pass3_dispersed_test50.csv",
        "legacy_final": base / "stage06_final_dataset" / f"stage06_{lang}_final_dispersed_test50.csv",
    }


def audit_taxonomy(findings: list[Finding], drive_root: Path, repo_root: Path) -> None:
    drive_taxonomy = drive_root / "taxonomy" / "cefr_function_taxonomy_v0_2.csv"
    repo_taxonomy = repo_root / "taxonomy" / "cefr_function_taxonomy_v0_2.csv"
    required = {"function_id", "function_label", "top_level_label", "subcategory_id", "subcategory_label"}
    drive_cols = check_csv(findings, "taxonomy", "all", "Drive taxonomy", drive_taxonomy, required)
    repo_cols = check_csv(findings, "taxonomy", "all", "GitHub taxonomy", repo_taxonomy, required)
    if drive_taxonomy.exists() and repo_taxonomy.exists() and drive_cols and repo_cols:
        drive = pd.read_csv(drive_taxonomy, dtype=str, encoding="utf-8-sig").fillna("")
        repo = pd.read_csv(repo_taxonomy, dtype=str, encoding="utf-8-sig").fillna("")
        drive_ids = set(drive["function_id"].astype(str))
        repo_ids = set(repo["function_id"].astype(str))
        if drive_ids == repo_ids:
            add(findings, "taxonomy", "all", "function inventory", "OK",
                f"matching function IDs ({len(drive_ids)})", drive_taxonomy)
        else:
            add(findings, "taxonomy", "all", "function inventory", "ERROR",
                f"Drive-only={len(drive_ids-repo_ids)}; GitHub-only={len(repo_ids-drive_ids)}", drive_taxonomy)
        if "function_guidance" in drive.columns and "function_guidance" not in repo.columns:
            add(findings, "taxonomy", "all", "function guidance", "WARNING",
                "Drive taxonomy has function_guidance but GitHub taxonomy does not; use Drive taxonomy until synced",
                drive_taxonomy)
        elif "function_guidance" in drive.columns and "function_guidance" in repo.columns:
            add(findings, "taxonomy", "all", "function guidance", "OK",
                "function_guidance present in both copies", drive_taxonomy)


def audit_legacy_language(findings: list[Finding], root: Path, lang: str) -> None:
    paths = legacy_paths(root, lang)
    check_exists(findings, "legacy", lang, "Stage 00 raw sentences", paths["raw"])
    check_exists(findings, "legacy", lang, "Stage 01 prepared parquet", paths["prepared"])
    check_exists(findings, "legacy", lang, "Stage 02 lemma index", paths["lemma_index"])
    check_exists(findings, "legacy", lang, "Stage 02 token parts", paths["token_parts"],
                 status="LEGACY_REUSABLE", message="chunked token output preserved; no combined token parquet required for reuse")
    check_csv(findings, "legacy", lang, "Stage 03 lemma statistics", paths["stats"],
              {"language_code", "lemma", "pos", "arf_per_million"}, ok_status="LEGACY_REUSABLE")
    check_csv(findings, "legacy", lang, "Stage 04 full sample", paths["full_sample"],
              SAMPLE_COLUMNS, ok_status="LEGACY_REUSABLE")
    check_csv(findings, "legacy", lang, "Stage 04 normalised test50", paths["test50"],
              SAMPLE_COLUMNS, expected_rows=50, small_profile=True, ok_status="LEGACY_REUSABLE")
    check_csv(findings, "legacy", lang, "Function Pass 1", paths["function_pass1"],
              FUNCTION_PASS1_COLUMNS, expected_rows=50, small_profile=True,
              ok_status="LEGACY_REUSABLE")
    p2_cols = check_csv(findings, "legacy", lang, "Function Pass 2", paths["function_pass2"],
                        {"row_id", "sentence", "function_id", "function_label", "confidence"},
                        expected_rows=50, small_profile=True, ok_status="LEGACY_REFERENCE_ONLY")
    if p2_cols:
        if CURRENT_PASS2_COLUMNS.issubset(p2_cols):
            add(findings, "legacy", lang, "Function Pass 2 schema", "CURRENT_COMPATIBLE",
                "current informed-review schema", paths["function_pass2"])
        elif LEGACY_PASS2_COLUMNS.issubset(p2_cols):
            add(findings, "legacy", lang, "Function Pass 2 schema", "LEGACY_REFERENCE_ONLY",
                "function-only validator output; retain for comparison but do not feed into the current combined builder",
                paths["function_pass2"])
        else:
            add(findings, "legacy", lang, "Function Pass 2 schema", "WARNING",
                "unrecognised Pass 2 variant", paths["function_pass2"])
    check_csv(findings, "legacy", lang, "Function Pass 3", paths["function_pass3"],
              LEGACY_PASS3_COLUMNS, expected_rows=50, small_profile=True,
              ok_status="LEGACY_REFERENCE_ONLY")
    check_csv(findings, "legacy", lang, "Stage 06 legacy final", paths["legacy_final"],
              {"row_id", "sentence", "final_function_id", "final_function_label"},
              expected_rows=50, small_profile=True, ok_status="LEGACY_REFERENCE_ONLY")

    join_files = [paths["test50"], paths["function_pass1"], paths["function_pass2"], paths["function_pass3"], paths["legacy_final"]]
    if all(path.exists() for path in join_files):
        try:
            id_sets = [set(pd.read_csv(path, usecols=["row_id"], dtype=str, encoding="utf-8-sig")["row_id"]) for path in join_files]
            if all(ids == id_sets[0] for ids in id_sets[1:]):
                add(findings, "legacy", lang, "row_id chain", "OK", "Stage 04–06 row IDs match exactly", paths["test50"])
            else:
                sizes = [len(ids) for ids in id_sets]
                add(findings, "legacy", lang, "row_id chain", "ERROR", f"row-ID sets differ: {sizes}", paths["test50"])
        except Exception as exc:
            add(findings, "legacy", lang, "row_id chain", "ERROR", f"join check failed: {exc}", paths["test50"])


def audit_v2_language(findings: list[Finding], root: Path, lang: str) -> None:
    base = root / "sense_aware_v2" / lang
    if not base.exists():
        add(findings, "v2", lang, "sense-aware output area", "NOT_STARTED",
            "no v2 output folder yet; this is expected before the revised workflow is run", base)
        return
    candidates = {
        "normalised input": (base / "inputs" / f"{lang}_test50_target_occurrences.csv", SAMPLE_COLUMNS | {"target_lemma", "target_pos"}),
        "sense inventory": (base / "sense_inventory" / f"{lang}_sense_inventory_v1.csv", SENSE_INVENTORY_COLUMNS),
        "sense Pass 1": (base / "sense_pass1" / f"{lang}_sense_pass1_test50.csv", SENSE_PASS_COLUMNS),
        "sense Pass 2": (base / "sense_pass2" / f"{lang}_sense_pass2_informed_test50.csv", SENSE_PASS_COLUMNS | {"review_mode"}),
        "function Pass 2": (base / "function_pass2" / f"{lang}_function_pass2_informed_test50.csv", CURRENT_PASS2_COLUMNS),
        "combined review": (base / "combined_review" / f"{lang}_combined_sense_function_test50.csv", {"row_id", "final_sense_id", "final_function_id", "review_status"}),
    }
    for item, (path, required) in candidates.items():
        if path.exists():
            check_csv(findings, "v2", lang, item, path, required, small_profile=path.stat().st_size < 5_000_000)
        else:
            add(findings, "v2", lang, item, "NOT_STARTED", "not created yet", path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only audit of Drive outputs against the current pipeline.")
    parser.add_argument("--drive_root", required=True)
    parser.add_argument("--repo_root", default=".")
    parser.add_argument("--report_csv")
    parser.add_argument("--report_json")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if ERROR findings exist")
    args = parser.parse_args()

    drive_root = Path(args.drive_root)
    repo_root = Path(args.repo_root)
    findings: list[Finding] = []
    check_exists(findings, "paths", "all", "Drive root", drive_root)
    check_exists(findings, "paths", "all", "Repository root", repo_root)
    audit_taxonomy(findings, drive_root, repo_root)
    for lang in LANGUAGES:
        audit_legacy_language(findings, drive_root, lang)
        audit_v2_language(findings, drive_root, lang)

    frame = pd.DataFrame([asdict(item) for item in findings])
    display_cols = ["status", "section", "language", "item", "message", "path"]
    with pd.option_context("display.max_rows", 300, "display.max_colwidth", 120, "display.width", 220):
        print(frame[display_cols].to_string(index=False))
    print("\nSummary")
    print(frame["status"].value_counts(dropna=False).to_string())

    if args.report_csv:
        report = Path(args.report_csv)
        report.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(report, index=False)
        print(f"CSV report: {report}")
    if args.report_json:
        report = Path(args.report_json)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps([asdict(item) for item in findings], indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report: {report}")

    if args.strict and (frame["status"] == "ERROR").any():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
