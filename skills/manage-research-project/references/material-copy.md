# Material mapping and safe copy

## Purpose

Use this workflow both when first connecting an ongoing project and whenever later-discovered legacy, external, collaborator-provided, or previously missed materials need to enter the current project structure.

This is selective intake, not backup software, file synchronization, or arbitrary filesystem management.

## In-chat plan

Keep the authoritative mapping only in the conversation. Do not create a project-side manifest, migration plan, scan report, copy log, or completion marker.

For every numbered item show:

| Field | Required content |
|---|---|
| ID | Stable item number such as `01` |
| Source | Absolute source path |
| Destination | Relative path under the authoritative project root |
| Scope | Directory contents, single file, or selected descendants |
| Include | Exact selected content or glob patterns |
| Exclude | Explicitly omitted content |
| Inventory | Selected directory count, file count, and bytes |
| Evidence | Why the material belongs at the destination |
| Conflict | Existing path or version conflict |
| Risk | Absolute path dependencies, stale IDs, multiple versions, or uncertainty |
| Verification | `size` or `sha256` |
| Owning skill | Skill responsible for later scientific or editorial content work |

Explicitly list material that was inspected but will not be copied. Never default to the entire source project merely because it is available.

## JSON input

Pass one UTF-8 JSON object to `scripts/copy_project_materials.py` through standard input:

```json
{
  "project_root": "/absolute/path/to/your-project",
  "verification": "size",
  "items": [
    {
      "id": "01",
      "source": "/absolute/path/to/legacy-information",
      "destination": "03_数据与分析\\主库\\信息单元",
      "include": [],
      "exclude": ["**/__pycache__/**", "**/*.pyc"]
    }
  ]
}
```

Rules:

- `project_root` must be an existing absolute directory.
- `verification` is `size` or `sha256`.
- `items` must be a nonempty list with unique string IDs.
- `source` must be an existing absolute regular file or directory.
- `destination` must be relative to the project root and inside an allowed destination root.
- For a directory source, copy selected contents into the exact destination directory.
- For a file source, `destination` is the exact destination file path.
- `include` and `exclude` are optional lists of forward-slash relative glob patterns.
- Empty `include` means all source descendants; exclusions still apply.
- Ordinary hidden files follow the same selection rules.
- Reparse points are always rejected, not selectable.

Use explicit selection instead of broad exclusions whenever only a small portion of a source is needed.

## Preview

Run with Python bytecode disabled and without `--apply`:

```text
python -B scripts/copy_project_materials.py
```

Provide the JSON through standard input. Preview must:

1. resolve and validate the unique project root;
2. validate allowed destinations;
3. inventory selected source paths without following reparse points;
4. calculate selected directory count, file count, bytes, and required free space;
5. build every intended destination path;
6. detect all source, target, cross-item, and path-type conflicts;
7. report the exact selected and excluded scope;
8. make no filesystem changes.

Show the preview result to the user. If it differs from the approved conversation plan, stop and re-plan.

## Apply

Only after the complete preview matches an explicitly approved plan, rerun the same JSON with `--apply`:

```text
python -B scripts/copy_project_materials.py --apply
```

The script must preflight again before copying. It must create files exclusively, never open an existing target for writing. Preserve modification times.

Do not create or persist a mapping file merely to run the script. Use the conversation plan to construct standard input at execution time.

## Verification

For every item verify:

- every expected destination directory exists;
- every expected destination file exists;
- relative paths match the selected source inventory;
- file count and total bytes match;
- file sizes match, or SHA-256 matches when requested;
- no unexpected new paths were created;
- selected source file paths, sizes, and modification times are unchanged.

Copy success does not establish scientific validity, version authority, or task completion. Report whether each material is merely imported, awaiting audit, or eligible for later promotion by its owning skill.

## Clean result

The project may retain only approved copied materials and the necessary destination directories. Do not leave runtime scripts, JSON plans, manifests, logs, PID files, caches, `__pycache__`, `.pyc`, status markers, `.gitkeep`, or temporary folders unless they were themselves explicitly selected source materials.

The reusable script remains in the skill package. Remove any task-specific temporary helpers from the exact operating-system temporary path and verify cleanup.

## PROJECT.md follow-up

After successful copy, compare the imported evidence with `PROJECT.md` and propose all linked changes together. Do not write them automatically. Copied material generally begins as `进行中` or `待审计`; only user-confirmed dependable work becomes `已完成`.
