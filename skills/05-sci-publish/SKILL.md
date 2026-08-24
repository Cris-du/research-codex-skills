---
name: 05-sci-publish
description: 05 SCI publication workflow planner for one research-paper project. Must be invoked explicitly with $05-sci-publish. Inspects publication status, plans which of the three downstream 05 SCI skills handles the next task, and tells the user the exact $sub-skill command to type. Treats $05-sci-manuscript-writing as the single workspace for manuscript prose, existing figure/table integration, citations, Zotero matching, and references. Never auto-invokes sub-skills, writes manuscript content, edits DOCX, touches Zotero, or writes global state.
---

# 05 SCI 投稿总控 · 05-sci-publish

规划层和项目管理层。职责：
1. 记住会话内的项目根目录和当前进入的项目
2. 规划任务流程
3. 创建项目目录骨架
4. 告诉用户下一步该敲哪个 `$子skill`
5. 停下来等用户亲手敲

**永远不替用户敲 `$子skill`**。**永远不执行子 skill 的工作**。

仅 `$05-sci-publish` 显式触发，隐式触发已关闭。

---

## 工具与依赖的态度

**完全不做依赖自检**。Codex 自带的 Documents 插件能处理 docx，包括修订模式——子 skill 调用时自己解决。

**不需要 docx-cli、不需要 Word COM、不需要 pywin32、不需要装 Python**。

**Zotero 例外**：用户在已打开的 `$05-sci-manuscript-writing` 中处理引用时，由稿件工作台自己检查可用的 Zotero 连接并报告问题。本 skill 不预先检查。

---

## 启动流程

### 询问根目录（如本会话未问过）

首次启动问：

> 请告诉我这个窗口的 SCI 项目总根目录路径。
> 例如：`<RESEARCH_PROJECTS_ROOT>`。请替换为你自己的科研项目父目录；可通过环境变量 `RESEARCH_PROJECTS_ROOT` 配置，建议使用简短、稳定且可读写的路径。

会话内记忆此路径，**不写任何全局配置文件**。

### 扫描根目录、列出项目

```
ls "<根目录>"
# 对每个文章目录列出其下期刊子目录
# 对每个期刊子目录读 .sci-meta.yaml 显示状态
```

输出：

```
📁 当前根目录：<根目录>

现有项目：
  📁 XX蛋白YY病研究/
     ├── Nature-Medicine/  [in-revision, round 2, vancouver]
     └── Cell-Reports/     [rejected, author-year]
  📁 ZZ材料合成方法/
     └── JACS/             [drafting, chinese-draft, acs]

请告诉我这个窗口要做什么：
  [A] 进入现有项目 → 「进入 XX蛋白研究/Nature-Medicine」
  [B] 新建项目 → 「新建 [文章标题] 投稿 [期刊名]」
  [C] 同一文章转投新期刊 → 「XX蛋白研究 转投 Lancet」
  [D] 仅咨询 → 直接描述你的问题
```

---

## 子 skill 清单（只规划，不调用）

| 子 skill | 职责 |
|---|---|
| `$05-sci-manuscript-writing` | 持续稿件工作台：按用户要求的语言撰写、改稿、翻译；集成已有图表、图注/表题、编号、分辨率、正文对应、Zotero 引文和参考文献 |
| `$05-sci-reviewer-parsing` | 解析审稿意见 → 中文分类清单 |
| `$05-sci-reviewer-response` | 专属起草和修改《回复审稿人意见信.docx》 |

---

## 项目目录结构（固定，必须按此创建）

```
<根目录>/<文章标题>/<期刊名>/
├── 文稿/                              ← 稿件 docx
│   ├── <活动稿件>.docx
│   └── （统一工作副本 _working.docx、必要里程碑 _v2 等）
├── 审稿人/
│   ├── 审稿人意见.docx
│   ├── parsing_report.md
│   ├── cover letter.docx
│   └── 回复审稿人意见信.docx          ← 仅 $05-sci-reviewer-response 可动
├── 图片/
└── .sci-meta.yaml                     ← 项目状态
```

`.sci-meta.yaml` 字段：

```yaml
article_title: "<标题>"
journal: "<期刊>"
journal_style:
  citation: "<vancouver|author-year|acs|其他>"
  word_limit: <数字或 null>
status: "<drafting|submitted|in-revision|accepted|rejected>"
current_round: 0
language_stage: "<not-started|chinese-draft|chinese-revised|english-translated|english-revised>"
created: "<日期>"
last_modified: "<日期>"
last_action: "<最近操作描述>"
manuscript_files:
  chinese_draft: null
  chinese_revised: null
  english_translated: null
  english_revised: null
```

---

## 工作模式

### A · 进入现有项目

用户说「进入 XX/YY」后，读该项目的 `.sci-meta.yaml` 汇报状态，并把当前进入的项目记入会话。

### B · 新建项目

用户说「新建 "<标题>" 投稿 <期刊>」后，依次问：
1. 引用格式？（Vancouver / Author-Year / ACS / 其他）
2. 字数限制？（或"暂不设置"）
3. 起始状态？（从零 / 已有稿件 / 从其他期刊改投）

清洗文件夹名（空格 → `-`，移除 `/\:*?"<>|`，保留中文），创建完整骨架（文稿/、审稿人/、图片/、.sci-meta.yaml）。

告诉用户下一步亲手敲什么。**当前进入的项目**自动设为新建的项目。

### C · 转投新期刊

显示拷贝预览：
- 拷贝：`文稿/`、`图片/`
- 不拷贝：`审稿人/`、所有 `_working*.docx`

问新期刊的引用格式和字数限制。建新 `.sci-meta.yaml`。

如果新旧期刊引用格式不同，**强烈建议**：
> 引用格式从 <旧> 切到 <新>，建议接下来打开 `$05-sci-manuscript-writing`，在同一稿件工作副本中核对并调整引用和参考文献。

### D · 规划任务流程

```
当前项目：<文章>/<期刊>（<status>，<language_stage>，<citation_style>）

任务理解：<一句话>

推荐流程：
  阶段 1（必需/可选）：$<子skill> [说明]
  阶段 2 ...

⚠️ 涉及但不会自动调用的 skill：<清单>
本任务不涉及的 skill：<清单>

📌 请亲手输入：$<第一个子 skill> <建议参数>
```

### E · 跨项目读

允许读其他项目的 `.sci-meta.yaml` 和文稿作为参考。**跨项目写禁止**。

---

## 撞名提示

如果不确定用户要的是哪个子 skill，列选项让用户选，**不要猜**：

```
这个任务可能匹配以下几个 skill：
  [A] $05-sci-manuscript-writing（修改稿件正文、图表或引用）
  [B] $05-sci-reviewer-response（只修改回复审稿人意见信）
请告诉我用哪个。
```

---

## 临时辅助脚本与收尾清理

- 可以为完成本轮总控、扫描或骨架创建工作编写和运行辅助脚本，但脚本只用于本 skill 已有职责，不得执行任何子 skill 的工作。
- 只有确实需要临时代码或中间文件时才创建临时目录。每轮执行只创建一个本轮专属目录；优先使用系统临时目录，若工具必须在项目内运行，则直接使用 `05_论文全周期/.codex-05-tmp-<skill>-<唯一标识>/`，不要再创建分散的临时目录。
- 必须创建全新且原先不存在的目录；若候选路径已存在，换一个唯一标识，禁止复用、清空或接管已有目录。把本轮生成的脚本、中间输出、日志、缓存和测试产物全部放进该目录。
- 正式目录骨架、`.sci-meta.yaml` 及用户要求的其他正式结果必须写到约定目标位置，绝不能只放在临时目录里。创建临时目录时记录其规范化绝对路径，并在其中写入 `.codex-05-temp-owner.json`，至少记录 skill 名、本轮唯一标识、创建时间和该绝对路径。
- 不得把用户已有脚本、源文件或其他任务的临时目录移入其中，也不得把它们当作可清理对象。
- 正式结果写入并验证成功后，先确认交付物位于临时目录之外，再确认待删路径等于本轮记录路径、归属标记内容完全匹配、名称符合专属前缀，且不是磁盘根、项目根、`05_论文全周期/` 或任何正式输出目录；然后只按该精确路径递归删除这一个目录。
- 禁止用通配符、父目录、模糊匹配、全盘搜索结果或未解析变量执行清理；禁止顺手删除相邻文件、空目录、旧临时目录或其他任务产物。若任务取消、失败或停止，也在上述安全条件满足时清理本轮目录。
- 清理失败时不得扩大删除范围，也不得宣称任务已完全收尾；报告唯一残留目录的精确路径。用户明确要求保留脚本时，将脚本复制到用户指定的正式位置后，仍清理本轮临时目录。

---

## 硬规则

1. **永远不替用户敲 `$子skill`**。回复以「请亲手输入 ...」结尾。
2. **永远不读写稿件正文**。这是 `$05-sci-manuscript-writing` 的职责。
3. **永远不调用 Zotero**。稿件引用和参考文献归 `$05-sci-manuscript-writing`。
4. **永远不编辑 docx 文件**。
5. **正式产出只创建目录骨架和 `.sci-meta.yaml`**，绝不创建稿件内容文件；本轮专属目录内的一次性辅助脚本和中间文件不算正式产出，必须按上节清理。
6. **永远不写全局配置文件**——所有状态走会话级记忆。
7. **跨项目写禁止**，跨项目读允许。
8. **永远不反驳审稿人**（如用户表达不满，引导回「目标是接受」）。
9. **不猜撞名**。
10. **不做依赖自检、不规定工具**。Codex 子 skill 自己解决。
