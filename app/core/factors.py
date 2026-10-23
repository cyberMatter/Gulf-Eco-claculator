"""Loads emission factors from JSON so data can be updated without code changes."""
import json
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).parent / "emission_factors_qatar.json"


@lru_cache(maxsize=1)
def load_factors() -> dict:
    return json.loads(_PATH.read_text(encoding="utf-8"))


def grid_factor() -> dict:
    return load_factors()["grid_electricity"]


def heat_factor() -> dict:
    return load_factors()["heat"]


def desal_factor(technology):
    block = load_factors()["desalination"]
    name = technology or block["default_technology"]
    if name not in block["technologies"]:
        raise KeyError(name)
    return name, block["technologies"][name]


def technologies():
    return list(load_factors()["desalination"]["technologies"])
