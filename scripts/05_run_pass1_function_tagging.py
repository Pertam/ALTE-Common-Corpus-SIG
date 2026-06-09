"""Pass 1: sentence-level CEFR function tagging.

Input: sampled sentence CSV + taxonomy CSV.
Output: CSV with provisional pass1 function labels and rationale.
Requires OPENAI_API_KEY in environment.
"""
from pathlib import Path
import argparse, json, os, time
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

PASS1_SCHEMA = {
    "name": "pass1_function_tags",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "row_id": {"type": "integer"},
                        "top_level_label": {"type": "string"},
                        "subcategory_id": {"type": "string"},
                        "subcategory_label": {"type": "string"},
                        "function_id": {"type": "string"},
                        "function_label": {"type": "string"},
                        "confidence": {"type": "number"},
                        "ai_rationale": {"type": "string"},
                        "review_status": {"type": "string", "enum": ["provisional", "review_required"]}
                    },
                    "required": ["row_id", "top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "confidence", "ai_rationale", "review_status"]
                }
            }
        },
        "required": ["items"]
    },
    "strict": True
}

SYSTEM = """You are tagging sentences for the European CEFR Vocabulary Atlas pilot.
Tag the communicative function of the whole sentence, not the sampled lemma and not the topic.
Use only function labels from the supplied taxonomy. Do not invent labels.
These are Tier 4 LLM candidate tags for later expert review.
Be conservative. Use review_required when the sentence is ambiguous, multi-functional, or the taxonomy fit is weak."""


def taxonomy_text(taxonomy: pd.DataFrame) -> str:
    cols = ["top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "definition", "decision_rule", "do_not_use_when"]
    cols = [c for c in cols if c in taxonomy.columns]
    return taxonomy[cols].fillna("").to_csv(index=False)


def call_model(client: OpenAI, model: str, tax_text: str, batch: pd.DataFrame) -> list[dict]:
    rows = batch[["row_id", "language_code", "lemma", "pos", "sentence"]].to_dict("records")
    prompt = f"""CONTROLLED TAXONOMY CSV:\n{tax_text}\n\nROWS TO TAG JSON:\n{json.dumps(rows, ensure_ascii=False)}"""
    resp = client.responses.create(
        model=model,
        input=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        text={"format": {"type": "json_schema", "json_schema": PASS1_SCHEMA}}
    )
    return json.loads(resp.output_text)["items"]


def run(input_csv: Path, taxonomy_csv: Path, output_csv: Path, model: str, batch_size: int) -> None:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    df = pd.read_csv(input_csv).reset_index(drop=True)
    df.insert(0, "row_id", range(1, len(df) + 1))
    taxonomy = pd.read_csv(taxonomy_csv)
    valid = set(taxonomy["function_id"])
    tax_text = taxonomy_text(taxonomy)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if output_csv.exists():
        done = pd.read_csv(output_csv)
        done_ids = set(done["row_id"])
    else:
        done = pd.DataFrame()
        done_ids = set()
    all_new = []
    todo = df[~df["row_id"].isin(done_ids)]
    for start in tqdm(range(0, len(todo), batch_size)):
        batch = todo.iloc[start:start + batch_size]
        for attempt in range(3):
            try:
                items = call_model(client, model, tax_text, batch)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        out = pd.DataFrame(items)
        bad = set(out["function_id"]) - valid
        if bad:
            raise ValueError(f"Model returned invalid function IDs: {bad}")
        merged = batch.merge(out, on="row_id", how="left")
        all_new.append(merged)
        pd.concat([done] + all_new, ignore_index=True).to_csv(output_csv, index=False)
    print(f"Saved pass1 tags to {output_csv}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--batch_size", type=int, default=25)
    args = p.parse_args()
    run(Path(args.input), Path(args.taxonomy), Path(args.output), args.model, args.batch_size)
