---
name: build-research-figures
description: Plan, audit, assemble, refine, and caption publication-independent research figure panels from a project's 02 evidence plan and 03 SVG figure units. Use when the user explicitly invokes this skill to inspect 04 status, plan a figure set, build one or more Fig SVGs, apply named visual refinements, or create same-name caption sidecars under 04_结果主库.
---

# Build Research Figures

Turn the evidence and display intentions in 02 plus the real SVG units and explanations in 03 into traceable, publication-independent Fig products in 04. Select and assemble existing scientific plots; do not perform analyses or redraw data plots.

## Load the applicable contracts

Read these references before acting:

- Always read [modes-and-routing.md](references/modes-and-routing.md), [input-and-path-contracts.md](references/input-and-path-contracts.md), and [filesystem-boundaries.md](references/filesystem-boundaries.md).
- For planning or full-auto work, also read [planning-and-matching.md](references/planning-and-matching.md).
- For assembly or refinement, also read [svg-execution-and-refinement.md](references/svg-execution-and-refinement.md).
- For captions or completion handoff, also read [captions-and-handoff.md](references/captions-and-handoff.md).

Treat every referenced contract as binding. Stop when contracts conflict with the project state; report the conflict instead of guessing.

## Preserve the module boundary

- Read 02 and 03 as upstream evidence. Never modify them.
- Write only approved 04 outputs. Never modify `PROJECT.md`; report status changes for `$manage-research-project` to apply separately.
- Never run analyses, alter scientific values, reinterpret missing statistics, or fabricate evidence.
- Never redraw an unsuitable data plot in 04. Return content-correct/form-wrong work to 03 for replotting, and content-wrong work to 03 for analysis.
- Accept SVG sources only. Keep editable text as `<text>`; reject non-SVG inputs and text converted entirely to outlines when editable text is required.
- Keep 03 sources in place. Embed their SVG content into the final self-contained Fig, but do not copy standalone source files into 04.
- Produce publication-independent composition only. Leave journal dimensions, DPI, font-size adaptation, and export formats to 05.

## Route the request

Choose exactly one primary mode:

1. **Overview** — inspect the project and recommend the next route; remain read-only.
2. **Plan** — match 02 evidence to 03 units, write or update `04_结果主库/图片规划.md` only after explicit approval, then stop for review.
3. **Assemble** — execute an already approved plan mechanically; do not change scientific selection.
4. **Refine** — change only user-named elements in an existing Fig and record the same changes in a reproducible script.
5. **Full-auto** — plan and assemble exactly one named Fig without an intermediate pause only when the user explicitly requests full-auto/direct generation and all inputs are unambiguous.
6. **Caption** — create or revise the same-name `.txt` sidecar from the approved evidence mapping, 03 explanations, and the actual final Fig.

If the mode is unclear, default to Overview. If the user asks for a complete figure set, route to Plan. If the user asks for one Fig but does not explicitly request full-auto, route to Plan first.

## Execute the common workflow

1. Resolve and display the absolute project root.
2. Discover inputs without writing. Prefer the current scaffold; never silently mix current and legacy roots.
3. State the mode, inputs found, missing inputs, output scope, and whether the turn is read-only.
4. In Plan or Full-auto, perform content-first matching and the reverse coverage check.
5. Before any persistent write outside an explicitly requested Full-auto run, show the exact paths and operations and obtain explicit approval.
6. Before assembly, run `scripts/audit_svg_inputs.py` on every selected SVG and resolve all blocking findings.
7. Assemble deterministically from an approved layout. Preserve a project-local build script under `04_结果主库/脚本/`.
8. Run `scripts/verify_svg_figure.py`, render a preview with an available local renderer, inspect the complete figure, fix visible defects, and repeat verification. If no renderer exists, report that visual QA remains incomplete.
9. Generate the caption only from mapped evidence and recorded explanations.
10. Report created/modified files, rejected candidates, unresolved gaps, verification evidence, and the structured handoff for project status.

## Gate writes and conflicts

For a write preview, list:

- Project root and authoritative input roots.
- Each selected and rejected candidate with its evidence mapping and reason.
- Missing evidence or form requirements.
- Fig/panel layout and panel labels.
- Every directory and file to create or modify.
- Existing-output conflicts and the exact overwrite requested.
- Explicit exclusions, including 02, 03, `PROJECT.md`, journal adaptation, and unrequested refinements.

Treat approval as scoped to the displayed operations. Never silently overwrite an existing plan, Fig, caption, or script. A Refine request authorizes only the named changes. Full-auto authorization applies only to the one named Fig and must stop on any gap, ambiguous authority, invalid SVG, or existing-output conflict.

## Use the bundled resources

- Use `assets/FIGURE_PLAN.template.md` when creating `图片规划.md`.
- Use `assets/build_figure.template.py` as the base for each retained `build_Fig_N.py`.
- Use `assets/refine_figure.template.py` as the base for each retained refinement script.
- Use `scripts/assemble_svg_figure.py` for deterministic composition from a reviewed JSON layout spec.
- Use `scripts/audit_svg_inputs.py` and `scripts/verify_svg_figure.py` as hard preflight and postflight gates.

Run scripts with the active Python interpreter and UTF-8 mode where available. Preview commands first when a script offers `--dry-run`. Do not install dependencies or use network access without separate authorization.
