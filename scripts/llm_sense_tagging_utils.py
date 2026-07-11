"""Shared helpers for lexical-sense inventory and tagging scripts."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from llm_function_tagging_utils import append_csv_row, call_model_json, load_done_ids, make_schema, require_columns

REQUIRED_INVENTORY_COLUMNS = [
    "inventory_id", "language", "target_lemma", "target_pos",
    "sense_id", "sense_gloss", "inventory_status",
]


def ensure_target_columns(df: pd.DataFrame, label: str) -> pd.DataFrame:
    require_columns(df, ["sentence"], label)
    result = df.copy()
    if "row_id" not in result.columns:
        result.insert(0, "row_id", [f"row_{i + 1:06d}" for i in range(len(result))])
    aliases = {
        "language": ["language", "lang"],
        "target_token": ["target_token", "token"],
        "target_lemma": ["target_lemma", "lemma"],
        "target_pos": ["target_pos", "pos"],
    }
    for destination, candidates in aliases.items():
        if destination in result.columns:
            continue
        source = next((name for name in candidates if name in result.columns), None)
        if source:
            result[destination] = result[source]
        elif destination == "target_token":
            result[destination] = ""
        else:
            raise ValueError(f"{label} requires {destination}; accepted aliases: {candidates}")
    return result


def read_inventory(path: Path, allow_provisional: bool = False):
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, dtype=str).fillna("")
    require_columns(df, REQUIRED_INVENTORY_COLUMNS, "Sense inventory")
    if not allow_provisional:
        invalid = df[df["inventory_status"].str.lower() != "approved"]
        if not invalid.empty:
            raise ValueError("Sense inventory must be human-approved before production tagging.")
    grouped = {}
    for _, row in df.iterrows():
        key = (row["language"].casefold(), row["target_lemma"].casefold(), row["target_pos"].casefold())
        grouped.setdefault(key, []).append(row.to_dict())
    return grouped


def inventory_for_row(row: dict[str, str], grouped):
    key = (row["language"].casefold(), row["target_lemma"].casefold(), row["target_pos"].casefold())
    if key not in grouped:
        raise KeyError(f"No approved sense inventory for {key}")
    return grouped[key]


def compact_inventory(records) -> str:
    return "\n".join(
        f"{r['sense_id']} | {r['sense_gloss']} | {r.get('distinguishing_features', '')} | {r.get('typical_patterns', '')}"
        for r in records
    )
