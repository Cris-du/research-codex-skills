# Filesystem boundaries

## Authored project content

The only persistent project file whose content this skill may author and continue modifying is:

```text
<project-root>/PROJECT.md
```

It may also create these two root placeholders only when absent:

```text
<project-root>/01_立项与选题论证.md
<project-root>/02_实验设计.md
```

Create each as a zero-byte file. Once either exists, treat it as read-only regardless of content. Never truncate, overwrite, append to, or edit it.

The fixed initialization directories remain exactly:

```text
03_数据与分析/
03_数据与分析/skill化工作记录/
03_数据与分析/非skill化工作台/
03_数据与分析/主库/
03_数据与分析/主库/信息单元/
03_数据与分析/主库/图文单元/
03_数据与分析/主库/图文单元/图/
03_数据与分析/主库/图文单元/绘图输入/
03_数据与分析/主库/图文单元/文本结果/
03_数据与分析/主库/单元解释/
03_数据与分析/主库备份/
04_结果主库/
04_结果主库/自制图/
04_结果主库/Fig/
04_结果主库/脚本/
05_论文全周期/
05_论文全周期/投前论文成稿/
05_论文全周期/期刊适配/
05_论文全周期/审稿修回/
项目汇报/
项目汇报/组会汇报/
项目汇报/项目汇报/
Git/
```

Do not add migration, temporary, log, cache, status, date, part, Fig, journal, or review-round placeholders during initialization.

## Byte-for-byte copy exception

After the user approves an exact in-chat mapping batch, this skill may create byte-for-byte copies of selected existing materials under these destination roots:

```text
03_数据与分析/
04_结果主库/
05_论文全周期/
项目汇报/
```

Copied files are imported materials, not content authored by this skill. Preserve file bytes and modification times. Creating approved subdirectories below the allowed roots is permitted only as needed to hold selected copied materials.

Never copy into:

```text
<project-root>/
01_立项与选题论证.md
02_实验设计.md
Git/
```

Never copy outside the authoritative project root. Reject absolute destination paths, `..` traversal, symlinks, junctions, mount points, and other reparse-point traversal.

## Source safety

Sources may be outside the project root or in a nonstandard location inside it. They must be explicitly supplied by the user or unambiguous from the current conversation.

Treat every source as read-only. Never:

- move or rename it;
- edit file contents or metadata;
- delete or archive it;
- use it as a cleanup target;
- follow symlinks, junctions, or other reparse points;
- assume every source child should be copied.

Capture a selected-source snapshot before copying and verify selected source paths, sizes, and modification times afterward.

## Target conflicts

Preflight the entire approved batch before writing.

- Existing normal directory needed as a parent: allowed.
- Existing destination file: conflict, even if content appears identical.
- Existing directory where a file is planned: conflict.
- Existing file where a directory is planned: conflict.
- Two mapping items producing the same destination path: conflict.
- Destination resolving outside the project root: conflict.
- Source and destination containing one another: conflict.
- Symlink, junction, mount point, or reparse point in source or destination ancestry: conflict.
- Insufficient free space: conflict.

Any conflict stops the whole batch before copying. Never overwrite, merge, silently skip, or choose a newer file.

## Existing project materials

Except for separately approved `PROJECT.md` edits, existing project files remain read-only. Copy may add nonconflicting new paths under allowed destination roots, but may not modify existing paths.

Do not initialize Git or create anything inside `Git/`. Do not write content into 01/02 placeholders. Do not create extra reports, logs, manifests, markers, `.gitkeep`, caches, or sidecars.

## Partial failure

If a copy fails after some files were created:

- stop the remaining batch;
- report the affected mapping item, completed count, last attempted path, and destination roots;
- do not automatically delete copied business materials;
- do not claim complete success;
- require a new explicit plan before resuming or cleaning up.

## Temporary resources

Keep the reusable copy script in the skill package. Pass mapping JSON through standard input so no persistent plan file is needed.

If additional runtime resources are unavoidable:

1. create one unique task directory under the operating-system temporary area;
2. record every created absolute path;
3. run Python with `-B` or `PYTHONDONTWRITEBYTECODE=1`;
4. remove only exact temporary paths created by the current task;
5. never use wildcard deletion;
6. verify removal;
7. report cleanup failure as incomplete work.
