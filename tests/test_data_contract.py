from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from data_contract_utils import make_inventory_id, make_observation_id, make_sense_id  # noqa: E402
from llm_sense_tagging_utils import ensure_target_columns, read_inventory  # noqa: E402


class StableIdentifierTests(unittest.TestCase):
    def test_unicode_lemmas_do_not_collapse(self):
        byt = make_inventory_id("cs", "být", "VERB", "v1")
        bit = make_inventory_id("cs", "bít", "VERB", "v1")
        self.assertNotEqual(byt, bit)

    def test_inventory_version_changes_identity(self):
        v1 = make_inventory_id("de", "Bank", "NOUN", "v1")
        v2 = make_inventory_id("de", "Bank", "NOUN", "v2")
        self.assertNotEqual(v1, v2)

    def test_repeated_occurrences_have_distinct_observation_ids(self):
        first = make_observation_id("en", "en_abc", 0, 4, "bank", "NOUN")
        second = make_observation_id("en", "en_abc", 20, 24, "bank", "NOUN")
        self.assertNotEqual(first, second)
        self.assertEqual(first, make_observation_id("en", "en_abc", 0, 4, "bank", "NOUN"))

    def test_sense_ids_are_scoped_to_inventory_version(self):
        inv1 = make_inventory_id("en", "bank", "NOUN", "v1")
        inv2 = make_inventory_id("en", "bank", "NOUN", "v2")
        self.assertNotEqual(make_sense_id(inv1, "ordinary:01"), make_sense_id(inv2, "ordinary:01"))


class TargetColumnTests(unittest.TestCase):
    def test_language_code_alias_and_observation_id(self):
        df = pd.DataFrame([
            {
                "observation_id": "obs_en_123",
                "language_code": "en",
                "lemma": "bank",
                "pos": "NOUN",
                "target_token": "bank",
                "sentence": "The bank is open.",
            }
        ])
        out = ensure_target_columns(df, "test")
        self.assertEqual(out.loc[0, "row_id"], "obs_en_123")
        self.assertEqual(out.loc[0, "language"], "en")
        self.assertEqual(out.loc[0, "target_lemma"], "bank")

    def test_missing_stable_identifier_is_rejected(self):
        df = pd.DataFrame([
            {"language_code": "en", "lemma": "bank", "pos": "NOUN", "sentence": "The bank is open."}
        ])
        with self.assertRaises(ValueError):
            ensure_target_columns(df, "test")


class InventoryVersionTests(unittest.TestCase):
    def test_multiple_inventory_versions_for_one_lemma_are_rejected(self):
        rows = []
        for version in ["v1", "v2"]:
            inventory_id = make_inventory_id("cs", "být", "VERB", version)
            rows.append({
                "inventory_id": inventory_id,
                "inventory_version": version,
                "language": "cs",
                "target_lemma": "být",
                "target_pos": "VERB",
                "sense_id": make_sense_id(inventory_id, "ordinary:01"),
                "sense_gloss": "test",
                "inventory_status": "approved",
            })
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inventory.csv"
            pd.DataFrame(rows).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                read_inventory(path)


if __name__ == "__main__":
    unittest.main()
