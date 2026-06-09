
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

PASS2_FIELDS = [
    "row_id",
    "sentence",
    "pass1_function_id",
    "validator_decision",
    "function_id",
    "function_label",
    "confidence",
    "validation_rationale",
    "requires_review",
]

def validate_pass2(model, taxonomy_text, row, valid_ids):
    schema = make_schema(
        "cefr_function_pass2",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "pass1_function_id": {"type": "string"},
            "validator_decision": {"type": "string", "enum": ["accept", "change", "uncertain"]},
            "function_id": {"type": "string"},
            "function_label": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "validation_rationale": {"type": "string"},
            "requires_review": {"type": "boolean"},
        },
        PASS2_FIELDS,
    )

    instructions = f"""
You are doing BLIND VALIDATION of one sentence-level CEFR-derived function tag.

Your job is to validate the Pass 1 tag carefully.

Do not agree automatically, but do not change the label merely because another label is also possible.

Accept the Pass 1 tag if it is a reasonable and defensible best-fit label.

Change the Pass 1 tag only when another taxonomy label is clearly better for the whole sentence.

Rules:
- Use only a function_id from the controlled taxonomy.
- If Pass 1 is best, validator_decision = accept.
- If another label is better, validator_decision = change.
- If genuinely ambiguous, validator_decision = uncertain and requires_review = true.
- Keep validation_rationale short: maximum 30 words.
- Tag what the whole sentence is doing communicatively.

CONTROLLED TAXONOMY:
{taxonomy_text}

SENTENCE AND PASS 1 TAG:
row_id: {row["row_id"]}
sentence: {row["sentence"]}
pass1_function_id: {row["function_id"]}
pass1_function_label: {row["function_label"]}
pass1_rationale: {row.get("rationale", "")}
"""
    result = call_model_json(model, instructions, schema)
    validate_function_id(result, valid_ids)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL_PASS2", "gpt-5.4-mini"))
    args = parser.parse_args()

    taxonomy, valid_ids, _ = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(taxonomy)

    pass1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in pass1.iterrows():
        row_dict = row.to_dict()
        row_dict["row_id"] = str(row_dict["row_id"])
        if row_dict["row_id"] in done:
            continue

        result = validate_pass2(args.model, taxonomy_text, row_dict, valid_ids)
        append_csv_row(output_path, PASS2_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f'Pass 2 validated row {row_dict["row_id"]}: {result["validator_decision"]} -> {result["function_id"]}')
        time.sleep(12)

if __name__ == "__main__":
    main()
