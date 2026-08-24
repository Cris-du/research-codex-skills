---
name: build-research-presentations
description: >-
  Create or update editable PowerPoint decks for one research-paper project by synthesizing its PROJECT.md and 01–05 materials. Use for incremental lab or group-meeting reports about recent work, results, blockers, decisions, and next steps, or panoramic proposal, midterm, defense, collaborator-handoff, conference, and major-group presentations covering the project from question to plan and evidence. Also use to revise an unfinished or archived project deck when the requested changes concern its scientific narrative or selected project materials. Own project discovery, reporting-mode routing, source selection, project-relative provenance, and archive placement; use the Presentations skill for PPTX construction, rendering, and visual QA. Do not use for generic slide editing detached from a research project, business reporting, feedback persistence, experimental-design changes, new analysis, scientific-figure reconstruction, manuscript writing, or external sharing.
---

# Build Research Presentations

把一个科研论文项目中已经形成的材料组织成可编辑、可追溯并经过视觉检查的 PPT。只负责汇报，不把 PPT 变成新的项目事实源。

## 读取适用合同

- 始终完整读取 [modes-and-routing.md](references/modes-and-routing.md) 和 [source-and-filesystem-contracts.md](references/source-and-filesystem-contracts.md)。
- 规划、创建或修改实际 PPT 时，另完整读取 [scientific-content-qa.md](references/scientific-content-qa.md) 与 [visual-storyboard-and-scientific-layout.md](references/visual-storyboard-and-scientific-layout.md)。
- 创建或编辑 `.pptx` 前，使用并完整遵守当前安装的 `Presentations` Skill。让它负责演示文稿实现、模板继承、渲染、溢出检查和视觉验收；本 Skill 负责科研语境、内容来源和归档边界。

## 保持模块所有权

- 从用户明确路径或无歧义上下文确定唯一项目根目录。
- 只读 `PROJECT.md`、`01_立项与选题论证.md`、`02_实验设计.md`、`03_数据与分析/`、`04_结果主库/`、`05_论文全周期/`及既有汇报。
- 只在用户明确要求创建或修改汇报时，写入 `项目汇报/组会汇报/`或`项目汇报/项目汇报/`中的目标 PPT。
- 不修改 `PROJECT.md` 或 `01–05`，不建立永久素材清单、汇报日志、来源数据库或中间规划文件。
- 不执行分析，不重画数据图，不改变统计值，不重组论文 Fig，不撰写论文正文。
- 不上传、发送、共享或公开 PPT；这些都是独立外部动作。

如果项目根不唯一、关键材料身份冲突或目标 PPT 不明确，先停止写入并让用户确定边界。

## 选择唯一业务模式

选择且只选择一个业务模式：

1. **组会增量**：回答“上次汇报以后发生了什么”。
2. **项目全景**：回答“这个项目从研究问题到计划、结果和下一步整体是什么”。

修改既有 PPT 不是第三种模式。先判断该 PPT 属于增量还是全景，再沿用对应合同。完整背景与近期进展同时出现时，走全景模式并增加近期进展板块。

模式仍会实质改变读取范围或叙事时，只问一个模式问题。不要同时制作两套。

## 区分讨论、检查与写入

- 讨论、规划或检查：给出人类可审阅的页面故事板、素材候选、冲突和建议，不写文件。页面故事板必须让用户能看出每页在讲什么、图文如何组合、结果与结论分别放在哪里；不能只给标题列表或素材清单。
- 创建或修改：用户明确要求制作、更新或改写某场科研汇报时，可写入已确定的目标 PPT。
- 组会增量在没有会改变结论的取舍时可直接生成初稿；但制作前先向用户展示精简页面故事板，使其能检查页面顺序、图文组合和结论边界。
- 项目全景默认先展示页面故事板、关键结果候选和缺口，取得用户对故事与取舍的确认后再生成。
- 已归档 PPT 不因当前项目变化而回写。修改历史场次时，必须由用户明确指向该文件；非同一场汇报不得静默覆盖。

## 执行共同流程

1. 显示项目根、业务模式、听众、场景、日期、时长或页数、语言和目标文件。
2. 按模式发现材料，区分已确认事实、解释、当前假设、缺口和冲突。
3. 为每页建立明确的沟通任务和视觉构图；只选服务该任务的素材。按 `visual-storyboard-and-scientific-layout.md` 生成页面故事板，明确思路、结果、结论、结论边界、主图、辅助图、图旁文字和阅读顺序。
4. 对会改变科学含义、结果取舍、外部可见范围或项目故事的事项，让用户判断。
5. 使用 `Presentations` Skill 创建或编辑可编辑 `.pptx`，不以整页截图代替可编辑页面。实施时遵守页面故事板的证据组合和图片比例规则：所有图片完整适配，不裁剪、不拉伸、不压缩。
6. 在备注中保存必要的项目相对来源和外部来源，不把内部制作说明显示在页面上。
7. 渲染并逐页检查全部幻灯片；同时检查结果与结论是否混淆、页面证据密度是否过低、图形是否变形；修复后复验。
8. 核对最终文件名与归档位置，报告使用和未使用的关键材料、冲突、缺口及没有执行的外部动作。
9. 若本次汇报反映出已确认的项目状态变化，只向用户提供简短状态交接；由 `$manage-research-project` 决定是否更新 `PROJECT.md`。

## 正确处理反馈

- 版式、措辞、页序、背景压缩、结果突出等只影响当前 PPT 的反馈，可直接落实到目标 PPT。
- 改变研究问题、证据判断、技术路线、任务优先级或项目下一步的反馈，不得先写进 PPT 并冒充已确认事实；说明其项目层影响并让渡给 `$manage-research-project`、`$research-project-framing`或`$research-study-design`。
- 同一条反馈同时包含汇报表达和项目决策时，拆开处理：先执行已明确的 PPT 局部修改，把项目决策部分保持未决并报告。

## 完成标准

- 最终交付物为可编辑 `.pptx`；PDF 仅在用户明确要求时额外交付。
- 每个关键结论都能回到项目材料或明确的外部来源。
- 没有虚构结果、进度、卡点、决定或计划。
- 没有未解释的材料冲突或科学内容缺口。
- 全部页面已经渲染、逐页检查并通过必要复验。
- 中间渲染、草稿资产和临时文件已经清理，仅保留最终汇报文件。
- `PROJECT.md`、`01–05`和既有科研图均未被修改。
