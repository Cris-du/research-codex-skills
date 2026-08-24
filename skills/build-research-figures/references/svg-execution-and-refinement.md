# SVG execution and refinement

## Preflight every selected source

Run:

```text
python -X utf8 scripts/audit_svg_inputs.py <source-1.svg> <source-2.svg> ...
```

Require exit code 0. Treat malformed XML, a non-SVG root, missing usable dimensions, duplicate IDs, scripts, event handlers, `foreignObject`, or external references as blocking. Treat embedded raster data and zero editable text as warnings unless the requested operation requires editing those interiors.

Do not repair a source file in 03. Return a precise request to 03 or ask the user for a compliant SVG.

## Define the approved layout

Represent composition with a UTF-8 JSON spec:

```json
{
  "width": 1800,
  "height": 1200,
  "background": "#ffffff",
  "label_style": {
    "font_family": "Arial, sans-serif",
    "font_size": 42,
    "font_weight": "bold",
    "fill": "#000000",
    "offset_x": 0,
    "offset_y": 42
  },
  "panels": [
    {
      "label": "A",
      "source": "absolute-or-spec-relative/source.svg",
      "x": 60,
      "y": 60,
      "width": 800,
      "height": 480,
      "fit": "contain"
    }
  ]
}
```

Use finite positive canvas and panel dimensions. Use `contain` by default; use `stretch` only when distortion is scientifically harmless and approved. Do not use `cover` unless deliberate clipping is part of the approved plan.

Preview without writing:

```text
python -X utf8 scripts/assemble_svg_figure.py --spec <layout.json> --output <Fig.svg> --dry-run
```

Then execute only approved new outputs. Add `--overwrite` only for an exact approved replacement.

## Preserve reproducibility

Create `04_结果主库/脚本/build_Fig_N.py` from `assets/build_figure.template.py`. Embed the reviewed layout in that script and use project-relative source paths whenever the project structure is stable. The retained script must:

- Resolve its own project root deterministically.
- Refuse an existing output unless explicitly invoked with `--overwrite`.
- Preserve source files.
- Produce the same panel order, transforms, labels, and colors.
- Print a machine-readable summary.

Keep transient layout JSON outside the project unless the user explicitly approves retaining it.

## Refine only named elements

Start from `assets/refine_figure.template.py`. Translate each user request into an explicit operation targeting a stable SVG `id` or `data-panel-label`. Supported operation patterns include:

- Set one or more attributes.
- Prefix a translate or scale transform.
- Change a panel-label text value.
- Delete one identified element.

Do not infer additional cleanup. Render a preview first. Compare pre/post structure and confirm that only target elements and required ancestors changed. Preserve the original until the user approves replacing the canonical Fig.

## Verify technically and visually

Run:

```text
python -X utf8 scripts/verify_svg_figure.py <Fig.svg> --expect-label A --expect-label B
```

Require exit code 0, then render with an already available local SVG renderer. Inspect at least:

- All expected panels and labels are present.
- No clipping, overlap, or excess whitespace obscures interpretation.
- Axes, legends, symbols, and scientific annotations remain legible.
- Panel ordering matches the approved plan.
- Shared colors and legends are internally consistent.
- No unexpected content changed during refinement.

Technical verification cannot replace visual inspection. If rendering is unavailable, mark visual QA as incomplete and do not claim a finished visual result.
