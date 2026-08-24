#!/usr/bin/env python3
"""Assemble audited SVG units into one deterministic, self-contained figure."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from audit_svg_inputs import audit_one, parse_dimension, parse_view_box


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

ID_CHAR_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")
URL_ID_PATTERN = re.compile(r"url\(\s*(['\"]?)#([^)'\"\s]+)\1\s*\)")


def svg_tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def finite_number(value: Any, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(number) or (positive and number <= 0):
        qualifier = "finite and positive" if positive else "finite"
        raise ValueError(f"{label} must be {qualifier}")
    return number


def compact_number(number: float) -> str:
    return f"{number:.12g}"


def safe_id(value: str) -> str:
    cleaned = ID_CHAR_PATTERN.sub("_", value.strip())
    if not cleaned:
        cleaned = "panel"
    if not re.match(r"[A-Za-z_]", cleaned):
        cleaned = "p_" + cleaned
    return cleaned


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_box(root: ET.Element) -> tuple[float, float, float, float]:
    view_box = parse_view_box(root.get("viewBox"))
    if view_box is not None:
        return tuple(view_box)  # type: ignore[return-value]
    width = parse_dimension(root.get("width"))
    height = parse_dimension(root.get("height"))
    if width is None or height is None:
        raise ValueError("source SVG has no usable viewBox or width/height")
    return 0.0, 0.0, width, height


def replace_references(value: str, id_map: dict[str, str], *, css_text: bool = False) -> str:
    def replace_url(match: re.Match[str]) -> str:
        quote, old_id = match.groups()
        new_id = id_map.get(old_id, old_id)
        return f"url({quote}#{new_id}{quote})"

    updated = URL_ID_PATTERN.sub(replace_url, value)
    if updated.startswith("#") and updated[1:] in id_map:
        updated = "#" + id_map[updated[1:]]
    for old_id in sorted(id_map, key=len, reverse=True):
        new_id = id_map[old_id]
        if css_text:
            updated = re.sub(
                rf"(?<![A-Za-z0-9_.-])#{re.escape(old_id)}(?=\s*(?:[{{,>+~.\[:]))",
                f"#{new_id}",
                updated,
            )
        updated = re.sub(
            rf"(?<![A-Za-z0-9_.-]){re.escape(old_id)}(?=\.(?:begin|end)\b)",
            new_id,
            updated,
        )
    return updated


def prefix_ids(container: ET.Element, prefix: str) -> dict[str, str]:
    id_map: dict[str, str] = {}
    for element in container.iter():
        old_id = element.get("id")
        if old_id:
            id_map[old_id] = f"{prefix}{safe_id(old_id)}"
    for element in container.iter():
        old_id = element.get("id")
        if old_id:
            element.set("id", id_map[old_id])
        for attr_name, attr_value in list(element.attrib.items()):
            if attr_name == "id":
                continue
            element.set(attr_name, replace_references(str(attr_value), id_map))
        if local_name(element.tag) == "style" and element.text:
            element.text = replace_references(element.text, id_map, css_text=True)
    return id_map


def load_and_validate_spec(spec_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON spec: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("layout spec root must be a JSON object")

    data["width"] = finite_number(data.get("width"), "width", positive=True)
    data["height"] = finite_number(data.get("height"), "height", positive=True)
    background = data.get("background")
    if background is not None and not isinstance(background, str):
        raise ValueError("background must be a string or null")

    panels = data.get("panels")
    if not isinstance(panels, list) or not panels:
        raise ValueError("panels must be a non-empty list")
    seen_labels: set[str] = set()
    seen_slugs: set[str] = set()
    for index, panel in enumerate(panels, start=1):
        if not isinstance(panel, dict):
            raise ValueError(f"panels[{index}] must be an object")
        label = panel.get("label")
        source = panel.get("source")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"panels[{index}].label must be a non-empty string")
        if label in seen_labels:
            raise ValueError(f"duplicate panel label: {label}")
        seen_labels.add(label)
        label_slug = safe_id(label)
        if label_slug in seen_slugs:
            raise ValueError(f"panel labels collide after SVG id normalization: {label}")
        seen_slugs.add(label_slug)
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"panels[{index}].source must be a non-empty path")
        panel["x"] = finite_number(panel.get("x"), f"panels[{index}].x")
        panel["y"] = finite_number(panel.get("y"), f"panels[{index}].y")
        panel["width"] = finite_number(panel.get("width"), f"panels[{index}].width", positive=True)
        panel["height"] = finite_number(panel.get("height"), f"panels[{index}].height", positive=True)
        fit = panel.get("fit", "contain")
        if fit not in {"contain", "cover", "stretch"}:
            raise ValueError(f"panels[{index}].fit must be contain, cover, or stretch")
        panel["fit"] = fit
        if "label_x" in panel:
            panel["label_x"] = finite_number(panel["label_x"], f"panels[{index}].label_x")
        if "label_y" in panel:
            panel["label_y"] = finite_number(panel["label_y"], f"panels[{index}].label_y")

    style = data.setdefault("label_style", {})
    if not isinstance(style, dict):
        raise ValueError("label_style must be an object")
    style.setdefault("font_family", "Arial, sans-serif")
    style.setdefault("font_size", 36)
    style.setdefault("font_weight", "bold")
    style.setdefault("fill", "#000000")
    style.setdefault("offset_x", 0)
    style.setdefault("offset_y", style["font_size"])
    for key in ("font_family", "font_weight", "fill"):
        if not isinstance(style[key], str) or not style[key]:
            raise ValueError(f"label_style.{key} must be a non-empty string")
    style["font_size"] = finite_number(style["font_size"], "label_style.font_size", positive=True)
    style["offset_x"] = finite_number(style["offset_x"], "label_style.offset_x")
    style["offset_y"] = finite_number(style["offset_y"], "label_style.offset_y")
    return data


def resolve_source(spec_path: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = spec_path.parent / candidate
    return candidate.resolve(strict=False)


def build_figure(spec_path: Path, spec: dict[str, Any]) -> tuple[ET.ElementTree, list[dict[str, Any]]]:
    width = spec["width"]
    height = spec["height"]
    root = ET.Element(
        svg_tag("svg"),
        {
            "version": "1.1",
            "width": compact_number(width),
            "height": compact_number(height),
            "viewBox": f"0 0 {compact_number(width)} {compact_number(height)}",
            "role": "img",
        },
    )
    defs = ET.SubElement(root, svg_tag("defs"))
    background = spec.get("background")
    if background:
        ET.SubElement(
            root,
            svg_tag("rect"),
            {
                "id": "figure_background",
                "x": "0",
                "y": "0",
                "width": compact_number(width),
                "height": compact_number(height),
                "fill": background,
            },
        )

    reports: list[dict[str, Any]] = []
    style = spec["label_style"]
    source_hashes_before: dict[Path, str] = {}

    for index, panel in enumerate(spec["panels"], start=1):
        source = resolve_source(spec_path, panel["source"])
        audit = audit_one(source, bool(panel.get("require_editable_text", False)))
        if not audit["valid"]:
            issues = "; ".join(audit["blocking_issues"])
            raise ValueError(f"panel {panel['label']} source failed audit: {issues}")
        source_hashes_before[source] = sha256(source)

        source_tree = ET.parse(source)
        source_root = source_tree.getroot()
        min_x, min_y, source_width, source_height = source_box(source_root)
        dest_x = panel["x"]
        dest_y = panel["y"]
        dest_width = panel["width"]
        dest_height = panel["height"]
        fit = panel["fit"]

        if fit == "stretch":
            scale_x = dest_width / source_width
            scale_y = dest_height / source_height
            target_x = dest_x
            target_y = dest_y
        else:
            scale = min(dest_width / source_width, dest_height / source_height)
            if fit == "cover":
                scale = max(dest_width / source_width, dest_height / source_height)
            scale_x = scale_y = scale
            target_x = dest_x + (dest_width - source_width * scale) / 2.0
            target_y = dest_y + (dest_height - source_height * scale) / 2.0

        panel_slug = safe_id(panel["label"])
        wrapper = ET.SubElement(
            root,
            svg_tag("g"),
            {
                "id": f"panel_{panel_slug}",
                "data-panel-label": panel["label"],
                "data-panel-source": panel["source"],
            },
        )
        if fit == "cover":
            clip_id = f"clip_panel_{index}_{panel_slug}"
            clip_path = ET.SubElement(
                defs,
                svg_tag("clipPath"),
                {"id": clip_id, "clipPathUnits": "userSpaceOnUse"},
            )
            ET.SubElement(
                clip_path,
                svg_tag("rect"),
                {
                    "x": compact_number(dest_x),
                    "y": compact_number(dest_y),
                    "width": compact_number(dest_width),
                    "height": compact_number(dest_height),
                },
            )
            wrapper.set("clip-path", f"url(#{clip_id})")

        transform = (
            f"translate({compact_number(target_x)} {compact_number(target_y)}) "
            f"scale({compact_number(scale_x)} {compact_number(scale_y)}) "
            f"translate({compact_number(-min_x)} {compact_number(-min_y)})"
        )
        content_group = ET.SubElement(wrapper, svg_tag("g"), {"transform": transform})
        excluded_root_attrs = {
            "id",
            "viewBox",
            "width",
            "height",
            "version",
            "xmlns",
            "preserveAspectRatio",
        }
        for attr_name, attr_value in source_root.attrib.items():
            if local_name(attr_name) not in excluded_root_attrs and not local_name(attr_name).lower().startswith("on"):
                content_group.set(attr_name, attr_value)
        for child in source_root:
            content_group.append(copy.deepcopy(child))
        id_map = prefix_ids(content_group, f"p{index}_{panel_slug}_")

        label_x = panel.get("label_x", dest_x + style["offset_x"])
        label_y = panel.get("label_y", dest_y + style["offset_y"])
        label_element = ET.SubElement(
            root,
            svg_tag("text"),
            {
                "id": f"panel_label_{panel_slug}",
                "data-panel-label": panel["label"],
                "data-panel-label-role": "label",
                "x": compact_number(label_x),
                "y": compact_number(label_y),
                "font-family": style["font_family"],
                "font-size": compact_number(style["font_size"]),
                "font-weight": style["font_weight"],
                "fill": style["fill"],
            },
        )
        label_element.text = panel["label"]
        reports.append(
            {
                "label": panel["label"],
                "source": str(source),
                "source_sha256": source_hashes_before[source],
                "source_ids_prefixed": len(id_map),
                "fit": fit,
                "transform": transform,
                "warnings": audit["warnings"],
            }
        )

    for source, old_hash in source_hashes_before.items():
        new_hash = sha256(source)
        if new_hash != old_hash:
            raise RuntimeError(f"source changed during assembly: {source}")
    if len(defs) == 0:
        root.remove(defs)
    return ET.ElementTree(root), reports


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
            raise FileExistsError(f"output appeared during generation: {output}")
        os.replace(temp_path, output)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="UTF-8 JSON layout specification")
    parser.add_argument("--output", required=True, type=Path, help="target self-contained SVG")
    parser.add_argument("--dry-run", action="store_true", help="validate and assemble in memory without writing")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing exact target")
    args = parser.parse_args()

    spec_path = args.spec.expanduser().resolve(strict=False)
    output = args.output.expanduser().resolve(strict=False)
    try:
        spec = load_and_validate_spec(spec_path)
        tree, panels = build_figure(spec_path, spec)
        payload: dict[str, Any] = {
            "mode": "dry-run" if args.dry_run else "apply",
            "spec": str(spec_path),
            "output": str(output),
            "target_exists": output.exists(),
            "canvas": {"width": spec["width"], "height": spec["height"]},
            "panels": panels,
        }
        if not args.dry_run:
            atomic_write(tree, output, args.overwrite)
            payload["output_sha256"] = sha256(output)
            payload["bytes"] = output.stat().st_size
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # Present a concise machine-readable failure.
        print(
            json.dumps(
                {"mode": "dry-run" if args.dry_run else "apply", "error": str(exc)},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
