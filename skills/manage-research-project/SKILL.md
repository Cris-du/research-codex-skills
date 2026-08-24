---
name: manage-research-project
description: >-
  Explicitly invoked project cockpit for one research-paper project. Initialize and maintain the fixed project scaffold and root PROJECT.md; scan or resume project context; review progress and next actions; record confirmed cancellations; plan selected legacy, external, or previously missed materials in the conversation; and, after explicit approval, safely copy the selected materials into approved project destinations while leaving sources unchanged. Use only when the user explicitly invokes $manage-research-project. Once opened, keep it active throughout the current Codex task until the user explicitly closes it or explicitly invokes another skill, which closes this skill automatically before the other skill proceeds. Always begin read-only. Before any write or copy, show the exact in-chat plan and obtain explicit approval. Never move, rename, delete, merge, edit, or overwrite existing business materials; never copy into 01, 02, Git, or arbitrary project-root paths.
---

# Manage Research Project

维护一个科研论文项目的固定骨架、根目录 `PROJECT.md` 和材料接入状态。让用户能够快速知道 01–05 推进到哪里、当前事项、下一步、卡点、取消方向，以及外部或历史材料如何接入当前体系。

本 skill 可以：

- 初始化和审计固定项目骨架；
- 创建并持续维护 `PROJECT.md`；
- 在会话中规划历史、外部或遗漏材料的映射；
- 经明确批准后，把选定材料按字节复制到允许的项目位置，源文件保持不动；
- 在同一 Codex 任务中保持项目管理开启。

本 skill 不负责提出科学假设、设计实验、决定分析方法、设计图片、撰写论文正文或修改已复制材料的内容。

## 显式开启和会话状态

只在用户显式调用 `$manage-research-project` 时开启。不要隐式启动。

开启后：

1. 简短说明“00科研项目驾驶舱已开启”。
2. 从只读开始。
3. 根据用户明确路径或无歧义上下文确定唯一项目根目录。
4. 在当前 Codex 任务的后续多轮对话中持续保持开启，不再每轮询问是否关闭。

它不是后台程序。新的 Codex 任务默认关闭，必须重新显式调用。

只有以下两种情况关闭：

1. 用户明确要求关闭 `$manage-research-project`；
2. 用户显式调用另一个 skill。

检测到用户显式调用另一个 skill 时：

- 不再启动新的项目管理、复制或写入动作；
- 尚未开始的已批准批次作废；
- 已在运行的单个文件操作先到达安全边界，不强制中断正在写入的文件；
- 不自动同步 `PROJECT.md`；
- 简短说明驾驶舱已为避免能力冲突而自动关闭；
- 后续只按新 skill 执行；
- 新 skill 结束后不要自动重新开启驾驶舱。

同一条消息同时显式调用本 skill 和另一个 skill 时，另一个 skill 优先，本 skill 保持关闭。普通聊天、工具调用、App 调用或其他 skill 的隐式使用不构成关闭条件。

## 写入和复制确认门

仅仅调用本 skill 不代表允许修改或复制文件。

每次创建固定骨架或写入 `PROJECT.md` 前，必须展示：

- 准确项目根目录；
- 准备创建的每个目录；
- 准备创建的每个零字节占位文件；
- 完整 `PROJECT.md` 草稿或精确字段级修改；
- 已确认事实、推断和未知内容；
- 冲突、保持不动的路径和本批明确不做的事情。

每次复制材料前，必须在会话中展示编号映射表，包括：

- 绝对源路径；
- 项目根目录内的目标路径；
- 复制整个目录、单个文件还是明确选择的子路径；
- 包含和排除内容；
- 文件数、目录数和总字节数；
- 目标冲突、版本风险、绝对路径依赖和负责后续内容处理的 skill；
- 验证方式；
- 本批明确不复制的材料。

得到明确批准后，只执行已经展示并获批的部分。用户在同一条消息中对完整计划作出的明确执行指令可以构成批准。含糊回复、沉默或切换话题不构成批准。

规划只保留在会话中。不得在项目内创建迁移清单、扫描报告、复制日志、状态标记或 sidecar 文件。

## 请求类型和必读资源

选择一个主要类型：

- 初始化：没有可靠的 `PROJECT.md`，或用户要求启动、接入项目；
- 同步：在工作、决定、取消、复制或项目扫描后更新状态；
- 读取状态：只读说明当前进度、下一步、卡点、待审计和取消事项；
- 审计目录：比较实际项目与固定骨架；
- 材料映射：规划历史、外部或后来发现的材料如何进入当前体系；
- 安全复制：执行已经明确批准的编号映射批次。

所有类型都要阅读 [references/initialization-and-sync.md](references/initialization-and-sync.md)。起草或修改 `PROJECT.md` 前阅读 [references/project-md-rules.md](references/project-md-rules.md)。任何文件操作前阅读 [references/filesystem-boundaries.md](references/filesystem-boundaries.md)。规划或执行材料复制前还要阅读 [references/material-copy.md](references/material-copy.md)。

## 固定项目骨架

项目根目录由用户创建。初始化时固定骨架保持如下，不增加迁移、临时、日志或状态目录：

    <project-root>/
    ├── 01_立项与选题论证.md
    ├── 02_实验设计.md
    ├── 03_数据与分析/
    │   ├── skill化工作记录/
    │   ├── 非skill化工作台/
    │   ├── 主库/
    │   │   ├── 信息单元/
    │   │   ├── 图文单元/
    │   │   │   ├── 图/
    │   │   │   ├── 绘图输入/
    │   │   │   └── 文本结果/
    │   │   └── 单元解释/
    │   └── 主库备份/
    ├── 04_结果主库/
    │   ├── 自制图/
    │   ├── Fig/
    │   └── 脚本/
    ├── 05_论文全周期/
    │   ├── 投前论文成稿/
    │   ├── 期刊适配/
    │   └── 审稿修回/
    ├── 项目汇报/
    │   ├── 组会汇报/
    │   └── 项目汇报/
    └── Git/

不要为日期、时间戳、part、Fig、期刊或审稿轮次创建字面占位目录。故事层、证据层、展示层、数据层、技术路线层、单项分析和分图是 `PROJECT.md` 中的管理结构，不是初始化目录。

`01_立项与选题论证.md` 和 `02_实验设计.md` 只能在缺失时创建严格零字节空文件。本 skill 创建后不得修改或覆盖；具体内容由各自负责的 skill 维护。`Git/` 在 Git skill 工作前保持为空。

得到批准后，优先使用 [scripts/create_project_directories.py](scripts/create_project_directories.py)。不带 `--apply` 只预览，带 `--apply` 才创建已批准的完整批次。

## PROJECT.md 所有权

`<project-root>/PROJECT.md` 是本 skill 唯一可以创作并持续修改内容的项目文件。复制能力是例外的“字节级材料接入”：只能把用户选定的现有文件原样复制到允许目标，不得编辑、合并或重新生成其内容。

其他 skill 可以读取并报告状态变化，但不能直接写入 `PROJECT.md`；本 skill 也不能替其他 skill 创作 01–05 业务内容。

[assets/PROJECT.template.md](assets/PROJECT.template.md) 是完整结构模板。实际 `PROJECT.md` 必须使用真实项目名称和已确认目标，保留顶部摘要、01–05、状态说明和取消记录；没有真实任务时使用真实短句，不得写入示例任务、尖括号占位符、虚构路径或未经确认的科学内容。

只允许五种状态：待办、进行中、待审计、已完成、取消。文件存在或复制成功不等于任务已完成。复制进来的工作默认仍需根据证据判断为进行中或待审计；只有工作和必要检查都完成且用户确认可依赖时，才标为已完成。

取消事项保留在原任务块，并记录原因、能否复用和取消时间，同时在文末建立索引。

## 材料映射和安全复制

复制能力既可用于项目初次接入，也可用于项目推进中后来发现的历史文件、外部数据、合作者材料、旧结果或遗漏备份。它不是后台同步工具，不会自动扫描用户未指定的计算机位置。

只复制规划中明确选中的内容，不假设整个来源目录都需要接入。源路径必须由用户明确提供或来自无歧义上下文，并始终只读。

允许的目标根为：

- `03_数据与分析/`；
- `04_结果主库/`；
- `05_论文全周期/`；
- `项目汇报/`。

禁止复制到：

- 项目根目录的任意新业务路径；
- `01_立项与选题论证.md`；
- `02_实验设计.md`；
- `Git/`；
- 项目根目录之外；
- 任何符号链接、junction 或其他重解析点经过的路径。

复制时绝不移动、删除、重命名、合并、修改或覆盖源与目标材料。非空目标可以接入无冲突的新相对路径；发现任意同名文件、文件/目录类型冲突或重复目标时，停止整个批次并回到会话说明。

规划和执行优先使用 [scripts/copy_project_materials.py](scripts/copy_project_materials.py)。映射 JSON 通过标准输入传入，不落地为项目文件；用 Python `-B` 运行。脚本默认只预览，只有完整预检通过且计划已获批准时才带 `--apply`。

复制后验证相对路径、目录数、文件数、字节数、选定的哈希策略、源文件前后快照和计划外新增路径。复制成功后不要自动同步 `PROJECT.md`；先展示联动修改并重新获得批准。

## 进行中项目和同步

根据材料实际含义判断项目阶段，不能只看目录名称、整齐程度或文件数量。

对进行中或目录杂乱的项目：

- 为每项判断提供证据路径；
- 区分已确认事实、推断和未知；
- 将真实分析、Fig、稿件和取消事项映射到 `PROJECT.md`；
- 对位置不合适的材料展示来源、目标、理由、风险和负责 skill；
- 未获批准前保持只读；
- 复制获批内容时保持源材料不动。

一次 `PROJECT.md` 同步要联动检查：具体任务状态、任务内部进度/下一步/卡点/结果/路径、所属大标题状态、顶部“目前主要做到”“现在在做”“最近更新时间”，以及取消事项的原块和文末索引。

不要自行发明科学问题、实验设计、分析步骤、图片目的或论文内容。只整理用户、可靠材料或负责对应工作的 skill 已确认的信息。

## 临时资源和干净结果

固定通用脚本保留在本 skill 的 `scripts/` 内，不复制进科研项目。

单次任务若确需生成辅助脚本、标准输入内容之外的临时配置、日志或缓存，只能放入操作系统下唯一临时目录。记录本次创建的每个绝对路径；任务结束前只删除本次创建的精确临时路径，不使用通配符，并验证不存在残留。

运行 Python 时使用 `-B` 或设置 `PYTHONDONTWRITEBYTECODE=1`，避免生成 `__pycache__`。项目最终只保留获批的正式材料、必要目标子目录，以及另行批准的 `PROJECT.md` 修改。

临时资源清理失败时，不得报告任务完全完成。复制中途失败时不要自动删除已复制的业务材料；报告准确目标和完成程度，避免误删。

## 完成检查

结束前：

- 验证所有获批目录、占位文件、复制结果或 `PROJECT.md` 修改；
- 确认没有未批准修改、覆盖、移动、删除或计划外文件；
- 确认源材料保持不动；
- 检查 `PROJECT.md` 的标题、状态、顶部摘要和取消记录一致性；
- 报告建议但未执行的事项；
- 验证本次临时资源已经清理；
- 如果驾驶舱仍开启，简短说明它将在当前 Codex 任务中继续保持开启，不要每轮询问关闭。
