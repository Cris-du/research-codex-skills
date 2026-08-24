# 图片规划

项目：{{PROJECT_NAME}}

项目根：`{{PROJECT_ROOT}}`

规划范围：{{PLAN_SCOPE}}

规划状态：{{DRAFT_OR_APPROVED}}

批准记录：{{APPROVAL_DATE_AND_SCOPE}}

## 权威输入

- 02 证据与展示规划：`{{DESIGN_PATH_OR_USER_BRIEF}}`
- 03 单元解释根：`{{EXPLANATION_ROOT}}`
- 03 SVG 单图根：`{{FIGURE_UNIT_ROOT}}`
- 路径版本：{{CURRENT_OR_LEGACY_MAPPING}}

## Fig 规划

### {{FIG_ID}}｜{{FIG_ROLE}}

- 服务证据：{{EVIDENCE_IDS_AND_WORDING}}
- 布局：{{ROWS_COLUMNS_AND_HIERARCHY}}
- panel 关系：{{SHARED_LEGEND_COLORS_ALIGNMENT_SCALE}}

| Panel | 内容判定 | 形式判定 | 图型 | SVG 来源 | 解释来源 | 选择理由 |
|---|---|---|---|---|---|---|
| {{PANEL}} | {{CONTENT_DECISION}} | {{FORM_DECISION}} | {{PLOT_TYPE}} | `{{SVG_PATH}}` | `{{EXPLANATION_PATH}}` | {{RATIONALE}} |

## 被拒绝候选

| 服务证据 | 候选 | 象限 | 拒绝理由 | 回流动作 |
|---|---|---|---|---|
| {{EVIDENCE}} | `{{CANDIDATE_PATH}}` | {{QUADRANT}} | {{REASON}} | {{RETURN_ACTION}} |

## 缺口与回流 03

- {{PRECISE_GAP_OR_NONE}}

## 双向覆盖检查

- 02 → 04：{{COVERAGE_RESULT}}
- 04 → 02：{{REVERSE_COVERAGE_RESULT}}

## 执行清单

- 计划生成：`{{FIG_OUTPUT_PATH}}`
- 计划保留脚本：`{{BUILD_SCRIPT_PATH}}`
- 计划图注：`{{CAPTION_PATH}}`
- 明确不修改：02、03、`PROJECT.md`、期刊规格、未点名的既有 Fig
