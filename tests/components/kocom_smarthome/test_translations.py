"""Every sensor a response can produce must have a name and an icon.

A missing key does not raise — Home Assistant quietly falls back to the object
id — so nothing but a test catches it.
"""

import json
import pathlib

import pytest

from custom_components.kocom_smarthome.models import MEASURES, SensorSpec

COMPONENT = pathlib.Path("custom_components/kocom_smarthome")
ENERGIES = ("elec", "gas", "heat", "hotwater", "water")

ALL_SPECS = [
    SensorSpec(energy, measure, previous)
    for energy in ENERGIES
    for measure in MEASURES
    for previous in (False, True)
]

TRANSLATION_FILES = [
    COMPONENT / "strings.json",
    COMPONENT / "translations" / "en.json",
    COMPONENT / "translations" / "ko.json",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_translation_key_shape():
    assert SensorSpec("elec", "value", False).translation_key == "elec_value"
    assert SensorSpec("gas", "price", True).translation_key == "gas_price_previous"


def test_every_spec_has_a_distinct_translation_key():
    keys = [spec.translation_key for spec in ALL_SPECS]
    assert len(keys) == len(set(keys)) == 30


@pytest.mark.parametrize("path", TRANSLATION_FILES, ids=lambda p: p.name)
def test_every_sensor_is_named_in_every_language(path):
    names = load(path)["entity"]["sensor"]
    missing = [s.translation_key for s in ALL_SPECS if s.translation_key not in names]
    assert not missing, f"{path.name} is missing: {missing}"
    blank = [k for k, v in names.items() if not v.get("name", "").strip()]
    assert not blank, f"{path.name} has empty names: {blank}"


@pytest.mark.parametrize("path", TRANSLATION_FILES, ids=lambda p: p.name)
def test_no_stray_translation_keys(path):
    """A key nobody uses is a name that silently never shows up."""
    names = load(path)["entity"]["sensor"]
    expected = {spec.translation_key for spec in ALL_SPECS}
    assert set(names) == expected


def test_every_sensor_has_an_icon():
    icons = load(COMPONENT / "icons.json")["entity"]["sensor"]
    missing = [s.translation_key for s in ALL_SPECS if s.translation_key not in icons]
    assert not missing, f"icons.json is missing: {missing}"
    assert all(v["default"].startswith("mdi:") for v in icons.values())


def test_languages_agree_on_which_keys_exist():
    key_sets = [set(load(p)["entity"]["sensor"]) for p in TRANSLATION_FILES]
    assert key_sets[0] == key_sets[1] == key_sets[2]


def test_strings_and_english_translations_match():
    """strings.json is the source; en.json must not drift from it."""
    assert load(TRANSLATION_FILES[0]) == load(TRANSLATION_FILES[1])


def test_korean_names_are_actually_korean():
    names = load(COMPONENT / "translations" / "ko.json")["entity"]["sensor"]
    untranslated = [
        key
        for key, value in names.items()
        if not any("가" <= ch <= "힣" for ch in value["name"])
    ]
    assert not untranslated
