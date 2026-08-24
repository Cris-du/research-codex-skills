#!/usr/bin/env python3
"""Project-local reproducible build wrapper; replace all double-brace fields."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ASSEMBLER_PATH = Path(r"{{ASSEMBLER_PATH}}")
ASSEMBLER_SHA256 = "{{ASSEMBLER_SHA256}}"
OUTPUT_RELATIVE_PATH = Path(r"{{OUTPUT_RELATIVE_PATH}}")
LAYOUT_JSON = r'''{{LAYOUT_JSON}}'''


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_root() -> Path:
    # Expected location: <project>/04_结果主库/脚本/build_Fig_N.py
    return Path(__file__).resolve().parents[2]


def expanded_layout(root: Path) -> dict:
    layout = json.loads(LAYOUT_JSON)
    for panel in layout["panels"]:
        source = Path(panel["source"])
        if not source.is_absolute():
            panel["source"] = str((root / source).resolve())
    return layout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    assembler = ASSEMBLER_PATH.expanduser().resolve(strict=False)
    if not assembler.is_file():
        raise SystemExit(f"assembler not found: {assembler}")
    actual_hash = file_sha256(assembler)
    if actual_hash.lower() != ASSEMBLER_SHA256.lower():
        raise SystemExit(
            "assembler hash differs from the approved build dependency; "
            f"expected {ASSEMBLER_SHA256}, found {actual_hash}"
        )

    root = project_root()
    output = (root / OUTPUT_RELATIVE_PATH).resolve()
    layout = expanded_layout(root)
    with tempfile.TemporaryDirectory(prefix="build-research-figure-") as temp_dir:
        spec_path = Path(temp_dir) / "layout.json"
        spec_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
        command = [
            sys.executable,
            "-X",
            "utf8",
            str(assembler),
            "--spec",
            str(spec_path),
            "--output",
            str(output),
        ]
        if args.dry_run:
            command.append("--dry-run")
        if args.overwrite:
            command.append("--overwrite")
        completed = subprocess.run(command, check=False)
        return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
