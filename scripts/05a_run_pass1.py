
import argparse
import csv
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
client = OpenAI()

def read_taxonomy(path: Path):
    df = pd.read_csv(path, dtype=str).fillna("")
    required = [
        "top_level_label",
        "subcategory_id",
        "subcategory_label",
        "function_id",
        "function_label",
        "function_guidance",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Taxonomy file is missing columns: {missing}")

    records = df[required].to_dict(orient="records")
    valid_ids = set(df["function_id"].astype(str))
    hierarchy = {
        row["function_id"]: {
            "top_level_label": row["top_level_label"],
            "subcategory_id": row["subcategory_id"],
            "subcategory_label": row["subcategory_label"],
            "function_label": row["function_label"],
        }
        for row in records
    }
    return records, valid_ids, hierarchy

def compact_taxonomy_text(records):
    lines = []
    for r in records:
        lines.append(
            f'{r["function_id"]} | {r["top_level_label"]} > '
            f'{r["subcategory_id"]}: {r["subcategory_label"]} > '
            f'{r["function_label"]} | Guidance: {r["function_guidance"]}'
        )
    return "\n".join(lines)

def load_done_ids(output_path: Path):
    if not output_path.exists() or output_path.stat().st_size == 0:
        return set()
    df = pd.read_csv(output_path, dtype=str)
    if "row_id" not in df.columns:
        return set()
    return set(df["row_id"].astype(str))

def append_csv_row(output_path: Path, fieldnames, row):
    exists = output_path.exists() and output_path.stat().st_size > 0
    with open(output_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fieldnames})

def validate_function_id(result, valid_ids):
    fid = result.get("function_id", "")
    if fid not in valid_ids:
        raise ValueError(f"Invalid function_id returned: {fid}")

def make_schema(name, properties, required):
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

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def call_model_json(model, instructions, schema):
    response = client.responses.create(
        model=model,
        input=instructions,
        text={"format": schema},
    )
    return json.loads(response.output_text)

PASS1_FIELDS = [
    "row_id",
    "sentence",
    "top_level_label",
    "subcategory_id",
    "subcategory_label",
    "function_id",
    "function_label",
    "confidence",
    "rationale",
    "alternative_function_id",
    "ambiguity_note",
    "requires_review",
]

def annotate_pass1(model, taxonomy_text, row, valid_ids):
    schema = make_schema(
        "cefr_function_pass1",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "top_level_label": {"type": "string"},
            "subcategory_id": {"type": "string"},
            "subcategory_label": {"type": "string"},
            "function_id": {"type": "string"},
            "function_label": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "rationale": {"type": "string"},
            "alternative_function_id": {"type": "string"},
            "ambiguity_note": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        PASS1_FIELDS,
    )

    instructions = f"""
You are annotating ONE sentence for CEFR-derived communicative function.

Do not use memory from any previous examples.
Do not generalise across rows.
Tag what the whole sentence is doing communicatively, not the topic of the sentence.
Use only a function_id from the taxonomy.
Keep the rationale short: maximum 25 words.
If uncertain, use confidence = low and requires_review = true.
If there is no plausible alternative, set alternative_function_id to an empty string.

CONTROLLED TAXONOMY:
{taxonomy_text}

SENTENCE:
row_id: {row["row_id"]}
sentence: {row["sentence"]}
"""
    result = call_model_json(model, instructions, schema)
    validate_function_id(result, valid_ids)
    if result.get("alternative_function_id") and result["alternative_function_id"] not in valid_ids:
        result["alternative_function_id"] = ""
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sentences", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL_PASS1", "gpt-5.4-mini"))
    args = parser.parse_args()

    taxonomy, valid_ids, _ = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(taxonomy)

    sentences = pd.read_csv(args.sentences, dtype=str).fillna("")
    if "row_id" not in sentences.columns or "sentence" not in sentences.columns:
        raise ValueError("Sentence file must contain row_id and sentence columns.")

    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in sentences.iterrows():
        row_dict = {"row_id": str(row["row_id"]), "sentence": str(row["sentence"])}
        if row_dict["row_id"] in done:
            continue

        result = annotate_pass1(args.model, taxonomy_text, row_dict, valid_ids)
        append_csv_row(output_path, PASS1_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f'Pass 1 tagged row {row_dict["row_id"]}: {result["function_id"]} ({result["confidence"]})')
        time.sleep(12)

if __name__ == "__main__":
    main()
