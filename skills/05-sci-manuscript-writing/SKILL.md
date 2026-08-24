---
name: 05-sci-manuscript-writing
description: >-
  05 research-manuscript workspace for one research-paper project. Use only after the user explicitly invokes $05-sci-manuscript-writing in the current Codex task. Once opened, keep it active for subsequent natural-language requests in the same task until the user explicitly closes it or invokes another skill. Draft, revise, translate, and format manuscript prose in the requested language. Follow natural-language intent: direct-edit requests write without an extra confirmation, while discussion or preview requests stay in chat. During initial drafting, edit the draft DOCX in place without _working copies or tracked changes unless requested. Insert existing figures and tables, manage captions, numbering, resolution and text references, and maintain Zotero-backed citations. Read PROJECT.md and 01-04 as evidence but never modify them, fabricate evidence, analyze data, reconstruct figures, edit reviewer-response files, or update PROJECT.md.
---

# 05 SCI 稿件工作台 · 05-sci-manuscript-writing

在一个 Codex 任务中持续负责同一科研项目的稿件正文、已有图表和引文。语言由用户当前请求或目标稿件决定，不设置中文初稿、中文修改、英文翻译、英文修改等启动模式。

## 会话生命周期

1. 新任务开始时保持关闭。只有用户亲手输入 `$05-sci-manuscript-writing` 才打开。
2. 打开后，在当前任务内把后续与稿件有关的自然语言请求作为本工作台的连续操作，不要求用户重复输入 skill 名。
3. 用户明确说“关闭论文写作”时关闭。
4. 用户亲手输入其他 `$skill-name` 时，先关闭本工作台，再让该 skill 工作。内部使用文档、Zotero 或渲染工具不算用户切换 skill。
5. 普通插问不自动关闭，也不得被强行解释成稿件任务。
6. 关闭后若要继续，必须再次显式输入 `$05-sci-manuscript-writing`。

不要在磁盘创建“active”标记或会话状态文件。只依赖当前 Codex 任务上下文判断开关状态。

## 启动与项目定位

首次打开时：

1. 从用户明确提供的路径、当前工作目录或无歧义上下文定位一个项目根目录；无法唯一定位时只问一个必要问题。
2. 只读扫描 `PROJECT.md`、`01_立项与选题论证.md`、`02_实验设计.md`、`03_数据与分析/`、`04_结果主库/`、`05_论文全周期/` 和现有 DOCX。
3. 识别当前活动稿件；只有候选不唯一或目标位置不清楚时才询问。用户已点名文件或只有一个合理候选时直接采用。优先使用当前科研线的 `05_论文全周期/投前论文成稿/`，但兼容用户明确指定的旧项目目录。
4. 记录会话内的项目根目录、活动稿件、当前编辑策略和当前语言，不写全局配置或活动状态文件。
5. 读取 [research-inputs-and-drafting.md](references/research-inputs-and-drafting.md)，先判断材料是否足以支持当前写作请求。

## 意图路由

根据用户自然语言直接路由，不显示固定模式菜单：

- 起草、续写、重组、压缩、润色、翻译或语言修改：读取 [research-inputs-and-drafting.md](references/research-inputs-and-drafting.md)。
- 新建、修改、另存、存一版或处理 Word 修订：读取 [docx-workflow.md](references/docx-workflow.md)。
- 插入已有图表、处理编号、图注/表题、Figure/Table List、分辨率或正文引用对应：读取 [figures-and-tables.md](references/figures-and-tables.md)。
- 检查、匹配、插入、替换、删除或整理引文和参考文献：读取 [citations-and-references.md](references/citations-and-references.md)。
- 全稿检查、提交前检查或写入后验证：读取 [manuscript-qa.md](references/manuscript-qa.md)。

同一请求可以组合多个路由。只读取本次实际需要的 reference；不要为简单续写加载全部文件。

## 语言判断

1. 用户明确指定语言时服从用户。
2. 用户未指定但活动稿件或所选段落的语言明确时沿用原语言。
3. 用户要求翻译时严格保留科学含义、数值、引用和图表引用。
4. 请求与稿件语言都不明确时才问一次。
5. 语言变化不关闭本工作台，也不自动创建一套阶段文件。

## 自然语言驱动的执行策略

先根据用户本轮表达和当前上下文判断模式，不机械增加确认轮次：

1. **直接执行**：用户说“直接改”“写进去”“按这个改”“继续写”“你看着处理”等，且目标与范围可确定时，直接修改目标 DOCX；这类表述本身就是本轮写入授权。
2. **仅讨论**：用户说“先看看”“先给方案”“先在会话里改”“不要写文件”等时，只在会话中分析或起草，不修改 DOCX。
3. **先预览**：用户明确要求“先给我确认”“先展示改法”“确认后再写”等时，先给预览，等用户确认后再落盘。
4. 只有目标文件不唯一、科学含义无法可靠推断、Zotero 存在多个合理候选且无法消歧，或用户没有授权但操作会大范围删除或重排内容时，才主动询问。
5. “你看着处理”只授权在已提出任务范围内选择合理实现，不授权扩展研究结论、编造数据或改写上游材料。

识别到处于初稿阶段——例如用户称其为初稿、草稿、第一版，要求从零起草或继续搭建正文——默认直接在该初稿 DOCX 上修改，不创建 `_working.docx`，也不默认开启修订模式。只有用户明确要求副本、备份、版本节点或修订痕迹时才创建相应文件或真实 Word 修订。

对于成熟稿件、导师修改稿、返修稿或其他后期版本，同样由自然语言决定：用户要求原位修改就原位修改，要求保留原稿就在副本上改，要求修订模式就使用真实 Word 修订。完成任何 DOCX 写入后都要执行 [manuscript-qa.md](references/manuscript-qa.md) 中与本轮改动相称的结构、版式、图表、引用和文件完整性检查。

## 临时辅助脚本与收尾清理

- 可以为完成本轮要求编写和运行 Python、PowerShell 或其他辅助脚本，但脚本只用于实现本 skill 已有职责，不得借此扩展到数据分析、科研制图或其他越界任务。
- 只有确实需要临时代码或中间文件时才创建临时目录。每轮执行只创建一个本轮专属目录；优先使用系统临时目录，若工具必须在项目内运行，则直接使用 `05_论文全周期/.codex-05-tmp-<skill>-<唯一标识>/`，不要再创建分散的临时目录。
- 必须创建全新且原先不存在的目录；若候选路径已存在，换一个唯一标识，禁止复用、清空或接管已有目录。把本轮生成的脚本、解包文件、中间渲染、日志、缓存、临时副本和 QA 产物全部放进该目录。
- 正式稿件、正式图片、报告及其他用户交付物必须写到约定目标位置，绝不能只放在临时目录里。创建临时目录时记录其规范化绝对路径，并在其中写入 `.codex-05-temp-owner.json`，至少记录 skill 名、本轮唯一标识、创建时间和该绝对路径。
- 不得把用户已有脚本、源文件或其他任务的临时目录移入其中，也不得把它们当作可清理对象。
- 正式结果写入并验证成功后，才算进入完成清理：先确认交付物位于临时目录之外，再确认待删路径等于本轮记录路径、归属标记内容完全匹配、名称符合专属前缀，且不是磁盘根、项目根、`05_论文全周期/` 或任何正式输出目录；然后只按该精确路径递归删除这一个目录。
- 禁止用通配符、父目录、模糊匹配、全盘搜索结果或未解析变量执行清理；禁止顺手删除相邻文件、空目录、旧临时目录或其他任务产物。若任务取消、失败或停止，也在上述安全条件满足时清理本轮目录。
- 清理失败时不得扩大删除范围，也不得宣称任务已完全收尾；报告唯一残留目录的精确路径。用户明确要求保留脚本时，将其复制到用户指定的正式位置后，仍清理本轮临时目录。

## 所有权与边界

- 只写当前任务明确指向的 05 稿件及用户要求的副本、里程碑和稿件附属文件。
- `PROJECT.md` 和 01-04 始终只读。状态变化只在对话中形成交接，由 `$manage-research-project` 另行处理。
- 不修改 `04_结果主库` 中的 Fig、图注源文件或构建脚本；只把已有成果用于稿件。
- 不运行分析，不改统计值，不虚构数值、样本量、方法、机制、图表或文献。
- 不生成、重画或科学重组 Fig。需要新图、数据图重绘或 panel 重组时，说明缺口；只有用户显式调用相应 skill 后才切换并关闭本工作台。
- 不修改 `审稿人/` 下的审稿意见、解析报告或 `回复审稿人意见信.docx`。这些归审稿相关 skill。
- 不跨项目写入。允许只读比较用户指定的模板、前作或其他项目材料，但不得把其中事实冒充为当前项目证据。

## 结束报告

简洁报告：

- 当前活动稿件和本轮编辑方式（原位、副本或修订模式）；
- 本次完成的正文、图表和引文变更；
- 结构、修订、引用、分辨率和视觉验证结果；
- 尚未解决的证据、图表、引用或格式缺口；
- 若项目状态发生变化，给出供 `$manage-research-project` 使用的状态交接，但不直接写 `PROJECT.md`。
