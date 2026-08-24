---
name: 05-sci-reviewer-response
description: 05 SCI reviewer-response letter drafting skill. Must be invoked explicitly with $05-sci-reviewer-response. Exclusively creates and modifies the reviewer-response letter and its working copies; no other skill may touch those files. Drafts responses from user direction and the parsing report, outputs a Chinese draft first, and translates to English only after user confirmation. Never rebuts a reviewer; the goal is journal acceptance, not debate. Never modifies manuscript files, which belong to $05-sci-manuscript-writing.
---

# 05 SCI 审稿回复信起草 · 05-sci-reviewer-response

**唯一职责**：起草和修改 `审稿人/回复审稿人意见信.docx`。

**不改稿件正文**。稿件修改归 `$05-sci-manuscript-writing`。

**最高硬规则：永不反驳审稿人**。目标是**期刊接受**，不是赢得辩论。

仅 `$05-sci-reviewer-response` 显式触发。

---

## 启动前置

1. **项目上下文**：询问用户当前项目的绝对路径。会话内记忆，不写磁盘。
2. **审稿人目录检查**：
   ```
   审稿人/ 目录现有文件：
     - 审稿人意见.docx
     - parsing_report.md
     - cover letter.docx
     - 回复审稿人意见信.docx (<存在/不存在>)
   ```
3. **询问任务类型**：
   ```
   请告诉我做什么：
     [1] 创建回复信（首次起草）
     [2] 添加新条目
     [3] 修改已有条目
     [4] 把中文初稿翻译成英文
     [5] 整体审阅与润色
   ```

---

## docx 操作目标（不规定工具）

Codex 自选实现。但所有写入必须：
1. 首次创建除外，其他写入都建工作副本 `_working.docx`
2. 写入前显示内容让用户确认
3. **修改类操作保留 Word 修订标记**（创建新文件无需）
4. 禁止 python-docx 和视觉模拟

---

## 「永不反驳」硬规则

### 回复条目固定四段结构

```
1. 感谢审稿人指出
2. 承认观点合理性
3. 说明已做的具体修改
4. 指明改动位置（Page X, Line YY-ZZ 或 §X.Y）
```

### 禁用句式（永远不写）

- "We disagree..."
- "However, we believe..."
- "This is not necessary because..."
- "The reviewer is mistaken..."
- "The reviewer misunderstood..."
- "We respectfully disagree..."
- "We don't think..."
- "Contrary to the reviewer's view..."

中文等价物同样禁用：「我们不同意」、「然而我们认为」、「这没有必要因为」、「审稿人有所误解」等。

### 推荐句式

**感谢类**：
- "We thank the reviewer for this insightful comment."
- "We sincerely appreciate the reviewer's careful reading."
- 中文：「感谢审稿人指出这一点。」

**承认类**：
- "We agree that..."
- "The reviewer raises an important point."
- 中文：「我们认同……」

**修改说明类**：
- "As suggested..."
- "Following the reviewer's suggestion..."
- "To address this concern, we have..."
- 中文：「按审稿人建议，我们已经……」

**指明位置类**：
- "Please see the revised manuscript at Page X, Line YY-ZZ."
- 中文：「具体修改位置：修改稿 Page X, Line YY-ZZ。」

### 客观无法采纳时的处理

例：审稿人要求补一个实验，但确实不可行（伦理结束、样本用完、设备停用）。

**绝不写**：「我们不同意」、「这没必要」。

**而是写**：
```
We sincerely appreciate the reviewer's suggestion for [specific experiment].
We agree that [this aspect] is important to address.

Unfortunately, we are unable to perform this exact experiment because
[客观原因，不带情绪]. To address the underlying concern, we have instead:

  - [Alternative 1，如：added a thorough discussion of this limitation]
  - [Alternative 2，如：cited recent work that addresses this question]
  - [Alternative 3，如：performed a related complementary analysis]

We hope these revisions adequately address the reviewer's concern.
```

**核心思路**：感谢 → 同意意见的重要性 → 客观说明限制 → 已用 XX 替代方式回应。**绝不出现"不同意"**。

---

## 任务 1 · 创建回复信（首次起草）

### 流程

1. **读取 parsing_report.md**：从 `审稿人/parsing_report*.md`（最新一份）获取所有意见

2. **询问范围**：
   ```
   parsing_report.md 中有 R1（8 条）和 R2（5 条），共 13 条。
   要起草哪些？
     [全部] / [选条目，如 R1-1, R1-2, R2-1] / [按优先级，如只 ★★★]
   ```

3. **询问每条意见的处理状态**（关键）：
   ```
   起草前需要知道每条意见的实际处理情况——这决定回复信里要写什么修改。

   请告诉我各条的处理情况：
     a) 完全采纳：在哪个 docx 的哪个位置改了？
     b) 部分采纳：怎么部分采纳的？
     c) 客观无法采纳：原因？已用什么替代方式回应？

   如果还没改稿件，建议先 $05-sci-manuscript-writing 改稿再回来起草回复。
   ```

4. **起草中文回复**（默认中文先行）：

   每条格式：
   ```
   【R1-1】Major · Method · power analysis

   [中文回复初稿]
   感谢审稿人对样本量的关注。我们认同应当对当前样本量的统计效能
   进行明确说明。在修改稿中，我们于 Methods §2.3 末尾补充了
   post-hoc power analysis 的结果（使用 G*Power 3.1，效应量
   Cohen's d = 0.82，双侧 α = 0.05，n = 24 时 power = 0.91），
   表明当前样本量足以检出主要效应（primary effect）。

   具体修改位置：修改稿 Page 5, Line 112-118（修订模式可见）。
   ```

5. **每条起草后停下**问用户：「这条 OK 吗？要改什么？」

6. **所有条目确认后**组装完整回复信中文初稿：
   ```markdown
   尊敬的编辑、审稿人：

   感谢编辑给予修改机会，也感谢各位审稿人提供的宝贵意见。
   我们已认真考虑每一条意见，对稿件做出了相应修改。以下是逐条回复：

   ──── Reviewer #1 ────

   【R1-1】...

   【R1-2】...

   ──── Reviewer #2 ────

   【R2-1】...

   ────

   再次感谢各位的宝贵意见。期待您的进一步反馈。

   作者敬上
   <日期>
   ```

7. **写入** `审稿人/回复审稿人意见信.docx`（首次创建，无需修订模式）

8. 完成后告诉用户：
   ```
   ══ 回复信中文初稿已创建 ══
   文件：审稿人/回复审稿人意见信.docx
   条目数：13

   ══ 下一步 ══
   - 修改某条 → 亲手输入 $05-sci-reviewer-response 选「修改已有条目」
   - 翻译成英文 → 亲手输入 $05-sci-reviewer-response 选「翻译」
   - 整体润色 → 亲手输入 $05-sci-reviewer-response 选「整体审阅」
   ```

---

## 任务 2 · 添加新条目

类似任务 1，但追加到现有回复信，**先建工作副本**再操作（**修改类操作必须保留 Word 修订标记**）。

---

## 任务 3 · 修改已有条目

1. 读 `回复审稿人意见信.docx` 找目标条目
2. 询问怎么改
3. 先建工作副本，按硬规则起草新版本
4. 显示新旧对比让用户确认
5. **写入工作副本时保留 Word 修订标记**

---

## 任务 4 · 翻译成英文

把已确认的中文回复信翻译成英文。

### 流程

1. 读当前回复信内容
2. 逐条翻译：
   - 严格按推荐句式
   - 保留专业术语原文
   - 不重新创作，对照中文翻译
3. 写入 `回复审稿人意见信_en_working.docx`（英文工作副本）
4. 报告：「英文版已生成在 `回复审稿人意见信_en_working.docx`，原中文版保持不动。」

---

## 任务 5 · 整体审阅与润色

读整封回复信，做整体审阅：
- 所有意见都回复了吗
- 有任何反驳措辞吗（敏感扫描禁用句式）—— 有则**强制改写**
- 语气是否一致（都用 "we"，时态一致）
- 修改位置标注是否完整（每条有 Page/Line 引用）

报告问题后让用户决定改不改。

---

## 临时辅助脚本与收尾清理

- 可以为创建、修改、翻译、修订或验证回复信编写和运行辅助脚本，但脚本只用于本 skill 已有职责，不得修改稿件正文或其他专属文件。
- 只有确实需要临时代码或中间文件时才创建临时目录。每轮执行只创建一个本轮专属目录；优先使用系统临时目录，若工具必须在项目内运行，则直接使用 `05_论文全周期/.codex-05-tmp-<skill>-<唯一标识>/`，不要再创建分散的临时目录。
- 必须创建全新且原先不存在的目录；若候选路径已存在，换一个唯一标识，禁止复用、清空或接管已有目录。把本轮生成的脚本、DOCX 解包文件、中间渲染、日志、缓存、临时副本和测试产物全部放进该目录。
- 正式回复信及用户要求保留的版本必须写到约定目标位置，绝不能只放在临时目录里。创建临时目录时记录其规范化绝对路径，并在其中写入 `.codex-05-temp-owner.json`，至少记录 skill 名、本轮唯一标识、创建时间和该绝对路径。
- 不得把用户已有脚本、源文件或其他任务的临时目录移入其中，也不得把它们当作可清理对象。
- 正式结果写入并验证成功后，先确认交付物位于临时目录之外，再确认待删路径等于本轮记录路径、归属标记内容完全匹配、名称符合专属前缀，且不是磁盘根、项目根、`05_论文全周期/`、`审稿人/` 或任何正式输出目录；然后只按该精确路径递归删除这一个目录。
- 禁止用通配符、父目录、模糊匹配、全盘搜索结果或未解析变量执行清理；禁止顺手删除相邻文件、空目录、旧临时目录或其他任务产物。若任务取消、失败或停止，也在上述安全条件满足时清理本轮目录。
- 清理失败时不得扩大删除范围，也不得宣称任务已完全收尾；报告唯一残留目录的精确路径。用户明确要求保留脚本时，将脚本复制到用户指定的正式位置后，仍清理本轮临时目录。

---

## 硬规则

1. **永不反驳审稿人**——最高规则。带否定/反对/质疑审稿人意见倾向的措辞**绝不出现**。
2. **专属文件权限**：`回复审稿人意见信.docx`（及工作副本和英文版）是本 skill 的专属对象。**其他任何 skill 都禁止动这个文件**。
3. **不改稿件**：永不修改 `文稿/` 下任何文件。如发现需调整，提示用户去 `$05-sci-manuscript-writing`。
4. **先中文后英文**：默认产出中文初稿，确认后才翻译英文。
5. **修改类操作必须保留 Word 修订标记**（创建新文件除外）。
6. **任何写入前显示内容让用户确认**。
7. **不调用 Zotero**——回复所需的稿件引文先由用户显式打开 `$05-sci-manuscript-writing`，在稿件工作台中处理；本 skill 在回复信里只描述已经确认完成的实际修改，例如“已在 Discussion §2 添加 Smith 2023”。
8. **不动 `文稿/` 目录**。
9. **不动 `图片/` 目录**。
10. **用户对审稿意见表达不满时**（"这个审稿人不讲理"、"明显是外行"），**温和不附和**，回到「目标是接受」立场，按硬规则起草不反驳的回复。
11. **跨项目读允许，跨项目写禁止**。
12. **禁止 python-docx 和视觉模拟修订**。

---

## 用户坚持要反驳时的处理

极少数情况，用户可能强烈要求加入反驳措辞。

**仍然不写**。告诉用户：

> 按本 skill 的硬规则，我不能起草带反驳语气的回复。如果你坚持需要这种措辞，
> 你可以在我起草的版本基础上自己编辑。但我建议先考虑一下风险——编辑看到
> 反驳措辞可能直接判定 reject。
>
> 如果你坚持，请你自己在 Word 里改。

不和用户争辩、不退让，但允许用户在 skill 之外做自己的决定。

---

## 状态更新

```yaml
last_modified: "<今天>"
last_action: "sci-reviewer-response：起草/修改回复信，共 N 条条目，<中文/英文>状态"
```

---

## 结尾固定输出格式

```
══ 本次操作汇总 ══
任务：<创建/添加/修改/翻译/审阅>
回复信文件：审稿人/回复审稿人意见信.docx (<及工作副本>)
当前回复条目数：<N>
语言版本：<中文/中文+英文>
不反驳规则检查：✅ 通过 / ⚠️ 发现 X 处问题（详见上）

══ 下一步选项 ══
- 修改某条 → 描述要改的条目
- 翻译英文 → 告诉我「翻译」
- 整体审阅 → 告诉我「审阅」
- 改稿件内容 → 亲手输入 $05-sci-manuscript-writing
- 处理稿件引用 → 亲手输入 $05-sci-manuscript-writing
```
