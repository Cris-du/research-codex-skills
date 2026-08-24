---
name: 05-sci-reviewer-parsing
description: 05 reviewer-comments parsing skill. Must be invoked explicitly with $05-sci-reviewer-parsing followed by a file path. Reads reviewer comments from the project's reviewer-material directory, produces a Chinese-summarized, classified, prioritized issue list with English key terms preserved, and maps each item to a manuscript location. Read-only for manuscript and reviewer source files; writes only the approved parsing report.
---

# 05 SCI 审稿意见解析 · 05-sci-reviewer-parsing

读审稿意见文档，产出**中文整理 + 关键术语保留英文**的结构化清单。**完全只读，不动任何稿件文件**。

仅 `$05-sci-reviewer-parsing <文件路径>` 显式触发。

---

## 启动前置

1. **项目上下文**：询问用户当前项目的绝对路径。会话内记忆，不写磁盘。
2. **审稿意见文件**：
   - 用户在指令中给了路径就用
   - 没给路径 → 扫描 `审稿人/` 列出 docx 让用户选
   - 列表里没有 → 提示用户先把审稿意见放进 `审稿人/`

---

## 工作流

### 1. 读取审稿意见

按段落读，不一次性读全文进上下文。

### 2. 识别审稿人

常见结构：`Reviewer #1` / `Reviewer 1` / `审稿人 1` / `R1`。

启发式自动识别审稿人分块。识别困难时问用户：「这份文档里有几个审稿人？」

### 3. 切分意见条目

对每个审稿人切分：
- 数字编号（`1.` `2.` `(1)` `(2)`）
- 段落分隔
- 关键词触发（"Comment 1:" / "Issue 1:" / "Major:" / "Minor:"）

### 4. 对每条意见生成结构化记录

```
【R<审稿人编号>-<意见编号>】<分类> · <类别> · 优先级 ★★★/★★/★

原文关键词：<英文原文里的关键术语，3-6 个>

中文整理：<2-4 句话精确翻译/转述>
        <关键术语保留英文括注>

对应稿件位置：<Introduction §X / Methods §X.Y / Results §X /
            Discussion §X / Fig N / Table N / Abstract / Cover Letter>

处理建议方向：<选择以下之一或组合>
  - 需补实验
  - 需补讨论/澄清表述
  - 需重写段落
  - 需补充引用
  - 需修改图表
  - 需修改方法描述
  - 仅语言/格式
```

### 5. 分类维度

**类型分类**（决定优先级和处理路径）：
- `Major` ★★★ — 涉及主要结论、需补实验或大段重写
- `Minor` ★★ — 局部修改即可
- `Language` ★ — 仅语言/拼写/语法
- `Reference` — 引用相关
- `Figure` — 图表相关
- `Data` — 数据呈现
- `Method` — 方法描述
- `Discussion` — 讨论
- `Format` — 格式

一条可有多个标签（如 Major + Method）。

### 6. 生成汇总统计

```
═══ 全部审稿意见汇总 ═══
Reviewer #1：N 条
Reviewer #2：M 条

按处理类型分组：
  需补实验：a 条
  需补讨论/澄清：b 条
  需重写段落：c 条
  需修改图表：d 条
  需补充引用：e 条
  仅语言/格式：f 条

按优先级：
  ★★★ Major：x 条
  ★★ Minor：y 条
  ★ Language：z 条
```

### 7. 保存报告

写入 `审稿人/parsing_report.md`（已存在则加日期后缀：`parsing_report_<日期>.md`）：

```markdown
# 审稿意见解析报告

**项目**：<文章>/<期刊>
**审稿轮次**：<round N>
**审稿意见原文件**：<审稿人/<文件名>>
**解析时间**：<日期时间>

---

## Reviewer #1

### 【R1-1】Major · Method · 优先级 ★★★

**原文关键词**：sample size justification, power analysis

**中文整理**：审稿人认为样本量（n=24）偏小，要求补充
power analysis 说明这个样本量足以检出预期效应（effect size）。

**对应稿件位置**：Methods §2.3（统计分析部分）

**处理建议方向**：补充 power analysis 描述（无需重做实验）

---

### 【R1-2】...

---

## Reviewer #2

...

---

## 汇总统计

...
```

### 8. 输出对话摘要

```
══ 审稿意见解析完成 ══
完整报告：审稿人/parsing_report.md

═══ 摘要 ═══
Reviewer #1：8 条
Reviewer #2：5 条

按处理类型：
  需补实验：0 条
  需补讨论：6 条
  需修改图表：2 条
  需补充引用：1 条
  仅语言/格式：4 条

═══ 前 3 条最关键的（★★★）═══

【R1-1】Major · Method · power analysis
  样本量需补 power analysis 说明

【R1-2】Major · Data · Figure 3 误差线
  Fig 3 误差线类型未说明，n 值未给出

【R2-1】Major · Discussion · 机制讨论不足
  Discussion 缺对 XX 机制的深入讨论

═══ 下一步 ═══
- 处理某一条 → 告诉我条目编号
- 看完整报告 → 阅读 审稿人/parsing_report.md
- 直接改稿 → 亲手输入 $05-sci-manuscript-writing
- 起草回复信 → 亲手输入 $05-sci-reviewer-response
```

---

## 「处理某一条」的咨询响应

用户接着说「处理 R1-1」时，**本 skill 不执行处理**。响应：

```
R1-1 的处理路径建议：

处理类型：补充 power analysis 描述
涉及操作：
  1. 改稿件 → 亲手输入 $05-sci-manuscript-writing
     （示例：在 Methods §2.3 末尾补充 power analysis 段落）
  2. 起草回复条目 → 亲手输入 $05-sci-reviewer-response
     （示例：起草 R1-1 的回复，引用稿件中刚补充的位置）

注意顺序：先改稿件，再起草回复（回复中要写出"已在 Page X Line Y 添加"）。

⚠️ 我不替你调用上述 skill。请亲手敲。
```

---

## 临时辅助脚本与收尾清理

- 可以为读取、切分、归类或生成报告编写和运行辅助脚本，但脚本只用于本 skill 已有职责，不得修改稿件或审稿意见源文件。
- 只有确实需要临时代码或中间文件时才创建临时目录。每轮执行只创建一个本轮专属目录；优先使用系统临时目录，若工具必须在项目内运行，则直接使用 `05_论文全周期/.codex-05-tmp-<skill>-<唯一标识>/`，不要再创建分散的临时目录。
- 必须创建全新且原先不存在的目录；若候选路径已存在，换一个唯一标识，禁止复用、清空或接管已有目录。把本轮生成的脚本、文档解包文件、文本提取物、中间渲染、日志、缓存和测试产物全部放进该目录。
- 正式 `parsing_report*.md` 必须写到约定目标位置，绝不能只放在临时目录里。创建临时目录时记录其规范化绝对路径，并在其中写入 `.codex-05-temp-owner.json`，至少记录 skill 名、本轮唯一标识、创建时间和该绝对路径。
- 不得把用户已有脚本、源文件或其他任务的临时目录移入其中，也不得把它们当作可清理对象。
- 正式报告写入并验证成功后，先确认交付物位于临时目录之外，再确认待删路径等于本轮记录路径、归属标记内容完全匹配、名称符合专属前缀，且不是磁盘根、项目根、`05_论文全周期/`、`审稿人/` 或任何正式输出目录；然后只按该精确路径递归删除这一个目录。
- 禁止用通配符、父目录、模糊匹配、全盘搜索结果或未解析变量执行清理；禁止顺手删除相邻文件、空目录、旧临时目录或其他任务产物。若任务取消、失败或停止，也在上述安全条件满足时清理本轮目录。
- 清理失败时不得扩大删除范围，也不得宣称任务已完全收尾；报告唯一残留目录的精确路径。用户明确要求保留脚本时，将脚本复制到用户指定的正式位置后，仍清理本轮临时目录。

---

## 硬规则

1. **完全只读**。永不写、不改、不动任何稿件文件。
2. **正式产出只允许 `审稿人/parsing_report*.md`**；本轮专属目录内的一次性辅助脚本和中间文件是临时例外，必须按上节清理。
3. **不动 `回复审稿人意见信.docx`**。
4. **不评价审稿人意见的对错**——只翻译/整理/分类。不写「这条意见不合理」之类评论。
5. **关键术语保留英文**（如 "power analysis", "effect size", "Bonferroni correction"）。
6. **对应位置不擅自加段落编号**——如稿件没清晰段落编号，按章节大致定位即可。
7. **跨项目读允许，跨项目写禁止**。

---

## 状态更新

```yaml
last_modified: "<今天>"
last_action: "sci-reviewer-parsing：解析 <文件名>，识别 N 条意见，报告在 审稿人/parsing_report_<日期>.md"
current_round: <推进到下一轮>
status: "in-revision"
```
