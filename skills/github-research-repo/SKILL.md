---
name: github-research-repo
description: >-
  Use only when the user explicitly invokes $github-research-repo to bootstrap a research methods-and-code repository from zero, clone or attach an existing GitHub repository, or inspect, curate, audit, synchronize, and publish it. A local checkout is not a prerequisite: route among absent, local-only, remote-only, and linked states, creating or cloning the project's Git directory when authorized. Maintain reader-facing scripts, configurations, workflows, README, and command-based method records with verified tools, versions, commands, parameters, inputs, outputs, dependencies, and execution order. Create private GitHub repositories when requested and verify identity and visibility. Use the GitHub plugin for supported operations, with narrow gh or git fallbacks for bootstrap, clone, attach, or creation. Never invent method facts, include data, results, figures, internal documents, logs, secrets, or the whole workspace, modify PROJECT.md or 01–05, or change scientific logic only in the reader-facing copy.
---

# GitHub Research Methods and Code Repo

从任意初始状态建立或维护一个科研项目的读者向方法与代码复现仓库。本地 `<project-root>/Git/` 是本 Skill 按需创建、克隆或接管的安全工作区，不是调用前提。把 `03` 中真实执行过、由用户明确选择的脚本、配置、命令流程和方法说明整理为可理解、可移植、可审计的分发版本。即使分析只由若干条命令组成、没有独立脚本，也要完整维护其实际方法链；但不把仓库变成项目备份。

## 读取适用合同

- 始终完整读取 [content-contract.md](references/content-contract.md) 和 [action-and-approval-gates.md](references/action-and-approval-gates.md)。
- 执行审计、commit、push、远端创建或公开发布前，另完整读取 [publication-audit.md](references/publication-audit.md)。
- 一旦任务需要通用 GitHub 操作，读取已安装 GitHub 插件中的最窄匹配 Skill，并把实际执行交给它；只有“创建 GitHub 仓库”在插件当前工具面中缺失时，才使用本 Skill 规定的 `gh repo create` 回退。

## 与 GitHub 插件的职责边界

本 Skill 是科研领域编排层，GitHub 插件是通用执行层。

- 本 Skill 负责：确定项目与 `Git/` 边界、选择允许晋升的科研内容、保护科学逻辑、组织读者向方法链和代码结构、维护 README 与命令记录、运行审计、生成确切的文件清单与授权范围。
- `$github`：仓库、PR 和 issue 的通用定位、查询、摘要与路由；也由它决定是否转入下列专用 Skill。
- `$gh-address-comments`：检查和处理 PR review 意见。
- `$gh-fix-ci`：检查 GitHub Actions 失败日志，定位并修复 CI。
- `$yeet`：在用户明确要求完整发布流程时，处理分支、精确暂存、commit、push 和 draft PR。
- 转交执行时，向插件 Skill 传递已确认的本地 repo、owner/repo、远端和分支、允许文件、排除项、审计结果与当前授权；插件不得重新扩大科研内容范围。
- 创建远端仓库：插件有创建仓库工具时优先使用插件；否则在取得独立授权后使用 `gh repo create`，并完成身份和可见性复核。
- 可见性变更、tag、release 或历史修复等其他能力若不在已安装插件的当前工具面中，不得假定它可用；报告缺口，并且只在对该动作取得独立授权后使用最窄回退。
- 若 GitHub 插件不可用，保留已完成的安全本地工作，报告缺失前提；不在未披露的情况下自行扩展为另一套 GitHub 流程。

## 固定项目与仓库边界

- 从用户明确路径或无歧义上下文确定唯一项目根。
- 默认唯一目标为 `<project-root>/Git/`。它是项目管理 Skill 预留的独立 Git 工作树，不是项目根仓库，也不要求调用前已经存在。
- `Git/` 不存在时，先判定目标远端是否存在：远端不存在则路由到 **Bootstrap**；远端已存在则路由到 **Clone**。不得仅因一次 Inspect 自动创建目录或仓库。
- `Git/` 已是本地 Git 仓库但尚未连接目标远端时，路由到 **Attach**；本地与远端均已正确连接时，进入维护、审计或同步。
- 把项目根中 `Git/` 以外的所有材料视为只读源。
- 不在项目根、`03_数据与分析/`或其他业务目录执行 `git init`。
- 不因为找不到仓库就创建第二个。若发现多个候选、本地与远端身份不一致、父目录已经处于其他仓库中或用户采用了不同布局，先报告并让用户确认。
- 只要用户没有明确重开顶层设计，就坚持一个项目、一个读者向方法与代码 repo；不因每个分析步骤或方法模块再建仓库。

## 路由动作

识别一个主要动作，并在混合请求中按门禁顺序执行：

1. **Inspect**：只读检查项目、本地目标和远端身份，判定当前属于不存在、本地独有、远端独有还是已连接状态。
2. **Bootstrap**：新课题的本地和远端都不存在时，按需创建 `Git/`、初始化 Git、建立 README 与 `.gitignore`；用户要求 GitHub 仓库时，再经独立门禁创建 private 远端并连接。
3. **Clone**：目标 GitHub 仓库已存在而本地 `Git/` 不存在或为空时，确认唯一身份和目标路径后克隆到 `Git/`，再复核本地与远端对应关系。
4. **Attach**：本地 `Git/` 已是目标仓库、远端也已存在但尚未正确连接时，核验身份和历史关系后添加或修正远端；不得借此合并不相关历史。
5. **Promote**：把用户明确选择的 `03` 脚本、配置或必要资源复制到 `Git/`，并把已核实的直接命令、参数和执行顺序整理为方法文档。
6. **Audit**：检查内容边界、秘密、大文件、可移植性、README、Git 状态和必要历史。
7. **Synchronize**：审计后生成确切的发布范围，取得分段授权，再路由到 GitHub 插件执行适用的 commit、push 或 PR 流程。
8. **Publish**：在用户确认的项目公开节点完成公开前全历史审计；可见性变更只在工具能力可核验且用户对具体远端最终批准后执行。

混合请求按 `Inspect → Bootstrap/Clone/Attach → Promote → Audit → Synchronize → Publish` 执行，只运行达到用户目标所必需的阶段。没有本地仓库不是阻断项；只有目标不唯一、路径冲突、身份不明、认证或权限不足等才阻断相应动作。

未显式调用本 Skill 的一般 GitHub 请求，全部让渡给 `$github` 及其专用 Skills。

## 始终从只读开始

每次运行先报告：

- 项目根与目标 `Git/` 的绝对路径；
- `Git/` 是不存在、空目录、普通目录还是 Git 仓库；不存在时说明应走 Bootstrap 还是 Clone；
- 本地仓库根、当前分支、HEAD、dirty 状态和已知 upstream 差异；
- 远端名称、owner/repo、默认分支和可核验的可见性；
- 当前动作、拟读取来源、拟写目标和明确排除项；
- Git、GitHub CLI、连接器、网络或认证中缺少的前提。

只读检查本身不授权创建目录、Bootstrap、Clone、Attach、复制、修改、commit、push、创建远端或改变可见性。

## 执行内容晋升

1. 让用户指定要进入 repo 的脚本、配置、资源或方法流程；不要主动把相邻脚本或整个任务目录一并加入。
2. 显示每个源路径或方法事实来源、目标路径、纳入理由、排除内容和拟进行的参数化或去敏修改。
3. 获得本地整理授权后，只复制到 `Git/`；不移动、不删除、不覆盖或反写 `03`。
4. 在 repo 副本中删除秘密信息，使用参数、相对路径、环境变量或示例配置替代环境偶然性。
5. 保持科学逻辑不变。若可移植化需要改变算法、阈值、样本范围、统计方法或结果，停止并让用户决定是否返回 `03`审查和重跑。
6. 对每个命令步骤记录：目的、工具与版本、实际命令、参数值及含义、输入、输出、环境或工作目录、上下游依赖与实际执行顺序。
7. 区分“已实际执行”和“为可移植性整理”。只能从原始脚本、shell history、工作记录、日志或用户明确确认的描述提取命令事实；不得猜测版本、补造参数或把推荐用法写成当时实际用法。
8. 信息不完时，private 阶段明确标注“未核实”并向用户确认；公开前解决所有会影响复现的未核实项。
9. 按实际运行顺序组织目录、方法文档和 README；例如病毒预测分析有 4 条连续命令，就维护为 4 个有前后依赖的方法步骤，而不是只写一句“运行病毒预测工具”。
10. 运行只读审计和可行的最小检查，报告 repo 副本、方法记录与源证据的差异。

## 使用确定性审计

用当前 Python 解释器运行：

```text
python <skill-root>/scripts/audit_repository.py <project-root>/Git
```

公开前运行：

```text
python <skill-root>/scripts/audit_repository.py <project-root>/Git --public
```

脚本只向标准输出写 JSON，不修改仓库。退出码：

- `0`：机械审计完整且没有阻断项；
- `2`：发现阻断项；
- `3`：审计不完整或发生运行错误。

脚本通过不等于语义审计完成。继续检查 README 的科学准确性、许可、数据可用性、远端身份、可见性和实际复现边界。

## 分离授权门禁

- 本地整理授权只覆盖展示过的 `Git/` 文件操作。
- commit 前由本 Skill 确认科研内容范围与审计结果；由 GitHub 插件 Skill 展示确切 diff、拟暂存文件和 commit message，并取得该步批准。
- push 前由 GitHub 插件 Skill 展示 commit、远端、分支、upstream 状态和可核验的远端可见性，并取得该步批准。
- 创建远端前确认 owner、repo 名、描述、远端名和可见性；默认 private。创建和首次 push 是两个独立动作。
- 公开前核验用户已确认当前方法内容可公开且无项目、论文、合作或数据时点限制，检查完整 Git 历史，展示最终目录树和可见性变更，再取得明确批准。
- tag、release、许可证选择、归档 DOI、删除、历史重写和 force-push均为独立动作，不从其他批准推断。

即使用户最初要求“整理、提交并推送”，也先完成整理和审计，再在 commit/push 门禁展示确切对象。局部同意不能扩展成全部同意。

## 冲突与停止条件

遇到以下情况停止相关写入或远端动作：

- dirty worktree 中存在与本次范围重叠的用户改动；
- 远端领先、已分叉或 upstream 身份不明；
- 用户确认的公开节点前远端已经是 public；
- 审计发现数据、结果、内部文档、秘密、大文件、未知二进制或污染的 Git 历史；
- `02`、真实执行证据与 repo 中的方法或代码互相冲突；
- repo 副本只有改变科学逻辑才能运行；
- Git、网络、认证或远端权限不足；
- 目标 repo、本地路径、远端或所属项目不唯一。

不得自动 stash、reset、merge、rebase、删除、重写历史或 force-push。保留已有成果并准确报告未完成动作。

## 完成报告

每次结束报告：

- 项目根、`Git/`本地路径、远端和当前可见性；
- 本次动作；
- 新增、修改、移动或删除的 repo 文件；
- 每个晋升文件或方法记录的事实来源及 repo 副本变化；
- 明确排除内容和理由；
- README 更新；
- 审计结果、警告和阻断项；
- commit hash、push 分支和远端状态（若执行）；
- 明确未执行的动作，例如“未 commit”“未 push”“仍为 private”；
- 可能需要 `$manage-research-project`、`$research-study-design`或数据分析 Skill 处理的上游事项。
