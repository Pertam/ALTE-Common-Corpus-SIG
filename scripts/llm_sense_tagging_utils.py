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
    """Normalise sample-column aliases without inventing order-dependent IDs."""
    require_columns(df, ["sentence"], label)
    result = df.copy()

    if "row_id" not in result.columns:
        if "observation_id" in result.columns:
            result.insert(0, "row_id", result["observation_id"].astype(str))
        else:
            raise ValueError(
                f"{label} requires row_id or observation_id. "
                "Do not generate positional row IDs; rerun the occurrence-level sampling stage."
            )

    if "observation_id" in result.columns:
        mismatch = result["row_id"].astype(str) != result["observation_id"].astype(str)
        if mismatch.any():
            raise ValueError(f"{label} contains row_id values that do not match observation_id.")

    if result["row_id"].astype(str).str.strip().eq("").any():
        raise ValueError(f"{label} contains blank row_id values.")
    if result["row_id"].duplicated().any():
        dupes = result.loc[result["row_id"].duplicated(), "row_id"].head(20).tolist()
        raise ValueError(f"{label} contains duplicate row_id values: {dupes}")

    aliases = {
        "language": ["language", "language_code", "lang"],
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

    if df["inventory_id"].astype(str).str.strip().eq("").any():
        raise ValueError("Sense inventory contains blank inventory_id values.")
    if df["sense_id"].astype(str).str.strip().eq("").any():
        raise ValueError("Sense inventory contains blank sense_id values.")
    if df["sense_id"].duplicated().any():
        dupes = df.loc[df["sense_id"].duplicated(), "sense_id"].head(20).tolist()
        raise ValueError(f"Sense inventory contains duplicate sense_id values: {dupes}")

    if not allow_provisional:
        invalid = df[df["inventory_status"].str.lower() != "approved"]
        if not invalid.empty:
            raise ValueError("Sense inventory must be human-approved before production tagging.")

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for _, row in df.iterrows():
        key = (row["language"].casefold(), row["target_lemma"].casefold(), row["target_pos"].casefold())
        grouped.setdefault(key, []).append(row.to_dict())

    # Never silently combine multiple revisions of one inventory into one choice set.
    for key, records in grouped.items():
        inventory_ids = {str(r["inventory_id"]) for r in records}
        if len(inventory_ids) != 1:
            raise ValueError(
                f"Multiple inventory versions/IDs found for {key}: {sorted(inventory_ids)}. "
                "Select one explicit inventory version for this tagging run."
            )
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
