#!/usr/bin/env python3
"""Read-only publication-safety audit for a research methods and code repository."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, Iterable


MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_CONTENT_SCAN_BYTES = MAX_FILE_BYTES

BLOCKED_SUFFIXES = {
    ".7z",
    ".arrow",
    ".bam",
    ".bcf",
    ".bed",
    ".biom",
    ".bmp",
    ".cram",
    ".csv",
    ".db",
    ".doc",
    ".docx",
    ".fa",
    ".fasta",
    ".feather",
    ".fq",
    ".gz",
    ".h5",
    ".h5ad",
    ".hdf5",
    ".jpeg",
    ".jpg",
    ".loom",
    ".mat",
    ".npy",
    ".npz",
    ".parquet",
    ".pdf",
    ".pickle",
    ".pkl",
    ".png",
    ".ppt",
    ".pptx",
    ".rar",
    ".rdata",
    ".rds",
    ".sam",
    ".sav",
    ".sqlite",
    ".svg",
    ".tar",
    ".tif",
    ".tiff",
    ".tsv",
    ".vcf",
    ".xls",
    ".xlsx",
    ".zip",
}

BLOCKED_COMPOUND_SUFFIXES = {
    ".fastq.gz",
    ".fq.gz",
    ".tar.bz2",
    ".tar.gz",
    ".tar.xz",
    ".tgz",
    ".vcf.gz",
}

BLOCKED_DIR_COMPONENTS = {
    ".cache",
    ".conda",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "cache",
    "data",
    "dataset",
    "datasets",
    "env",
    "figure",
    "figures",
    "logs",
    "node_modules",
    "output",
    "outputs",
    "plot",
    "plots",
    "processed",
    "raw",
    "result",
    "results",
    "venv",
    "03_数据与分析",
    "04_结果主库",
    "05_论文全周期",
    "项目汇报",
}

BLOCKED_EXACT_NAMES = {
    ".env",
    "01_立项与选题论证.md",
    "02_实验设计.md",
    "PROJECT.md",
}

REQUIRED_README_HEADINGS = {
    "overview",
    "repository map",
    "requirements",
    "workflow",
    "data availability",
    "reproducibility boundary",
    "citation / license",
}

SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    (
        "credential-url",
        re.compile(r"\bhttps?://[^/\s:@]+:[^@\s/]+@", re.IGNORECASE),
    ),
)

ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    \b(api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)\b
    \s*[:=]\s*
    ["']?([^"'\s,\#;]{6,})
    """
)

ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\[^\r\n\"']+"),
    re.compile(r"\\\\[A-Za-z0-9._-]+\\[^\r\n\"']+"),
    re.compile(r"(?<![A-Za-z0-9])/(?:home|Users|mnt|Volumes)/[^\s\"']+"),
)

README_PLACEHOLDER_PATTERN = re.compile(
    r"<[^>\r\n]{1,100}>|\b(?:TODO|TBD|COMING SOON)\b", re.IGNORECASE
)

SAFE_CREDENTIAL_VALUES = {
    "changeme",
    "example",
    "none",
    "null",
    "placeholder",
    "redacted",
    "replace_me",
    "replace-me",
    "your_token",
    "your-token",
    "your_password",
    "your-password",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    location: str
    message: str


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            raise RuntimeError(f"Unexpected EOF while reading {size} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _discard_exact(stream: BinaryIO, size: int) -> None:
    remaining = size
    while remaining:
        chunk = stream.read(min(remaining, 1024 * 1024))
        if not chunk:
            raise RuntimeError(f"Unexpected EOF while discarding {size} bytes")
        remaining -= len(chunk)


def _is_probably_binary(data: bytes) -> bool:
    if not data:
        return False
    if b"\x00" in data:
        return True
    try:
        data.decode("utf-8")
        return False
    except UnicodeDecodeError:
        control_count = sum(
            byte < 9 or (13 < byte < 32) or byte == 127 for byte in data
        )
        return control_count / len(data) > 0.02


def _is_safe_credential_value(value: str) -> bool:
    cleaned = value.strip().strip("\"'").lower()
    if cleaned in SAFE_CREDENTIAL_VALUES:
        return True
    return (
        cleaned.startswith(("$", "${", "{{", "<", "your_", "your-"))
        or "getenv" in cleaned
        or "environ" in cleaned
        or set(cleaned) <= {"x", "*", "_", "-"}
    )


def _redact_remote_url(url: str) -> str:
    return re.sub(r"(https?://)[^/@\s]+@", r"\1***@", url)


class RepositoryAuditor:
    def __init__(self, repo: Path, public: bool) -> None:
        self.repo = repo.resolve()
        self.public = public
        self.complete = True
        self.findings: list[Finding] = []
        self._finding_keys: set[tuple[str, str, str, str, str]] = set()
        self.files_scanned = 0
        self.history_blobs_scanned = 0
        self.git_info: dict[str, object] = {
            "root": None,
            "branch": None,
            "head": None,
            "dirty_entries": 0,
            "tracked_files": 0,
            "staged_files": [],
            "upstream": None,
            "ahead": None,
            "behind": None,
            "remotes": [],
            "remote_visibility": "not checked by local audit",
        }

    def add(
        self,
        severity: str,
        code: str,
        path: str,
        message: str,
        location: str = "",
    ) -> None:
        finding = Finding(severity, code, path, location, message)
        key = (
            finding.severity,
            finding.code,
            finding.path,
            finding.location,
            finding.message,
        )
        if key not in self._finding_keys:
            self._finding_keys.add(key)
            self.findings.append(finding)
        if severity == "fatal":
            self.complete = False

    def git(
        self, args: Iterable[str], *, allow_failure: bool = False
    ) -> subprocess.CompletedProcess[str]:
        command = [
            "git",
            "-c",
            "core.quotePath=false",
            "-C",
            str(self.repo),
            *args,
        ]
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git executable is not available") from exc
        if result.returncode != 0 and not allow_failure:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"Git command failed: {' '.join(args)}: {detail}")
        return result

    def validate_repository(self) -> bool:
        if not self.repo.exists() or not self.repo.is_dir():
            self.add(
                "fatal",
                "repo-missing",
                str(self.repo),
                "Repository path does not exist or is not a directory.",
            )
            return False
        try:
            result = self.git(["rev-parse", "--show-toplevel"])
        except RuntimeError as exc:
            self.add("fatal", "not-a-git-repository", str(self.repo), str(exc))
            return False
        actual_root = Path(result.stdout.strip()).resolve()
        self.git_info["root"] = str(actual_root)
        if actual_root != self.repo:
            self.add(
                "fatal",
                "wrong-repository-root",
                str(self.repo),
                f"Git resolves to parent or different repository root: {actual_root}",
            )
            return False
        return True

    def collect_git_info(self) -> None:
        branch = self.git(
            ["symbolic-ref", "--quiet", "--short", "HEAD"], allow_failure=True
        )
        self.git_info["branch"] = branch.stdout.strip() or "(detached or unborn)"

        head = self.git(["rev-parse", "--verify", "HEAD"], allow_failure=True)
        self.git_info["head"] = head.stdout.strip() or None

        status = self.git(
            ["status", "--porcelain=v1", "--untracked-files=all"]
        ).stdout.splitlines()
        self.git_info["dirty_entries"] = len(status)

        tracked = self.git(["ls-files"]).stdout.splitlines()
        self.git_info["tracked_files"] = len(tracked)

        staged = self.git(
            ["diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB"]
        ).stdout.splitlines()
        self.git_info["staged_files"] = staged

        remote_lines = self.git(["remote", "-v"]).stdout.splitlines()
        remotes: list[dict[str, str]] = []
        for line in remote_lines:
            parts = line.split()
            if len(parts) < 3:
                continue
            name, url, operation = parts[0], parts[1], parts[2].strip("()")
            redacted = _redact_remote_url(url)
            remotes.append({"name": name, "url": redacted, "operation": operation})
            if re.search(r"https?://[^/@\s]+@", url):
                self.add(
                    "blocker",
                    "credential-in-remote-url",
                    ".git/config",
                    f"Remote {name!r} contains embedded credentials.",
                )
        self.git_info["remotes"] = remotes
        if remotes:
            self.add(
                "warning",
                "remote-visibility-unverified",
                ".git/config",
                "Local audit cannot verify GitHub visibility; check the exact remote before push or publication.",
            )

        upstream = self.git(
            [
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
            ],
            allow_failure=True,
        )
        if upstream.returncode == 0:
            upstream_name = upstream.stdout.strip()
            self.git_info["upstream"] = upstream_name
            counts = self.git(
                ["rev-list", "--left-right", "--count", f"{upstream_name}...HEAD"],
                allow_failure=True,
            )
            if counts.returncode == 0:
                fields = counts.stdout.strip().split()
                if len(fields) == 2:
                    behind, ahead = int(fields[0]), int(fields[1])
                    self.git_info["behind"] = behind
                    self.git_info["ahead"] = ahead
                    if behind:
                        self.add(
                            "blocker",
                            "local-behind-upstream",
                            ".git",
                            f"Local branch is behind its known upstream by {behind} commit(s).",
                        )

    def check_path_contract(
        self, relative_path: str, size: int, *, origin: str
    ) -> None:
        normalized = relative_path.replace("\\", "/").lstrip("./")
        components = [component for component in normalized.split("/") if component]
        lowered = [component.lower() for component in components]
        name = components[-1] if components else normalized
        lower_name = name.lower()

        if name in BLOCKED_EXACT_NAMES or lower_name == "project.md":
            self.add(
                "blocker",
                "internal-project-document",
                normalized,
                f"Internal project document is not allowed ({origin}).",
            )

        if lower_name.startswith(".env") and lower_name != ".env.example":
            self.add(
                "blocker",
                "secret-configuration-file",
                normalized,
                f"Secret-bearing environment file is not allowed ({origin}).",
            )

        blocked_components = [
            component
            for component, lower in zip(components, lowered)
            if component in BLOCKED_DIR_COMPONENTS or lower in BLOCKED_DIR_COMPONENTS
        ]
        if blocked_components:
            self.add(
                "blocker",
                "blocked-directory",
                normalized,
                f"Path contains blocked data/result/cache directory {blocked_components[0]!r} ({origin}).",
            )

        suffix = Path(lower_name).suffix
        compound_match = next(
            (
                candidate
                for candidate in BLOCKED_COMPOUND_SUFFIXES
                if lower_name.endswith(candidate)
            ),
            None,
        )
        if suffix in BLOCKED_SUFFIXES or compound_match:
            matched = compound_match or suffix
            self.add(
                "blocker",
                "blocked-file-type",
                normalized,
                f"File type {matched!r} is not allowed in the research repository ({origin}).",
            )

        if lower_name.endswith(".log"):
            self.add(
                "blocker",
                "log-file",
                normalized,
                f"Log files are not allowed ({origin}).",
            )

        if size >= MAX_FILE_BYTES:
            self.add(
                "blocker",
                "large-file",
                normalized,
                f"File is {size} bytes; the hard limit is below {MAX_FILE_BYTES} bytes ({origin}).",
            )

    def scan_content(
        self, relative_path: str, data: bytes, *, origin: str
    ) -> None:
        if _is_probably_binary(data):
            self.add(
                "blocker",
                "unknown-binary",
                relative_path,
                f"File content appears binary ({origin}).",
            )
            return

        text = data.decode("utf-8", errors="replace")
        reported_codes: set[str] = set()
        for line_number, line in enumerate(text.splitlines(), start=1):
            for code, pattern in SECRET_PATTERNS:
                if code in reported_codes:
                    continue
                if pattern.search(line):
                    self.add(
                        "blocker",
                        code,
                        relative_path,
                        f"Potential secret or credential detected ({origin}).",
                        f"line {line_number}",
                    )
                    reported_codes.add(code)

            if "credential-assignment" not in reported_codes:
                assignment = ASSIGNMENT_PATTERN.search(line)
                if assignment and not _is_safe_credential_value(assignment.group(2)):
                    self.add(
                        "blocker",
                        "credential-assignment",
                        relative_path,
                        f"Potential literal credential assigned to {assignment.group(1)!r} ({origin}).",
                        f"line {line_number}",
                    )
                    reported_codes.add("credential-assignment")

            if "absolute-local-path" not in reported_codes:
                for pattern in ABSOLUTE_PATH_PATTERNS:
                    if pattern.search(line):
                        self.add(
                            "blocker",
                            "absolute-local-path",
                            relative_path,
                            f"Machine-specific absolute path detected ({origin}).",
                            f"line {line_number}",
                        )
                        reported_codes.add("absolute-local-path")
                        break

    def scan_worktree(self) -> None:
        paths = sorted(
            self.repo.rglob("*"),
            key=lambda item: item.relative_to(self.repo).as_posix().lower(),
        )
        for path in paths:
            relative = path.relative_to(self.repo)
            if relative.parts and relative.parts[0] == ".git":
                continue
            relative_text = relative.as_posix()

            if path.is_symlink():
                target = path.resolve(strict=False)
                try:
                    inside = os.path.commonpath([str(self.repo), str(target)]) == str(
                        self.repo
                    )
                except ValueError:
                    inside = False
                severity = "warning" if inside else "blocker"
                self.add(
                    severity,
                    "symlink-review",
                    relative_text,
                    f"Symlink resolves {'inside' if inside else 'outside'} the repository: {target}",
                )
                if not inside:
                    continue

            if not path.is_file():
                continue

            self.files_scanned += 1
            try:
                size = path.stat().st_size
                with path.open("rb") as handle:
                    data = handle.read(min(size, MAX_CONTENT_SCAN_BYTES))
            except OSError as exc:
                self.add(
                    "fatal",
                    "file-read-failed",
                    relative_text,
                    f"Could not read file: {exc}",
                )
                continue

            self.check_path_contract(relative_text, size, origin="working tree")
            self.scan_content(relative_text, data, origin="working tree")

    def check_readme(self) -> None:
        readme = self.repo / "README.md"
        if not readme.is_file():
            self.add(
                "blocker",
                "readme-missing",
                "README.md",
                "A root README.md is required.",
            )
            return
        try:
            text = readme.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.add(
                "blocker",
                "readme-unreadable",
                "README.md",
                f"README.md is not readable UTF-8 text: {exc}",
            )
            return

        headings = {
            re.sub(r"\s+", " ", line[3:].strip().lower())
            for line in text.splitlines()
            if line.startswith("## ")
        }
        for heading in sorted(REQUIRED_README_HEADINGS - headings):
            self.add(
                "blocker",
                "readme-section-missing",
                "README.md",
                f"Required section is missing: {heading}",
            )

        placeholder = README_PLACEHOLDER_PATTERN.search(text)
        if placeholder:
            self.add(
                "blocker" if self.public else "warning",
                "readme-placeholder",
                "README.md",
                (
                    "README contains an unresolved placeholder; public mode requires resolution."
                    if self.public
                    else "README contains an unresolved placeholder allowed only during private development."
                ),
                f"match {placeholder.group(0)!r}",
            )

    def scan_history(self) -> None:
        objects_result = self.git(["rev-list", "--objects", "--all"])
        objects: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for line in objects_result.stdout.splitlines():
            parts = line.split(" ", 1)
            if len(parts) != 2 or not parts[1]:
                continue
            item = (parts[0], parts[1])
            if item not in seen:
                seen.add(item)
                objects.append(item)

        if not objects:
            return

        command = [
            "git",
            "-c",
            "core.quotePath=false",
            "-C",
            str(self.repo),
            "cat-file",
            "--batch",
        ]
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git executable is not available") from exc

        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None

        try:
            for object_id, historical_path in objects:
                process.stdin.write((object_id + "\n").encode("ascii"))
                process.stdin.flush()
                header = process.stdout.readline()
                if not header:
                    raise RuntimeError("git cat-file ended unexpectedly")
                fields = header.decode("utf-8", errors="replace").strip().split()
                if len(fields) < 3 or fields[1] == "missing":
                    raise RuntimeError(
                        f"Unable to read Git object {object_id}: {header!r}"
                    )
                object_type = fields[1]
                size = int(fields[2])
                read_size = (
                    min(size, MAX_CONTENT_SCAN_BYTES)
                    if object_type == "blob"
                    else 0
                )
                data = _read_exact(process.stdout, read_size)
                _discard_exact(process.stdout, size - read_size)
                separator = _read_exact(process.stdout, 1)
                if separator != b"\n":
                    raise RuntimeError(
                        f"Invalid git cat-file framing for {object_id}"
                    )
                if object_type != "blob":
                    continue

                self.history_blobs_scanned += 1
                origin = f"Git history object {object_id[:12]}"
                normalized_path = historical_path.replace("\\", "/")
                self.check_path_contract(normalized_path, size, origin=origin)
                self.scan_content(normalized_path, data, origin=origin)
        finally:
            try:
                process.stdin.close()
            except OSError:
                pass
            stderr = process.stderr.read().decode("utf-8", errors="replace").strip()
            return_code = process.wait()
            if return_code != 0:
                raise RuntimeError(
                    f"git cat-file failed with code {return_code}: {stderr}"
                )

    def run(self) -> None:
        if not self.validate_repository():
            return
        self.collect_git_info()
        self.scan_worktree()
        self.check_readme()
        if self.public:
            self.scan_history()

    def payload(self) -> dict[str, object]:
        severity_order = {"fatal": 0, "blocker": 1, "warning": 2}
        ordered = sorted(
            self.findings,
            key=lambda finding: (
                severity_order.get(finding.severity, 9),
                finding.path.lower(),
                finding.code,
                finding.location,
            ),
        )
        blockers = sum(
            finding.severity == "blocker" for finding in ordered
        )
        warnings = sum(
            finding.severity == "warning" for finding in ordered
        )
        fatals = sum(finding.severity == "fatal" for finding in ordered)
        if not self.complete or fatals:
            result = "incomplete"
        elif blockers:
            result = "blocked"
        else:
            result = "passed"
        return {
            "repo": str(self.repo),
            "mode": "public" if self.public else "private",
            "result": result,
            "complete": self.complete and fatals == 0,
            "summary": {
                "files_scanned": self.files_scanned,
                "history_blobs_scanned": self.history_blobs_scanned,
                "blockers": blockers,
                "warnings": warnings,
                "fatals": fatals,
                "max_file_bytes_exclusive": MAX_FILE_BYTES,
            },
            "git": self.git_info,
            "findings": [asdict(finding) for finding in ordered],
        }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only audit of a research methods and code repository. "
            "Use --public to include complete Git-history and final README checks."
        )
    )
    parser.add_argument("repo", type=Path, help="Path to the repository root")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Run publication-mode checks and scan all Git history",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    auditor = RepositoryAuditor(args.repo, args.public)
    try:
        auditor.run()
    except Exception as exc:  # keep a machine-readable failure result
        auditor.add(
            "fatal",
            "audit-exception",
            str(auditor.repo),
            f"{type(exc).__name__}: {exc}",
        )
    payload = auditor.payload()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["result"] == "incomplete":
        return 3
    if payload["result"] == "blocked":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
