
import argparse
import csv
import json
import os
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

PASS3_FIELDS = [
    "row_id",
    "sentence",
    "pass1_function_id",
    "pass2_function_id",
    "final_function_id",
    "final_function_label",
    "final_confidence",
    "adjudication_rationale",
    "human_review_recommended",
]

def adjudicate_pass3(model, taxonomy_text, row, valid_ids):
    schema = make_schema(
        "cefr_function_pass3",
        {
            "row_id": {"type": "string"},
            "sentence": {"type": "string"},
            "pass1_function_id": {"type": "string"},
            "pass2_function_id": {"type": "string"},
            "final_function_id": {"type": "string"},
            "final_function_label": {"type": "string"},
            "final_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "adjudication_rationale": {"type": "string"},
            "human_review_recommended": {"type": "boolean"},
        },
        PASS3_FIELDS,
    )

    instructions = f"""
You are making the final moderated decision for one CEFR-derived sentence-level function tag.

Use the controlled taxonomy only.
Use Pass 1 and Pass 2 as evidence, but decide independently.
If Pass 1 and Pass 2 agree, still check whether the agreed label is genuinely the best whole-sentence function.
If Pass 1 and Pass 2 disagree, choose the label that best captures what the whole sentence is doing communicatively.
Do not simply average the two previous answers.
Keep adjudication_rationale short: maximum 35 words.
Mark human_review_recommended true only if the case remains genuinely ambiguous.

CONTROLLED TAXONOMY:
{taxonomy_text}

CASE:
row_id: {row["row_id"]}
sentence: {row["sentence"]}

PASS 1:
function_id: {row["pass1_function_id"]}
rationale: {row.get("pass1_rationale", "")}
confidence: {row.get("pass1_confidence", "")}

PASS 2:
function_id: {row["pass2_function_id"]}
decision: {row.get("validator_decision", "")}
rationale: {row.get("pass2_rationale", "")}
confidence: {row.get("pass2_confidence", "")}
"""
    result = call_model_json(model, instructions, schema)
    if result.get("final_function_id", "") not in valid_ids:
        raise ValueError(f'Invalid final_function_id returned: {result.get("final_function_id")}')
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass1", required=True)
    parser.add_argument("--pass2", required=True)
    parser.add_argument("--taxonomy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL_PASS3", "gpt-5.5"))
    args = parser.parse_args()

    taxonomy, valid_ids, _ = read_taxonomy(Path(args.taxonomy))
    taxonomy_text = compact_taxonomy_text(taxonomy)

    p1 = pd.read_csv(args.pass1, dtype=str).fillna("")
    p2 = pd.read_csv(args.pass2, dtype=str).fillna("")

    p1_small = p1.rename(columns={
        "function_id": "pass1_function_id",
        "confidence": "pass1_confidence",
        "rationale": "pass1_rationale",
    })[["row_id", "sentence", "pass1_function_id", "pass1_confidence", "pass1_rationale"]]

    p2_small = p2.rename(columns={
        "function_id": "pass2_function_id",
        "confidence": "pass2_confidence",
        "validation_rationale": "pass2_rationale",
    })[["row_id", "pass2_function_id", "pass2_confidence", "pass2_rationale", "validator_decision", "requires_review"]]

    merged = p1_small.merge(p2_small, on="row_id", how="inner")

    problem_cases = merged.copy()

    output_path = Path(args.output)
    done = load_done_ids(output_path)

    for _, row in problem_cases.iterrows():
        row_dict = row.to_dict()
        row_dict["row_id"] = str(row_dict["row_id"])
        if row_dict["row_id"] in done:
            continue

        result = adjudicate_pass3(args.model, taxonomy_text, row_dict, valid_ids)
        append_csv_row(output_path, PASS3_FIELDS, result)
        done.add(row_dict["row_id"])
        print(f'Pass 3 adjudicated row {row_dict["row_id"]}: {result["final_function_id"]}')

if __name__ == "__main__":
    main()
