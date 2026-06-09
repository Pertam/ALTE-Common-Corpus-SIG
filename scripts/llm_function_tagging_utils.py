"""Shared helpers for the Stage 05 LLM function-tagging scripts."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:  # allows --help and dry-run before optional API deps are installed
    def stop_after_attempt(*args, **kwargs):
        return None
    def wait_exponential(*args, **kwargs):
        return None
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

GUIDANCE_CANDIDATES = [
    "function_guidance",
    "rewritten_guidance",
    "guidance",
    "definition",
    "descriptor_text",
    "function_description",
]

TAXONOMY_REQUIRED = [
    "top_level_label",
    "subcategory_id",
    "subcategory_label",
    "function_id",
    "function_label",
]


def read_taxonomy(path: Path) -> tuple[list[dict[str, str]], set[str], dict[str, dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {path}")

    df = pd.read_csv(path, dtype=str).fillna("")
    missing = [c for c in TAXONOMY_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Taxonomy file is missing required columns: {missing}")

    guidance_col = next((c for c in GUIDANCE_CANDIDATES if c in df.columns), None)
    if guidance_col is None:
        df["function_guidance"] = ""
        guidance_col = "function_guidance"

    records: list[dict[str, str]] = []
    hierarchy: dict[str, dict[str, str]] = {}

    for _, row in df.iterrows():
        function_id = str(row["function_id"]).strip()
        if not function_id:
            continue

        record = {
            "top_level_label": str(row["top_level_label"]).strip(),
            "subcategory_id": str(row["subcategory_id"]).strip(),
            "subcategory_label": str(row["subcategory_label"]).strip(),
            "function_id": function_id,
            "function_label": str(row["function_label"]).strip(),
            "function_guidance": str(row.get(guidance_col, "")).strip(),
        }
        records.append(record)
        hierarchy[function_id] = record

    valid_ids = set(hierarchy)
    if len(valid_ids) != len(records):
        raise ValueError("Taxonomy contains duplicate function_id values.")

    return records, valid_ids, hierarchy


def compact_taxonomy_text(records: list[dict[str, str]]) -> str:
    lines = []
    for r in records:
        guidance = r.get("function_guidance", "")
        guidance_part = f" | Guidance: {guidance}" if guidance else ""
        lines.append(
            f'{r["function_id"]} | {r["top_level_label"]} > '
            f'{r["subcategory_id"]}: {r["subcategory_label"]} > '
            f'{r["function_label"]}{guidance_part}'
        )
    return "\n".join(lines)


def load_done_ids(output_path: Path) -> set[str]:
    if not output_path.exists() or output_path.stat().st_size == 0:
        return set()
    df = pd.read_csv(output_path, dtype=str).fillna("")
    if "row_id" not in df.columns:
        return set()
    return set(df["row_id"].astype(str))


def append_csv_row(output_path: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    exists = output_path.exists() and output_path.stat().st_size > 0
    with output_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fieldnames})


def make_schema(name: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "name": name,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required,
        },
        "strict": True,
    }


def normalise_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def get_openai_client():
    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install API dependencies first: pip install openai python-dotenv tenacity") from exc

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Set it in the environment before running Stage 05.")
    return OpenAI()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def call_model_json(model: str, instructions: str, schema: dict[str, Any]) -> dict[str, Any]:
    client = get_openai_client()
    response = client.responses.create(
        model=model,
        input=instructions,
        text={"format": schema},
    )
    text = getattr(response, "output_text", None)
    if not text:
        raise ValueError("Model response did not include output_text.")
    return json.loads(text)


def require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def apply_taxonomy_fields(result: dict[str, Any], function_id_key: str, hierarchy: dict[str, dict[str, str]]) -> dict[str, Any]:
    fid = str(result.get(function_id_key, "")).strip()
    if fid not in hierarchy:
        raise ValueError(f"Invalid function_id returned: {fid}")
    h = hierarchy[fid]
    if function_id_key == "function_id":
        result["top_level_label"] = h["top_level_label"]
        result["subcategory_id"] = h["subcategory_id"]
        result["subcategory_label"] = h["subcategory_label"]
        result["function_label"] = h["function_label"]
    elif function_id_key == "final_function_id":
        result["final_function_label"] = h["function_label"]
    return result


def default_model(pass_name: str) -> str:
    return os.getenv(f"OPENAI_MODEL_{pass_name.upper()}", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
