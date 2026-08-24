# Planning and matching

## Apply content-first matching

Process one evidence requirement at a time:

1. Extract what must be demonstrated from the 02 evidence layer.
2. Extract the intended display form from the 02 display layer.
3. Search explanation text for candidates that actually support the evidence.
4. Inspect only those candidate SVGs to judge form, encoding, legibility, and editability.
5. Classify every serious candidate in the matrix below.

Never reverse steps 3 and 4. A visually suitable chart can still contain the wrong comparison or data subset.

## Use the four-quadrant decision matrix

| Content | Form | Decision |
|---|---|---|
| Correct | Correct | Select; if several qualify, list all and choose one with a reason |
| Correct | Wrong | Form gap; ask 03 to replot the same analysis in a precisely specified form |
| Wrong | Correct | Trap; reject explicitly because the chart cannot support the evidence |
| Wrong | Wrong | Analysis gap; ask 03 for the missing analysis and required display |

Describe a gap at implementation-ready resolution. Include the data level/subset, groups, comparison, x/y encodings, units or normalization, expected plot type, and any required statistical annotation.

## Build the figure plan

Use `assets/FIGURE_PLAN.template.md`. Keep all planned Figs in one `04_结果主库/图片规划.md` unless the user explicitly requests another approved location.

For each Fig, record:

- The evidence requirement(s) served.
- The narrative role of the Fig.
- Overall rows/columns and relative panel prominence.
- Each panel label, plot type, source path, explanation path, and evidence mapping.
- Panel relationships: shared legend, consistent colors, aligned axes, common scale, or nested composition such as `A = A1 + A2`.
- Gaps and exact return-to-03 requests.
- Decisions that remain for the user.

Do not prescribe journal-specific dimensions, DPI, output format, or final font sizes.

## Run bidirectional coverage

Check both directions before approval:

1. **02 → 04:** Map every targeted evidence item to a Fig/panel or an explicit gap.
2. **04 → 02:** Map every planned Fig/panel to an evidence item. Flag attractive but unmapped material for a user decision.

Do not require all 03 material to appear in 04; unused analysis units are normal.

## Approval record

Before saving or executing a plan, show its complete candidate decisions, layout, gaps, paths, and conflicts. Record the approval date and a concise approval scope in the plan only after the user approves. Treat later scientific-selection changes as a new plan revision requiring approval.
