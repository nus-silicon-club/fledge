#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path

import yaml


TOP_LEVEL_FIELDS = {"schema_version", "bus", "regions"}
BUS_FIELDS = {"address_width", "data_width"}
REGION_FIELDS = {
    "name",
    "kind",
    "base",
    "size",
    "instance",
    "readable",
    "writable",
    "executable",
    "implemented",
}

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
INSTANCE_PATTERN = re.compile(r"^u_[a-z][a-z0-9_]*$")


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_power_of_two(value):
    return value > 0 and (value & (value - 1)) == 0


def unknown_fields(mapping, allowed):
    return sorted(set(mapping) - allowed)


def validate_memory_map(document):
    errors = []

    if not isinstance(document, dict):
        return ["top level must be a mapping"]

    for field in unknown_fields(document, TOP_LEVEL_FIELDS):
        errors.append(f"unknown top-level field: {field}")

    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    bus = document.get("bus")
    if not isinstance(bus, dict):
        errors.append("bus must be a mapping")
        return errors

    for field in unknown_fields(bus, BUS_FIELDS):
        errors.append(f"unknown bus field: {field}")

    address_width = bus.get("address_width")
    data_width = bus.get("data_width")

    if not is_integer(address_width) or address_width <= 0:
        errors.append("bus.address_width must be a positive integer")

    if (
        not is_integer(data_width)
        or data_width <= 0
        or data_width % 8 != 0
    ):
        errors.append(
            "bus.data_width must be a positive integer divisible by 8"
        )

    regions = document.get("regions")
    if not isinstance(regions, list) or not regions:
        errors.append("regions must be a non-empty list")
        return errors

    names = set()
    instances = set()
    validated_ranges = []

    for index, region in enumerate(regions):
        prefix = f"regions[{index}]"

        if not isinstance(region, dict):
            errors.append(f"{prefix} must be a mapping")
            continue

        for field in unknown_fields(region, REGION_FIELDS):
            errors.append(f"{prefix} has unknown field: {field}")

        missing = sorted(REGION_FIELDS - set(region))
        for field in missing:
            errors.append(f"{prefix} is missing required field: {field}")

        name = region.get("name")
        if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
            errors.append(
                f"{prefix}.name must use lowercase snake_case"
            )
        elif name in names:
            errors.append(f"duplicate region name: {name}")
        else:
            names.add(name)

        instance = region.get("instance")
        if (
            not isinstance(instance, str)
            or not INSTANCE_PATTERN.fullmatch(instance)
        ):
            errors.append(
                f"{prefix}.instance must use the form u_lowercase_name"
            )
        elif instance in instances:
            errors.append(f"duplicate region instance: {instance}")
        else:
            instances.add(instance)

        kind = region.get("kind")
        if kind not in {"memory", "peripheral"}:
            errors.append(
                f"{prefix}.kind must be memory or peripheral"
            )

        for field in (
            "readable",
            "writable",
            "executable",
            "implemented",
        ):
            if not isinstance(region.get(field), bool):
                errors.append(f"{prefix}.{field} must be a boolean")

        readable = region.get("readable")
        writable = region.get("writable")
        executable = region.get("executable")

        if readable is False and writable is False:
            errors.append(
                f"{prefix} must be readable, writable, or both"
            )

        if executable is True and readable is not True:
            errors.append(
                f"{prefix} cannot be executable without being readable"
            )

        if kind == "peripheral" and executable is True:
            errors.append(f"{prefix} peripheral cannot be executable")

        base = region.get("base")
        size = region.get("size")

        if not is_integer(base) or base < 0:
            errors.append(
                f"{prefix}.base must be a non-negative integer"
            )

        if not is_integer(size) or size <= 0:
            errors.append(f"{prefix}.size must be a positive integer")

        if not is_integer(base) or base < 0:
            continue

        if not is_integer(size) or size <= 0:
            continue

        if not is_power_of_two(size):
            errors.append(f"{prefix}.size must be a power of two")

        if base % size != 0:
            errors.append(
                f"{prefix}.base must be aligned to its size"
            )

        if is_integer(data_width) and data_width > 0:
            bytes_per_word = data_width // 8
            if bytes_per_word > 0 and size % bytes_per_word != 0:
                errors.append(
                    f"{prefix}.size must be aligned to the bus word size"
                )

        if is_integer(address_width) and address_width > 0:
            address_limit = 1 << address_width
            if base + size > address_limit:
                errors.append(
                    f"{prefix} exceeds the bus address width"
                )

        validated_ranges.append((base, base + size, prefix, name))

    validated_ranges.sort(key=lambda item: item[0])

    for previous, current in zip(
        validated_ranges,
        validated_ranges[1:],
    ):
        previous_base, previous_end, previous_prefix, previous_name = previous
        current_base, _, current_prefix, current_name = current

        if current_base < previous_end:
            errors.append(
                "overlapping regions: "
                f"{previous_name or previous_prefix} and "
                f"{current_name or current_prefix}"
            )

    return errors


def load_memory_map(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except OSError as error:
        raise ValueError(f"cannot read file: {error}") from error
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML: {error}") from error


def main():
    parser = argparse.ArgumentParser(
        description="Validate the Fledge SoC memory map."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("hw/soc/memory_map.yml"),
        help="path to the memory-map YAML file",
    )
    args = parser.parse_args()

    try:
        document = load_memory_map(args.path)
    except ValueError as error:
        print(f"{args.path}: {error}", file=sys.stderr)
        return 1

    errors = validate_memory_map(document)

    if errors:
        for error in errors:
            print(f"{args.path}: {error}", file=sys.stderr)
        return 1

    print(f"{args.path}: memory map validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
