#!/usr/bin/env python3
"""Read-only safety and editability audit for SVG figure units."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


NUMBER_WITH_UNIT = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*"
    r"(px|pt|pc|mm|cm|in)?\s*$",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def parse_dimension(value: str | None) -> float | None:
    if not value:
        return None
    match = NUMBER_WITH_UNIT.match(value)
    if not match:
        return None
    number = float(match.group(1))
    if not math.isfinite(number) or number <= 0:
        return None
    unit = (match.group(2) or "px").lower()
    factors = {
        "px": 1.0,
        "pt": 96.0 / 72.0,
        "pc": 16.0,
        "mm": 96.0 / 25.4,
        "cm": 96.0 / 2.54,
        "in": 96.0,
    }
    return number * factors[unit]


def parse_view_box(value: str | None) -> list[float] | None:
    if not value:
        return None
    try:
        numbers = [float(part) for part in re.split(r"[\s,]+", value.strip())]
    except ValueError:
        return None
    if len(numbers) != 4 or not all(math.isfinite(item) for item in numbers):
        return None
    if numbers[2] <= 0 or numbers[3] <= 0:
        return None
    return numbers


def is_external_reference(value: str) -> bool:
    candidate = value.strip().strip("'\"")
    if not candidate or candidate.startswith("#") or candidate.startswith("data:"):
        return False
    return True


def audit_one(path: Path, require_editable_text: bool) -> dict[str, Any]:
    absolute = path.expanduser().resolve(strict=False)
    result: dict[str, Any] = {
        "path": str(absolute),
        "valid": False,
        "blocking_issues": [],
        "warnings": [],
        "metrics": {},
    }
    blockers: list[str] = result["blocking_issues"]
    warnings: list[str] = result["warnings"]

    if not absolute.exists():
        blockers.append("file does not exist")
        return result
    if not absolute.is_file():
        blockers.append("path is not a file")
        return result
    if absolute.suffix.lower() != ".svg":
        blockers.append("input is not an .svg file")
        return result

    try:
        tree = ET.parse(absolute)
    except (ET.ParseError, OSError) as exc:
        blockers.append(f"SVG XML cannot be parsed: {exc}")
        return result

    root = tree.getroot()
    if local_name(root.tag) != "svg":
        blockers.append("document root is not <svg>")
        return result

    view_box = parse_view_box(root.get("viewBox"))
    width = parse_dimension(root.get("width"))
    height = parse_dimension(root.get("height"))
    if view_box is None and (width is None or height is None):
        blockers.append("SVG has neither a usable viewBox nor positive width/height")

    ids: list[str] = []
    tag_counts: Counter[str] = Counter()
    text_count = 0
    external_refs: list[str] = []
    embedded_raster_count = 0
    event_attributes: list[str] = []
    unsafe_tags: list[str] = []

    for element in root.iter():
        tag = local_name(element.tag)
        tag_counts[tag] += 1
        if tag == "text":
            text_count += 1
        if tag in {"script", "foreignObject"}:
            unsafe_tags.append(tag)

        element_id = element.get("id")
        if element_id:
            ids.append(element_id)

        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name).lower()
            value = str(raw_value)
            if name.startswith("on"):
                event_attributes.append(name)
            if name in {"href", "src"}:
                if tag == "image" and value.strip().startswith("data:"):
                    embedded_raster_count += 1
                elif is_external_reference(value):
                    external_refs.append(value)
            for match in URL_PATTERN.finditer(value):
                reference = match.group(2)
                if is_external_reference(reference):
                    external_refs.append(reference)

        if tag == "style" and element.text:
            if re.search(r"@import\b", element.text, re.IGNORECASE):
                external_refs.append("CSS @import")
            for match in URL_PATTERN.finditer(element.text):
                reference = match.group(2)
                if is_external_reference(reference):
                    external_refs.append(reference)

    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        blockers.append("duplicate SVG ids: " + ", ".join(duplicates))
    if unsafe_tags:
        blockers.append("unsafe or non-portable elements: " + ", ".join(sorted(set(unsafe_tags))))
    if event_attributes:
        blockers.append("event-handler attributes are not allowed: " + ", ".join(sorted(set(event_attributes))))
    if external_refs:
        blockers.append("external references are not allowed: " + ", ".join(sorted(set(external_refs))))
    if embedded_raster_count:
        warnings.append(
            f"contains {embedded_raster_count} embedded raster image(s); their interiors are not SVG-editable"
        )
    if text_count == 0:
        message = "contains no editable <text> elements; text may be absent or converted to outlines"
        if require_editable_text:
            blockers.append(message)
        else:
            warnings.append(message)

    result["metrics"] = {
        "view_box": view_box,
        "width_px": width,
        "height_px": height,
        "element_count": sum(tag_counts.values()),
        "text_element_count": text_count,
        "id_count": len(ids),
        "embedded_raster_count": embedded_raster_count,
        "tag_counts": dict(sorted(tag_counts.items())),
    }
    result["valid"] = not blockers
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="SVG files to inspect without modifying")
    parser.add_argument(
        "--require-editable-text",
        action="store_true",
        help="treat zero editable <text> elements as blocking",
    )
    args = parser.parse_args()

    results = [audit_one(path, args.require_editable_text) for path in args.inputs]
    payload = {
        "mode": "read-only-audit",
        "all_valid": all(item["valid"] for item in results),
        "blocking_count": sum(len(item["blocking_issues"]) for item in results),
        "warning_count": sum(len(item["warnings"]) for item in results),
        "files": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["all_valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
