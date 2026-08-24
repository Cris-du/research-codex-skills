#!/usr/bin/env python3
"""Apply an explicit, project-local list of named SVG refinements."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


INPUT_RELATIVE_PATH = Path(r"{{INPUT_RELATIVE_PATH}}")
OUTPUT_RELATIVE_PATH = Path(r"{{OUTPUT_RELATIVE_PATH}}")
OPERATIONS_JSON = r'''{{OPERATIONS_JSON}}'''


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_root() -> Path:
    # Expected location: <project>/04_结果主库/脚本/refine_Fig_N.py
    return Path(__file__).resolve().parents[2]


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def compact_number(value: float) -> str:
    return f"{value:.12g}"


def select_one(root: ET.Element, selector: dict[str, str]) -> ET.Element:
    if not isinstance(selector, dict) or len(selector) != 1:
        raise ValueError("selector must contain exactly one attribute/value pair")
    attr, expected = next(iter(selector.items()))
    matches = [element for element in root.iter() if element.get(attr) == expected]
    if len(matches) != 1:
        raise ValueError(f"selector {selector!r} matched {len(matches)} elements; expected exactly one")
    return matches[0]


def apply_operations(root: ET.Element, operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for index, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            raise ValueError(f"operation {index} must be an object")
        kind = operation.get("op")
        target = select_one(root, operation.get("selector"))
        target_id = target.get("id")

        if kind == "set-attrs":
            attrs = operation.get("attrs")
            if not isinstance(attrs, dict) or not attrs:
                raise ValueError(f"operation {index} requires non-empty attrs")
            if "id" in attrs:
                raise ValueError("changing SVG ids is not supported by the refinement template")
            for key, value in attrs.items():
                target.set(str(key), str(value))
        elif kind == "translate":
            dx = finite_number(operation.get("dx", 0), f"operation {index}.dx")
            dy = finite_number(operation.get("dy", 0), f"operation {index}.dy")
            existing = target.get("transform", "").strip()
            prefix = f"translate({compact_number(dx)} {compact_number(dy)})"
            target.set("transform", f"{prefix} {existing}".strip())
        elif kind == "scale":
            sx = finite_number(operation.get("sx"), f"operation {index}.sx")
            sy = finite_number(operation.get("sy", sx), f"operation {index}.sy")
            if sx <= 0 or sy <= 0:
                raise ValueError("scale factors must be positive")
            cx = finite_number(operation.get("cx", 0), f"operation {index}.cx")
            cy = finite_number(operation.get("cy", 0), f"operation {index}.cy")
            existing = target.get("transform", "").strip()
            prefix = (
                f"translate({compact_number(cx)} {compact_number(cy)}) "
                f"scale({compact_number(sx)} {compact_number(sy)}) "
                f"translate({compact_number(-cx)} {compact_number(-cy)})"
            )
            target.set("transform", f"{prefix} {existing}".strip())
        elif kind == "set-text":
            value = operation.get("text")
            if not isinstance(value, str):
                raise ValueError(f"operation {index}.text must be a string")
            for child in list(target):
                target.remove(child)
            target.text = value
        elif kind == "delete":
            parent_by_child = {child: parent for parent in root.iter() for child in parent}
            parent = parent_by_child.get(target)
            if parent is None:
                raise ValueError("cannot delete the SVG root")
            parent.remove(target)
        else:
            raise ValueError(f"unsupported operation {index}: {kind!r}")
        applied.append({"index": index, "op": kind, "target_id": target_id})
    return applied


def atomic_write(tree: ET.ElementTree, output: Path, overwrite: bool) -> None:
    if output.exists() and not overwrite:
        raise FileExistsError(f"output exists; pass --overwrite only after exact approval: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
        ) as handle:
            temp_path = Path(handle.name)
        ET.indent(tree, space="  ")
        tree.write(temp_path, encoding="utf-8", xml_declaration=True)
        if output.exists() and not overwrite:
            raise FileExistsError(f"output appeared during refinement: {output}")
        os.replace(temp_path, output)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root_path = project_root()
    input_path = (root_path / INPUT_RELATIVE_PATH).resolve()
    output_path = (root_path / OUTPUT_RELATIVE_PATH).resolve()
    if not input_path.is_file():
        raise SystemExit(f"input SVG not found: {input_path}")
    operations = json.loads(OPERATIONS_JSON)
    if not isinstance(operations, list) or not operations:
        raise SystemExit("OPERATIONS_JSON must be a non-empty JSON list")

    input_hash = file_sha256(input_path)
    tree = ET.parse(input_path)
    applied = apply_operations(tree.getroot(), operations)
    payload = {
        "mode": "dry-run" if args.dry_run else "apply",
        "input": str(input_path),
        "input_sha256": input_hash,
        "output": str(output_path),
        "operations": applied,
    }
    if not args.dry_run:
        atomic_write(tree, output_path, args.overwrite)
        payload["output_sha256"] = file_sha256(output_path)
        payload["bytes"] = output_path.stat().st_size
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(2)
