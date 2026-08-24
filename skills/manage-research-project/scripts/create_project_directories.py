#!/usr/bin/env python3
"""Preview or create the fixed research-project scaffold.

The scaffold contains fixed directories plus two empty root-level placeholder
files. This script never creates the project root or PROJECT.md, never writes
to an existing file, and never deletes, moves, renames, or overwrites paths.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FIXED_DIRECTORIES = (
    "03_数据与分析/skill化工作记录",
    "03_数据与分析/非skill化工作台",
    "03_数据与分析/主库/信息单元",
    "03_数据与分析/主库/图文单元/图",
    "03_数据与分析/主库/图文单元/绘图输入",
    "03_数据与分析/主库/图文单元/文本结果",
    "03_数据与分析/主库/单元解释",
    "03_数据与分析/主库备份",
    "04_结果主库/自制图",
    "04_结果主库/Fig",
    "04_结果主库/脚本",
    "05_论文全周期/投前论文成稿",
    "05_论文全周期/期刊适配",
    "05_论文全周期/审稿修回",
    "项目汇报/组会汇报",
    "项目汇报/项目汇报",
    "Git",
)

EMPTY_PLACEHOLDER_FILES = (
    "01_立项与选题论证.md",
    "02_实验设计.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preview or create the fixed research-project directories and "
            "empty 01/02 placeholder files."
        )
    )
    parser.add_argument("project_root", help="Existing project root directory")
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Create missing directories and empty placeholder files. "
            "Without this flag, only preview."
        ),
    )
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(
            json.dumps(
                {"error": "project_root_must_exist", "root": str(root)},
                ensure_ascii=False,
            )
        )
        return 2

    entries: list[dict[str, str]] = []
    conflicts: list[str] = []

    for relative in FIXED_DIRECTORIES:
        target = root.joinpath(*Path(relative).parts)
        if target.exists() and not target.is_dir():
            status = "conflict_file"
            conflicts.append(str(target))
        elif target.is_dir():
            status = "exists"
        else:
            status = "would_create"
        entries.append(
            {
                "kind": "directory",
                "relative": relative,
                "path": str(target),
                "status": status,
            }
        )

    for relative in EMPTY_PLACEHOLDER_FILES:
        target = root.joinpath(*Path(relative).parts)
        if target.exists() or target.is_symlink():
            if target.is_file() and not target.is_symlink():
                status = "exists"
            else:
                status = "conflict_not_regular_file"
                conflicts.append(str(target))
        else:
            status = "would_create"
        entries.append(
            {
                "kind": "empty_placeholder_file",
                "relative": relative,
                "path": str(target),
                "status": status,
            }
        )

    if conflicts:
        print(
            json.dumps(
                {
                    "mode": "preflight",
                    "root": str(root),
                    "entries": entries,
                    "conflicts": conflicts,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 3

    if args.apply:
        for entry in entries:
            if entry["status"] == "would_create":
                target = Path(entry["path"])
                if entry["kind"] == "directory":
                    target.mkdir(parents=True, exist_ok=False)
                else:
                    target.touch(exist_ok=False)
                entry["status"] = "created"

        failed: list[str] = []
        for entry in entries:
            target = Path(entry["path"])
            if entry["kind"] == "directory":
                valid = target.is_dir()
            else:
                valid = target.is_file() and (
                    entry["status"] != "created" or target.stat().st_size == 0
                )
            if not valid:
                failed.append(entry["path"])
        if failed:
            print(
                json.dumps(
                    {
                        "mode": "apply",
                        "root": str(root),
                        "entries": entries,
                        "verification_failed": failed,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 4

    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "preview",
                "root": str(root),
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
