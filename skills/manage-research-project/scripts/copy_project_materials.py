#!/usr/bin/env python3
"""Preview or safely copy an approved batch of research-project materials.

The mapping is read as one UTF-8 JSON object from standard input. Preview is
the default; --apply performs the same complete preflight and then copies files
exclusively. The script never overwrites, moves, deletes, or edits a source.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
from typing import Any, Iterable


ALLOWED_DESTINATION_ROOTS = (
    "03_数据与分析",
    "04_结果主库",
    "05_论文全周期",
    "项目汇报",
)
VERIFICATION_MODES = {"size", "sha256"}
COPY_CHUNK_SIZE = 8 * 1024 * 1024


class PlanError(Exception):
    """The requested batch is invalid and no file should be copied."""


class ApplyError(Exception):
    """Apply failed after it may have created one or more target paths."""

    def __init__(self, message: str, item_id: str | None, last_path: str | None):
        super().__init__(message)
        self.item_id = item_id
        self.last_path = last_path
        self.created_directories = 0
        self.created_files = 0


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def path_key(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def is_within(path: Path, parent: Path) -> bool:
    try:
        return os.path.commonpath([path_key(path), path_key(parent)]) == path_key(parent)
    except ValueError:
        return False


def is_reparse_point(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        isjunction = getattr(os.path, "isjunction", None)
        if isjunction is not None and isjunction(path):
            return True
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        return bool(attributes & flag)
    except OSError as exc:
        raise PlanError(f"无法检查路径是否为重解析点: {path}: {exc}") from exc


def reject_reparse_ancestry(path: Path, label: str) -> None:
    """Reject every existing reparse point from the filesystem anchor to path."""
    if not path.is_absolute():
        raise PlanError(f"{label}必须是绝对路径: {path}")
    parts = path.parts
    current = Path(parts[0])
    candidates = [current]
    for part in parts[1:]:
        current = current / part
        candidates.append(current)
    for candidate in candidates:
        try:
            exists = candidate.exists() or candidate.is_symlink()
        except OSError as exc:
            raise PlanError(f"无法检查{label}路径: {candidate}: {exc}") from exc
        if exists and is_reparse_point(candidate):
            raise PlanError(f"{label}经过符号链接、junction 或重解析点: {candidate}")


def normalized_absolute_path(raw: Any, label: str, must_exist: bool = True) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise PlanError(f"{label}必须是非空字符串")
    original = Path(raw)
    if not original.is_absolute():
        raise PlanError(f"{label}必须是绝对路径: {raw}")
    if ".." in original.parts:
        raise PlanError(f"{label}不能包含 '..': {raw}")
    lexical = Path(os.path.abspath(os.path.normpath(raw)))
    reject_reparse_ancestry(lexical, label)
    try:
        return lexical.resolve(strict=must_exist)
    except OSError as exc:
        raise PlanError(f"无法解析{label}: {lexical}: {exc}") from exc


def destination_path(project_root: Path, raw: Any, item_id: str) -> tuple[Path, str]:
    if not isinstance(raw, str) or not raw.strip():
        raise PlanError(f"条目 {item_id} 的 destination 必须是非空字符串")
    relative = Path(raw)
    if relative.is_absolute():
        raise PlanError(f"条目 {item_id} 的 destination 必须是项目内相对路径: {raw}")
    if ".." in relative.parts:
        raise PlanError(f"条目 {item_id} 的 destination 不能包含 '..': {raw}")
    clean_parts = tuple(part for part in relative.parts if part not in ("", "."))
    if not clean_parts:
        raise PlanError(f"条目 {item_id} 不能复制到项目根目录")
    if clean_parts[0] not in ALLOWED_DESTINATION_ROOTS:
        allowed = "、".join(ALLOWED_DESTINATION_ROOTS)
        raise PlanError(f"条目 {item_id} 的 destination 不在允许根中（{allowed}）: {raw}")
    clean_relative = Path(*clean_parts)
    lexical = Path(os.path.abspath(os.path.normpath(str(project_root / clean_relative))))
    if not is_within(lexical, project_root) or path_key(lexical) == path_key(project_root):
        raise PlanError(f"条目 {item_id} 的 destination 越出项目根目录: {raw}")
    reject_reparse_ancestry(lexical, f"条目 {item_id} 的目标")
    try:
        resolved = lexical.resolve(strict=False)
    except OSError as exc:
        raise PlanError(f"无法解析条目 {item_id} 的目标: {lexical}: {exc}") from exc
    if not is_within(resolved, project_root):
        raise PlanError(f"条目 {item_id} 的 destination 解析后越界: {raw}")
    return resolved, clean_relative.as_posix()


def parse_patterns(value: Any, label: str, item_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise PlanError(f"条目 {item_id} 的 {label} 必须是非空字符串列表")
    patterns: list[str] = []
    for raw in value:
        pattern = raw.replace("\\", "/").strip()
        while pattern.startswith("./"):
            pattern = pattern[2:]
        pattern = pattern.strip("/")
        if not pattern or pattern == ".." or pattern.startswith("../") or "/../" in pattern:
            raise PlanError(f"条目 {item_id} 的 {label} 含无效模式: {raw}")
        patterns.append(pattern)
    return patterns


def matches_pattern(relative: str, pattern: str) -> bool:
    relative = relative.replace("\\", "/").strip("/")
    pattern = pattern.replace("\\", "/").strip("/")
    variants = [pattern]
    if pattern.startswith("**/"):
        variants.append(pattern[3:])
    for candidate in variants:
        if fnmatch.fnmatchcase(relative, candidate):
            return True
        if candidate.endswith("/**"):
            base = candidate[:-3].rstrip("/")
            if fnmatch.fnmatchcase(relative, base) or fnmatch.fnmatchcase(relative, base + "/*"):
                return True
    return False


def selected_by_patterns(relative: str, include: list[str], exclude: list[str]) -> bool:
    relative_path = Path(relative)
    candidates = [relative_path.as_posix()]
    parent = relative_path.parent
    while str(parent) not in ("", "."):
        candidates.append(parent.as_posix())
        parent = parent.parent
    if exclude and any(
        matches_pattern(candidate, pattern) for candidate in candidates for pattern in exclude
    ):
        return False
    return not include or any(matches_pattern(relative, pattern) for pattern in include)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(COPY_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_snapshot(path: Path, relative: str, with_hash: bool) -> dict[str, Any]:
    try:
        info = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise PlanError(f"无法读取源文件状态: {path}: {exc}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise PlanError(f"源条目不是普通文件: {path}")
    return {
        "path": path,
        "relative": relative,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "sha256": sha256_file(path) if with_hash else None,
    }


def inventory_directory(
    source: Path, include: list[str], exclude: list[str], with_hash: bool
) -> tuple[list[str], list[dict[str, Any]], int, int]:
    all_dirs: list[str] = []
    all_files: list[tuple[Path, str]] = []
    for root_text, dir_names, file_names in os.walk(source, topdown=True, followlinks=False):
        root = Path(root_text)
        dir_names.sort()
        file_names.sort()
        for name in list(dir_names):
            child = root / name
            if is_reparse_point(child):
                raise PlanError(f"源目录包含不可跟随的符号链接、junction 或重解析点: {child}")
            relative = child.relative_to(source).as_posix()
            all_dirs.append(relative)
        for name in file_names:
            child = root / name
            if is_reparse_point(child):
                raise PlanError(f"源目录包含不可复制的符号链接或重解析点: {child}")
            relative = child.relative_to(source).as_posix()
            all_files.append((child, relative))

    selected_files: list[dict[str, Any]] = []
    for path, relative in all_files:
        if selected_by_patterns(relative, include, exclude):
            selected_files.append(file_snapshot(path, relative, with_hash))

    selected_dirs: set[str] = set()
    if include:
        for relative in all_dirs:
            if selected_by_patterns(relative, include, exclude):
                selected_dirs.add(relative)
    else:
        for relative in all_dirs:
            if not any(matches_pattern(relative, pattern) for pattern in exclude):
                selected_dirs.add(relative)

    for file_info in selected_files:
        parent = Path(file_info["relative"]).parent
        while str(parent) not in ("", "."):
            selected_dirs.add(parent.as_posix())
            parent = parent.parent
    for relative in list(selected_dirs):
        parent = Path(relative).parent
        while str(parent) not in ("", "."):
            selected_dirs.add(parent.as_posix())
            parent = parent.parent

    selected_dir_list = sorted(selected_dirs, key=lambda value: (len(Path(value).parts), value))
    excluded_dirs = len(all_dirs) - len(selected_dirs.intersection(all_dirs))
    excluded_files = len(all_files) - len(selected_files)
    return selected_dir_list, selected_files, excluded_dirs, excluded_files


def required_parent_dirs(project_root: Path, target: Path, target_is_directory: bool) -> list[Path]:
    end = target if target_is_directory else target.parent
    result: list[Path] = []
    current = end
    while path_key(current) != path_key(project_root):
        result.append(current)
        current = current.parent
        if not is_within(current, project_root):
            raise PlanError(f"目标父目录越出项目根目录: {target}")
    result.reverse()
    return result


def paths_overlap(first: Path, second: Path) -> bool:
    return is_within(first, second) or is_within(second, first)


def build_item(
    raw_item: Any, project_root: Path, verification: str, seen_ids: set[str]
) -> dict[str, Any]:
    if not isinstance(raw_item, dict):
        raise PlanError("items 中的每个条目必须是对象")
    item_id = raw_item.get("id")
    if not isinstance(item_id, str) or not item_id.strip():
        raise PlanError("每个条目都必须有非空字符串 id")
    item_id = item_id.strip()
    if item_id in seen_ids:
        raise PlanError(f"条目 id 重复: {item_id}")
    seen_ids.add(item_id)

    source = normalized_absolute_path(raw_item.get("source"), f"条目 {item_id} 的 source")
    if not source.is_file() and not source.is_dir():
        raise PlanError(f"条目 {item_id} 的 source 不是普通文件或目录: {source}")
    if is_reparse_point(source):
        raise PlanError(f"条目 {item_id} 的 source 是重解析点: {source}")
    target, target_relative = destination_path(project_root, raw_item.get("destination"), item_id)
    if paths_overlap(source, target):
        raise PlanError(f"条目 {item_id} 的 source 与 destination 相同或互相包含")

    include = parse_patterns(raw_item.get("include", []), "include", item_id)
    exclude = parse_patterns(raw_item.get("exclude", []), "exclude", item_id)
    with_hash = verification == "sha256"
    if source.is_file():
        source_relative = source.name
        if not selected_by_patterns(source_relative, include, exclude):
            raise PlanError(f"条目 {item_id} 的 include/exclude 排除了唯一源文件")
        source_dirs: list[str] = []
        source_files = [file_snapshot(source, source_relative, with_hash)]
        excluded_dirs = 0
        excluded_files = 0
        target_dirs = required_parent_dirs(project_root, target, False)
        target_files = [(source_files[0], target)]
        source_kind = "file"
        selected_directory_count = 0
    else:
        source_dirs, source_files, excluded_dirs, excluded_files = inventory_directory(
            source, include, exclude, with_hash
        )
        if include and not source_dirs and not source_files:
            raise PlanError(f"条目 {item_id} 的 include 没有选中任何源材料")
        target_dirs = required_parent_dirs(project_root, target, True)
        target_dirs.extend(target / Path(relative) for relative in source_dirs)
        target_files = [(info, target / Path(info["relative"])) for info in source_files]
        source_kind = "directory"
        selected_directory_count = 1 + len(source_dirs)

    # De-duplicate directories within one item while preserving shallow-first order.
    directory_map = {path_key(path): path for path in target_dirs}
    target_dirs = sorted(directory_map.values(), key=lambda path: (len(path.parts), path_key(path)))
    total_bytes = sum(info["size"] for info in source_files)
    return {
        "id": item_id,
        "source": source,
        "source_kind": source_kind,
        "destination": target,
        "destination_relative": target_relative,
        "include": include,
        "exclude": exclude,
        "source_dirs": source_dirs,
        "source_files": source_files,
        "target_dirs": target_dirs,
        "target_files": target_files,
        "directory_count": selected_directory_count,
        "file_count": len(source_files),
        "bytes": total_bytes,
        "excluded_directory_count": excluded_dirs,
        "excluded_file_count": excluded_files,
    }


def existing_path_type(path: Path) -> str | None:
    if path.is_symlink():
        return "reparse"
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise PlanError(f"无法检查目标路径: {path}: {exc}") from exc
    if is_reparse_point(path):
        return "reparse"
    if stat.S_ISDIR(info.st_mode):
        return "directory"
    if stat.S_ISREG(info.st_mode):
        return "file"
    return "special"


def preflight_targets(items: list[dict[str, Any]], project_root: Path) -> tuple[list[str], int]:
    conflicts: list[str] = []
    planned_files: dict[str, tuple[str, Path]] = {}
    new_directories: dict[str, tuple[str, Path]] = {}

    for item in items:
        item_id = item["id"]
        for directory in item["target_dirs"]:
            if not is_within(directory, project_root):
                conflicts.append(f"条目 {item_id} 的目标目录越界: {directory}")
                continue
            try:
                reject_reparse_ancestry(directory, f"条目 {item_id} 的目标目录")
                kind = existing_path_type(directory)
            except PlanError as exc:
                conflicts.append(str(exc))
                continue
            if kind is None:
                key = path_key(directory)
                prior = new_directories.get(key)
                if prior and prior[0] != item_id:
                    conflicts.append(
                        f"条目 {prior[0]} 与 {item_id} 会创建同一目标目录: {directory}"
                    )
                else:
                    new_directories[key] = (item_id, directory)
            elif kind != "directory":
                conflicts.append(f"条目 {item_id} 需要目录但目标是 {kind}: {directory}")

        for _, target in item["target_files"]:
            if not is_within(target, project_root):
                conflicts.append(f"条目 {item_id} 的目标文件越界: {target}")
                continue
            try:
                reject_reparse_ancestry(target, f"条目 {item_id} 的目标文件")
                kind = existing_path_type(target)
            except PlanError as exc:
                conflicts.append(str(exc))
                continue
            key = path_key(target)
            prior = planned_files.get(key)
            if prior:
                conflicts.append(f"条目 {prior[0]} 与 {item_id} 会创建同一目标文件: {target}")
            else:
                planned_files[key] = (item_id, target)
            if kind is not None:
                conflicts.append(f"条目 {item_id} 的目标文件已存在（{kind}）: {target}")

    for file_key, (file_item, file_path) in planned_files.items():
        if file_key in new_directories:
            dir_item, _ = new_directories[file_key]
            conflicts.append(
                f"条目 {file_item} 的文件与条目 {dir_item} 的目录目标类型冲突: {file_path}"
            )
        for dir_key, (dir_item, dir_path) in new_directories.items():
            if dir_key != file_key and is_within(dir_path, file_path):
                conflicts.append(
                    f"条目 {file_item} 的文件会成为条目 {dir_item} 目标目录的父路径: {file_path}"
                )

    required_bytes = sum(item["bytes"] for item in items)
    try:
        free_bytes = shutil.disk_usage(project_root).free
    except OSError as exc:
        conflicts.append(f"无法检查项目磁盘可用空间: {exc}")
        free_bytes = 0
    if required_bytes > free_bytes:
        conflicts.append(f"目标磁盘空间不足: 需要 {required_bytes} 字节，可用 {free_bytes} 字节")
    return conflicts, free_bytes


def public_item(item: dict[str, Any], verification: str) -> dict[str, Any]:
    return {
        "id": item["id"],
        "source": str(item["source"]),
        "source_kind": item["source_kind"],
        "destination": item["destination_relative"],
        "include": item["include"],
        "exclude": item["exclude"],
        "selected": {
            "directories": item["directory_count"],
            "files": item["file_count"],
            "bytes": item["bytes"],
        },
        "excluded": {
            "directories": item["excluded_directory_count"],
            "files": item["excluded_file_count"],
        },
        "verification": verification,
    }


def parse_plan() -> tuple[Path, str, list[dict[str, Any]], int]:
    try:
        raw_text = sys.stdin.buffer.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PlanError(f"标准输入不是有效 UTF-8: {exc}") from exc
    if not raw_text.strip():
        raise PlanError("标准输入必须提供一个 JSON 映射对象")
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise PlanError(f"JSON 无效: 第 {exc.lineno} 行第 {exc.colno} 列: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise PlanError("顶层 JSON 必须是对象")
    project_root = normalized_absolute_path(payload.get("project_root"), "project_root")
    if not project_root.is_dir():
        raise PlanError(f"project_root 不是目录: {project_root}")
    verification = payload.get("verification", "size")
    if verification not in VERIFICATION_MODES:
        raise PlanError("verification 只能是 'size' 或 'sha256'")
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise PlanError("items 必须是非空列表")
    seen_ids: set[str] = set()
    items = [build_item(item, project_root, verification, seen_ids) for item in raw_items]
    conflicts, free_bytes = preflight_targets(items, project_root)
    if conflicts:
        raise PlanError("完整批次预检失败:\n- " + "\n- ".join(conflicts))
    return project_root, verification, items, free_bytes


def verify_source_snapshot(item: dict[str, Any], verification: str) -> None:
    for before in item["source_files"]:
        path = before["path"]
        try:
            after = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise ApplyError(f"复制后无法复核源文件: {path}: {exc}", item["id"], str(path)) from exc
        if after.st_size != before["size"] or after.st_mtime_ns != before["mtime_ns"]:
            raise ApplyError(f"复制期间源文件大小或修改时间发生变化: {path}", item["id"], str(path))
        if verification == "sha256" and sha256_file(path) != before["sha256"]:
            raise ApplyError(f"复制期间源文件 SHA-256 发生变化: {path}", item["id"], str(path))


def apply_plan(
    items: list[dict[str, Any]], verification: str
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    created_dirs: list[str] = []
    created_files: list[str] = []
    created_keys: set[str] = set()
    current_item: str | None = None
    last_path: str | None = None
    try:
        expected_new_keys: set[str] = set()
        for item in items:
            for directory in item["target_dirs"]:
                if existing_path_type(directory) is None:
                    expected_new_keys.add(path_key(directory))
            for _, target in item["target_files"]:
                expected_new_keys.add(path_key(target))

        all_directories: list[tuple[str, Path]] = []
        for item in items:
            all_directories.extend((item["id"], path) for path in item["target_dirs"])
        all_directories.sort(key=lambda entry: (len(entry[1].parts), path_key(entry[1])))
        for item_id, directory in all_directories:
            current_item = item_id
            last_path = str(directory)
            key = path_key(directory)
            kind = existing_path_type(directory)
            if kind == "directory":
                if key in expected_new_keys:
                    raise ApplyError(
                        f"应用阶段原计划新建的目录已被外部创建: {directory}", item_id, last_path
                    )
                continue
            if kind is not None:
                raise ApplyError(f"应用阶段目标目录发生冲突（{kind}）: {directory}", item_id, last_path)
            os.mkdir(directory)
            created_keys.add(key)
            created_dirs.append(str(directory))

        for item in items:
            current_item = item["id"]
            for source_info, target in item["target_files"]:
                last_path = str(target)
                with source_info["path"].open("rb") as source_handle:
                    try:
                        target_handle = target.open("xb")
                    except FileExistsError as exc:
                        raise ApplyError(f"应用阶段目标文件已存在: {target}", current_item, last_path) from exc
                    created_files.append(str(target))
                    created_keys.add(path_key(target))
                    with target_handle:
                        shutil.copyfileobj(source_handle, target_handle, COPY_CHUNK_SIZE)
                        target_handle.flush()
                        os.fsync(target_handle.fileno())
                shutil.copystat(source_info["path"], target, follow_symlinks=False)

        verification_results: list[dict[str, Any]] = []
        for item in items:
            current_item = item["id"]
            for directory in item["target_dirs"]:
                last_path = str(directory)
                if existing_path_type(directory) != "directory":
                    raise ApplyError(f"验证时目标目录缺失或类型错误: {directory}", current_item, last_path)
            verified_bytes = 0
            for source_info, target in item["target_files"]:
                last_path = str(target)
                if existing_path_type(target) != "file":
                    raise ApplyError(f"验证时目标文件缺失或类型错误: {target}", current_item, last_path)
                target_size = target.stat(follow_symlinks=False).st_size
                if target_size != source_info["size"]:
                    raise ApplyError(f"目标文件大小与源文件不符: {target}", current_item, last_path)
                if verification == "sha256" and sha256_file(target) != source_info["sha256"]:
                    raise ApplyError(f"目标文件 SHA-256 与源文件不符: {target}", current_item, last_path)
                verified_bytes += target_size
            verify_source_snapshot(item, verification)
            verification_results.append(
                {
                    "id": item["id"],
                    "directories": item["directory_count"],
                    "files": item["file_count"],
                    "bytes": verified_bytes,
                    "verification": verification,
                    "source_snapshot_unchanged": True,
                }
            )
        if expected_new_keys != created_keys:
            raise ApplyError("内部验证发现计划外或缺失的创建路径", current_item, last_path)
        return verification_results, created_dirs, created_files
    except ApplyError as exc:
        exc.created_directories = len(created_dirs)
        exc.created_files = len(created_files)
        raise
    except Exception as exc:
        failure = ApplyError(str(exc), current_item, last_path)
        failure.created_directories = len(created_dirs)
        failure.created_files = len(created_files)
        raise failure from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从标准输入读取 JSON；默认预演，--apply 才安全复制已批准材料。"
    )
    parser.add_argument("--apply", action="store_true", help="完整预检通过后执行复制")
    args = parser.parse_args()

    try:
        project_root, verification, items, free_bytes = parse_plan()
    except PlanError as exc:
        emit({"status": "preflight_failed", "applied": False, "error": str(exc)})
        return 2

    public_items = [public_item(item, verification) for item in items]
    total_bytes = sum(item["bytes"] for item in items)
    if not args.apply:
        emit(
            {
                "status": "preview_ok",
                "applied": False,
                "project_root": str(project_root),
                "verification": verification,
                "items": public_items,
                "totals": {
                    "items": len(items),
                    "directories": sum(item["directory_count"] for item in items),
                    "files": sum(item["file_count"] for item in items),
                    "bytes": total_bytes,
                    "free_bytes": free_bytes,
                },
            }
        )
        return 0

    try:
        verified, created_dirs, created_files = apply_plan(items, verification)
    except ApplyError as exc:
        emit(
            {
                "status": "apply_failed_partial_state_possible",
                "applied": True,
                "error": str(exc),
                "item_id": exc.item_id,
                "last_path": exc.last_path,
                "created": {
                    "directories": exc.created_directories,
                    "files": exc.created_files,
                },
                "destination_roots": sorted(
                    {item["destination_relative"].split("/", 1)[0] for item in items}
                ),
                "instruction": "停止后续批次；不要自动删除已创建的业务材料。",
            }
        )
        return 3

    emit(
        {
            "status": "applied_and_verified",
            "applied": True,
            "project_root": str(project_root),
            "verification": verification,
            "items": public_items,
            "verification_results": verified,
            "created": {"directories": len(created_dirs), "files": len(created_files)},
            "source_unchanged": True,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
