"""Pass 2: blind validation of pass1 sentence-level function tags.
The model must challenge pass1 and either confirm or replace it using the taxonomy.
"""
from pathlib import Path
import argparse, json, os, time
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

PASS2_SCHEMA = {
    "name": "pass2_validation_tags",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {"items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
            "row_id": {"type": "integer"},
            "pass2_decision": {"type": "string", "enum": ["confirm_pass1", "replace_pass1", "review_required"]},
            "final_top_level_label": {"type": "string"},
            "final_subcategory_id": {"type": "string"},
            "final_subcategory_label": {"type": "string"},
            "final_function_id": {"type": "string"},
            "final_function_label": {"type": "string"},
            "confidence": {"type": "number"},
            "validation_rationale": {"type": "string"},
            "review_status": {"type": "string", "enum": ["provisional", "review_required"]}
        }, "required": ["row_id", "pass2_decision", "final_top_level_label", "final_subcategory_id", "final_subcategory_label", "final_function_id", "final_function_label", "confidence", "validation_rationale", "review_status"]}}},
        "required": ["items"]
    },
    "strict": True
}

SYSTEM = """You are doing blind validation for the European CEFR Vocabulary Atlas pilot.
Do not agree automatically with pass1. Decide whether the hierarchy and fine-grained function are the best available labels.
Tag the whole sentence communicative function, not the sampled lemma and not the topic.
Use only the controlled taxonomy. Return review_required for weak, mixed, or ambiguous cases."""


def tax_text(taxonomy):
    cols = [c for c in ["top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "definition", "decision_rule", "do_not_use_when", "common_confusions"] if c in taxonomy.columns]
    return taxonomy[cols].fillna("").to_csv(index=False)


def run(input_csv: Path, taxonomy_csv: Path, output_csv: Path, model: str, batch_size: int) -> None:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    df = pd.read_csv(input_csv)
    taxonomy = pd.read_csv(taxonomy_csv)
    valid = set(taxonomy["function_id"])
    text = tax_text(taxonomy)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    done = pd.read_csv(output_csv) if output_csv.exists() else pd.DataFrame()
    done_ids = set(done["row_id"]) if not done.empty else set()
    all_new = []
    todo = df[~df["row_id"].isin(done_ids)]
    fields = ["row_id", "sentence", "lemma", "pos", "top_level_label", "subcategory_id", "subcategory_label", "function_id", "function_label", "ai_rationale"]
    for start in tqdm(range(0, len(todo), batch_size)):
        batch = todo.iloc[start:start + batch_size]
        prompt = f"CONTROLLED TAXONOMY CSV:\n{text}\n\nPASS1 ROWS JSON:\n{json.dumps(batch[fields].to_dict('records'), ensure_ascii=False)}"
        for attempt in range(3):
            try:
                resp = client.responses.create(
                    model=model,
                    input=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
                    text={"format":{"type":"json_schema","json_schema":PASS2_SCHEMA}}
                )
                items = json.loads(resp.output_text)["items"]
                break
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        out = pd.DataFrame(items)
        bad = set(out["final_function_id"]) - valid
        if bad:
            raise ValueError(f"Invalid final_function_id values: {bad}")
        merged = batch.merge(out, on="row_id", how="left")
        all_new.append(merged)
        pd.concat([done] + all_new, ignore_index=True).to_csv(output_csv, index=False)
    print(f"Saved pass2 validation to {output_csv}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--batch_size", type=int, default=25)
    args = p.parse_args()
    run(Path(args.input), Path(args.taxonomy), Path(args.output), args.model, args.batch_size)
