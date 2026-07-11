from copy import deepcopy
from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_memory_map import validate_memory_map


@pytest.fixture
def valid_map():
    return {
        "schema_version": 1,
        "bus": {
            "address_width": 32,
            "data_width": 32,
        },
        "regions": [
            {
                "name": "boot_memory",
                "kind": "memory",
                "base": 0x00000000,
                "size": 0x4000,
                "instance": "u_boot_memory",
                "readable": True,
                "writable": False,
                "executable": True,
                "implemented": False,
            },
            {
                "name": "gpio",
                "kind": "peripheral",
                "base": 0x40000000,
                "size": 0x1000,
                "instance": "u_gpio",
                "readable": True,
                "writable": True,
                "executable": False,
                "implemented": True,
            },
        ],
    }


def assert_error_contains(document, expected):
    errors = validate_memory_map(document)
    assert any(expected in error for error in errors), errors


def test_valid_map_passes(valid_map):
    assert validate_memory_map(valid_map) == []


def test_rejects_unknown_top_level_field(valid_map):
    document = deepcopy(valid_map)
    document["unexpected"] = True

    assert_error_contains(document, "unknown top-level field")


def test_rejects_unknown_region_field(valid_map):
    document = deepcopy(valid_map)
    document["regions"][0]["execute"] = True

    assert_error_contains(document, "unknown field: execute")


def test_rejects_missing_required_field(valid_map):
    document = deepcopy(valid_map)
    del document["regions"][0]["implemented"]

    assert_error_contains(
        document,
        "missing required field: implemented",
    )


def test_rejects_duplicate_name(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["name"] = "boot_memory"

    assert_error_contains(document, "duplicate region name")


def test_rejects_duplicate_instance(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["instance"] = "u_boot_memory"

    assert_error_contains(document, "duplicate region instance")


def test_rejects_overlap(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["base"] = 0x00002000
    document["regions"][1]["size"] = 0x2000

    assert_error_contains(document, "overlapping regions")


def test_rejects_misaligned_base(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["base"] = 0x40000800

    assert_error_contains(document, "base must be aligned")


def test_rejects_non_power_of_two_size(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["size"] = 0x1800

    assert_error_contains(document, "size must be a power of two")


def test_rejects_executable_unreadable_region(valid_map):
    document = deepcopy(valid_map)
    document["regions"][0]["readable"] = False

    assert_error_contains(
        document,
        "cannot be executable without being readable",
    )


def test_rejects_executable_peripheral(valid_map):
    document = deepcopy(valid_map)
    document["regions"][1]["executable"] = True

    assert_error_contains(
        document,
        "peripheral cannot be executable",
    )


def test_rejects_region_outside_address_width(valid_map):
    document = deepcopy(valid_map)
    document["bus"]["address_width"] = 16

    assert_error_contains(document, "exceeds the bus address width")


def test_rejects_boolean_integer_field(valid_map):
    document = deepcopy(valid_map)
    document["regions"][0]["base"] = False

    assert_error_contains(
        document,
        "base must be a non-negative integer",
    )
