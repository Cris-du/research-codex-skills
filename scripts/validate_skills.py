#!/usr/bin/env python3
"""Validate repository Skill structure, local links, encoding, and public safety."""

from __future__ import annotations

import re
from pathlib import Path
import sys


EXPECTED_SKILLS = {
    "05-sci-manuscript-writing",
    "05-sci-publish",
    "05-sci-reviewer-parsing",
    "05-sci-reviewer-response",
    "build-research-figures",
    "build-research-presentations",
    "data-analysis-audit",
    "data-analysis-auto",
    "data-analysis-explanation",
    "github-research-repo",
    "manage-research-project",
    "research-project-framing",
    "research-study-design",
}

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
PRIVATE_MARKERS = (
    "codex\\科研项目",
    "活跃病毒\\03_数据与分析",
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".ps1", ".template"}


def read_utf8(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        errors.append(f"{path}: not valid UTF-8 ({exc})")
    except OSError as exc:
        errors.append(f"{path}: could not be read ({exc})")
    return None


def parse_frontmatter(text: str, path: Path, errors: list[str]) -> tuple[str, str] | None:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        errors.append(f"{path}: missing opening YAML frontmatter delimiter")
        return None
    end = normalized.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{path}: missing closing YAML frontmatter delimiter")
        return None
    frontmatter = normalized[4:end]
    name_match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)['\"]?\s*$", frontmatter)
    description_match = re.search(r"(?m)^description:\s*(.*)$", frontmatter)
    if not name_match:
        errors.append(f"{path}: frontmatter has no scalar name")
        return None
    if not description_match:
        errors.append(f"{path}: frontmatter has no description")
        return None
    return name_match.group(1).strip(), description_match.group(1).strip()


def validate_links(skill_file: Path, text: str, errors: list[str]) -> None:
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        resolved = (skill_file.parent / target).resolve(strict=False)
        if not resolved.exists():
            errors.append(f"{skill_file}: broken local link {raw_target!r}")


def validate_public_text(path: Path, text: str, errors: list[str]) -> None:
    relative = path.as_posix()
    if relative == "scripts/validate_skills.py":
        return

    lowered = text.lower()
    for marker in PRIVATE_MARKERS:
        if marker.lower() in lowered:
            errors.append(f"{path}: private or legacy marker remains: {marker!r}")

    if not relative.startswith("skills/"):
        return
    if relative.endswith("skills/github-research-repo/scripts/audit_repository.py"):
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        if WINDOWS_ABSOLUTE_PATTERN.search(line):
            errors.append(f"{path}:{line_number}: machine-specific Windows path remains")
            break


def validate_python(path: Path, text: str, errors: list[str]) -> None:
    try:
        compile(text, str(path), "exec")
    except SyntaxError as exc:
        errors.append(f"{path}:{exc.lineno}: Python syntax error: {exc.msg}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skills_root = root / "skills"
    errors: list[str] = []

    skill_dirs = {
        path.name: path
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    actual = set(skill_dirs)
    if actual != EXPECTED_SKILLS:
        missing = sorted(EXPECTED_SKILLS - actual)
        extra = sorted(actual - EXPECTED_SKILLS)
        if missing:
            errors.append(f"Missing expected Skills: {', '.join(missing)}")
        if extra:
            errors.append(f"Unexpected Skills (update validator and README intentionally): {', '.join(extra)}")

    root_readme = read_utf8(root / "README.md", errors) or ""
    for name, directory in sorted(skill_dirs.items()):
        skill_file = directory / "SKILL.md"
        text = read_utf8(skill_file, errors)
        if text is None:
            continue
        parsed = parse_frontmatter(text, skill_file, errors)
        if parsed:
            declared_name, _ = parsed
            if declared_name != name:
                errors.append(
                    f"{skill_file}: frontmatter name {declared_name!r} does not match folder {name!r}"
                )
            if not NAME_PATTERN.fullmatch(declared_name):
                errors.append(f"{skill_file}: invalid Skill name {declared_name!r}")
        validate_links(skill_file, text, errors)
        if f"`{name}`" not in root_readme:
            errors.append(f"README.md: Skill is not listed: {name}")

        agent_file = directory / "agents" / "openai.yaml"
        if agent_file.exists():
            agent_text = read_utf8(agent_file, errors)
            if agent_text is not None:
                for required in ("interface:", "display_name:", "short_description:"):
                    if required not in agent_text:
                        errors.append(f"{agent_file}: missing {required}")

    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore", ".gitattributes"}:
            continue
        text = read_utf8(path, errors)
        if text is None:
            continue
        validate_public_text(path.relative_to(root), text, errors)
        if path.suffix.lower() == ".py":
            validate_python(path.relative_to(root), text, errors)

    required_companions = (
        skills_root / "data-analysis-auto" / "SKILL.md",
        skills_root / "data-analysis-explanation" / "SKILL.md",
    )
    if not all(path.is_file() for path in required_companions):
        errors.append("data-analysis-auto and data-analysis-explanation must remain installable together")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} Skills with UTF-8, frontmatter, links, and public-path checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
