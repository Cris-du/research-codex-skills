#!/usr/bin/env python3
"""Install one or more repository Skills without overwriting existing copies."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def available_skills(skills_root: Path) -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(skills_root.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def default_destination() -> Path:
    configured_root = os.environ.get("CODEX_HOME")
    codex_root = Path(configured_root).expanduser() if configured_root else Path.home() / ".codex"
    return codex_root / "skills"


def reject_symlinks(source: Path) -> None:
    if source.is_symlink():
        raise RuntimeError(f"Skill source is a symlink: {source}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"Skill contains a symlink and was not installed: {path}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install Skills from this checkout into Codex. Existing destination "
            "directories are never overwritten."
        )
    )
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="Skill name to install. Repeat to install multiple Skills; omit for all.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        help="Destination skills directory. Defaults to $CODEX_HOME/skills or ~/.codex/skills.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available Skills and exit without writing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    skills_root = repository_root() / "skills"
    available = available_skills(skills_root)

    if args.list:
        for name in available:
            print(name)
        return 0

    requested = args.skills or list(available)
    duplicate_names = sorted({name for name in requested if requested.count(name) > 1})
    if duplicate_names:
        print(f"Duplicate --skill value(s): {', '.join(duplicate_names)}", file=sys.stderr)
        return 2

    unknown = [name for name in requested if name not in available]
    if unknown:
        print(f"Unknown Skill(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Available: {', '.join(available)}", file=sys.stderr)
        return 2

    destination = (args.dest or default_destination()).expanduser().resolve(strict=False)
    if destination.exists() and not destination.is_dir():
        print(f"Destination exists but is not a directory: {destination}", file=sys.stderr)
        return 2

    conflicts = [name for name in requested if (destination / name).exists()]
    if conflicts:
        print("Nothing was installed because these destinations already exist:", file=sys.stderr)
        for name in conflicts:
            print(f"  - {destination / name}", file=sys.stderr)
        print("Back up or remove only the intended old Skill directories, then retry.", file=sys.stderr)
        return 2

    try:
        for name in requested:
            reject_symlinks(available[name])
        destination.mkdir(parents=True, exist_ok=True)
        for name in requested:
            shutil.copytree(available[name], destination / name)
            print(f"Installed {name} -> {destination / name}")
    except Exception as exc:
        print(f"Installation stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"Installed {len(requested)} Skill(s). Start a new Codex task to load them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
