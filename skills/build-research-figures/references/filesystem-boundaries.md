# Filesystem boundaries

## Read-only upstream scope

Treat these as read-only, including all descendants:

```text
01_立项与选题论证.md
02_实验设计.md
03_数据与分析/
PROJECT.md
```

Do not rename, move, convert, rewrite, or clean upstream files. Compute hashes before and after assembly when practical to demonstrate that selected SVGs remained unchanged.

## Writable 04 scope

Write only the approved subset of:

```text
04_结果主库/图片规划.md
04_结果主库/自制图/*.svg
04_结果主库/Fig/Fig_*.svg
04_结果主库/Fig/Fig_*.txt
04_结果主库/脚本/build_Fig_*.py
04_结果主库/脚本/refine_Fig_*.py
```

Create missing `04_结果主库`, `自制图`, `Fig`, or `脚本` directories only when they were listed in the approved write preview. Do not create unannounced manifests, logs, caches, previews, or intermediate files in the project.

Use an operating-system temporary directory for layout JSON, render previews, test outputs, and atomic-write staging. Verify the temporary root before recursive cleanup.

## Conflict policy

- Treat every existing target as a conflict until the user approves that exact replacement.
- Do not use broad overwrite approval such as “update 04” to replace unrelated outputs.
- Write atomically: create a temporary sibling, verify it, then replace only the approved target.
- Keep the original intact if generation or verification fails.
- In Refine, write to a new preview target first. Replace the canonical Fig only after visual approval unless the user explicitly requests direct replacement.

## Scope isolation

Never:

- Update `PROJECT.md` directly.
- Copy 03 SVGs as standalone files into 04.
- Add journal-formatted exports to 04.
- Install software, download fonts, or access the network without separate approval.
- Delete user files as cleanup.

At completion, provide the exact changed-file list and a structured status handoff; leave project-state synchronization to `$manage-research-project`.
