"""Stable identifiers and Unicode-normalisation helpers for the pilot data contract.

These helpers deliberately avoid ASCII transliteration.  Identifiers are derived
from NFC-normalised UTF-8 values, so distinctions such as Czech `být` vs `bít`
remain distinct.  Human-readable labels remain separate from identifiers.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any


def nfc(value: Any) -> str:
    """Return a stripped NFC-normalised string without discarding diacritics."""
    return unicodedata.normalize("NFC", str(value)).strip()


def _digest(*parts: Any, length: int = 20) -> str:
    payload = "\x1f".join(nfc(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def _version_token(version: str) -> str:
    token = re.sub(r"[^A-Za-z0-9._-]+", "-", nfc(version)).strip("-._")
    if not token:
        raise ValueError("Version must contain at least one letter or number.")
    return token


def make_observation_id(
    language_code: str,
    sentence_uid: str,
    target_char_start: int,
    target_char_end: int,
    lemma: str,
    pos: str,
) -> str:
    """Stable ID for one target occurrence in one corpus sentence.

    The ID is independent of dataframe order and random sampling order.  Character
    offsets distinguish repeated occurrences of the same lemma in one sentence.
    """
    lang = nfc(language_code).lower()
    return f"obs_{lang}_{_digest(lang, sentence_uid, target_char_start, target_char_end, lemma, pos)}"


def make_inventory_id(language: str, lemma: str, pos: str, inventory_version: str) -> str:
    """Stable, collision-resistant ID for one versioned language-specific inventory."""
    lang = nfc(language).lower()
    version = _version_token(inventory_version)
    return f"inv_{lang}_{_digest(lang, lemma, pos, version)}_{version}"


def make_sense_id(inventory_id: str, sense_key: str) -> str:
    """Stable ID for a sense inside a specific inventory version."""
    key = nfc(sense_key)
    return f"sen_{_digest(inventory_id, key)}"
