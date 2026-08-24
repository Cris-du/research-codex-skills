#!/usr/bin/env python3
"""Read-only postflight verification for an assembled research figure SVG."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from audit_svg_inputs import audit_one, local_name


URL_ID_PATTERN = re.compile(r"url\(\s*(['\"]?)#([^)'\"\s]+)\1\s*\)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path, expected_labels: list[str], expected_panel_count: int | None) -> dict[str, Any]:
    absolute = path.expanduser().resolve(strict=False)
    audit = audit_one(absolute, False)
    blockers = list(audit["blocking_issues"])
    warnings = list(audit["warnings"])
    result: dict[str, Any] = {
        "path": str(absolute),
        "valid": False,
        "blocking_issues": blockers,
        "warnings": warnings,
        "metrics": audit.get("metrics", {}),
    }
    if blockers:
        return result

    root = ET.parse(absolute).getroot()
    ids = {element.get("id") for element in root.iter() if element.get("id")}
    missing_internal_refs: set[str] = set()
    panel_groups: list[dict[str, str]] = []
    label_values: list[str] = []

    for element in root.iter():
        if element.get("data-panel-source") is not None:
            panel_groups.append(
                {
                    "label": element.get("data-panel-label", ""),
                    "source": element.get("data-panel-source", ""),
                }
            )
        if element.get("data-panel-label-role") == "label":
            text_value = "".join(element.itertext()).strip()
            label_values.append(text_value)
        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name).lower()
            value = str(raw_value).strip()
            if name in {"href", "src"} and value.startswith("#") and value[1:] not in ids:
                missing_internal_refs.add(value[1:])
            for match in URL_ID_PATTERN.finditer(value):
                reference = match.group(2)
                if reference not in ids:
                    missing_internal_refs.add(reference)
        if local_name(element.tag) == "style" and element.text:
            for match in URL_ID_PATTERN.finditer(element.text):
                reference = match.group(2)
                if reference not in ids:
                    missing_internal_refs.add(reference)

    if missing_internal_refs:
        blockers.append("unresolved internal SVG references: " + ", ".join(sorted(missing_internal_refs)))

    duplicate_labels = sorted({label for label in label_values if label_values.count(label) > 1})
    if duplicate_labels:
        blockers.append("duplicate panel-label elements: " + ", ".join(duplicate_labels))

    for expected in expected_labels:
        count = label_values.count(expected)
        if count == 0:
            blockers.append(f"expected panel label is missing: {expected}")
        elif count > 1:
            blockers.append(f"expected panel label appears more than once: {expected}")

    if expected_panel_count is not None and len(panel_groups) != expected_panel_count:
        blockers.append(
            f"expected {expected_panel_count} panel group(s), found {len(panel_groups)}"
        )
    if not panel_groups:
        warnings.append("no data-panel-source groups found; source traceability is unavailable")

    result["labels"] = label_values
    result["panels"] = panel_groups
    result["sha256"] = sha256(absolute)
    result["bytes"] = absolute.stat().st_size
    result["valid"] = not blockers
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="assembled SVG to verify without modifying")
    parser.add_argument(
        "--expect-label",
        action="append",
        default=[],
        help="required panel label; repeat for multiple labels",
    )
    parser.add_argument("--expect-panel-count", type=int, help="required source-panel group count")
    args = parser.parse_args()
    if args.expect_panel_count is not None and args.expect_panel_count < 0:
        parser.error("--expect-panel-count must be non-negative")

    result = verify(args.svg, args.expect_label, args.expect_panel_count)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
