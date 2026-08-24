# Input and path contracts

## Resolve the project root

Accept one project-root path. Resolve it to an absolute path before discovery. Derive all other paths from that root; do not ask for each file separately when the scaffold is recognizable.

## Preferred current scaffold

Read these current paths first:

```text
02_实验设计.md
03_数据与分析/
└── 主库/
    ├── 图文单元/
    │   └── 图/
    └── 单元解释/

04_结果主库/
├── 图片规划.md
├── 自制图/
├── Fig/
└── 脚本/
```

Within `图文单元/图/`, accept only `.svg` candidates. Match explanations to figures by explicit paths or stable names recorded in the explanation; never rely on similar filenames alone when the mapping is uncertain.

## Upstream absence

- If `02_实验设计.md` is empty or absent during Overview/Plan, ask the user for the evidence and display intentions in natural language; do not claim that a plan was derived from 02.
- If explanations are absent, request the minimum content needed to judge each candidate: scientific claim, data subset, comparison, axes/encodings, and statistical meaning.
- If an SVG is absent, classify the gap precisely. Do not create a replacement data plot in 04.
- In Full-auto, treat any missing upstream meaning as blocking.

## Legacy discovery adapter

Some older 03 workflows may expose figure or explanation material under names such as:

```text
信息单元库/
图文单元库/图/
图文单元库/文/
结果/单元库/
```

Apply these rules:

1. Prefer the current scaffold when it contains the authoritative material.
2. If only one coherent legacy root exists, map it read-only and report the exact mapping before continuing.
3. If current and legacy roots both contain candidate material, stop and ask which root is authoritative.
4. Never merge candidates or explanations across roots silently.
5. Never rename, move, normalize, or repair legacy material from this skill.

## SVG input boundary

- Reject PDF, PNG, TIFF/TIF, JPEG, EPS, and other non-SVG files as assembly sources.
- Reject malformed SVG, external file/URL references, scripts, event handlers, and `foreignObject`.
- Allow embedded `data:` images only with an explicit warning that their interior is raster and not element-editable.
- Report zero editable `<text>` elements. When later text editing is required, block and request an SVG whose text remains text.
- Do not auto-convert or trace non-SVG input. Return an exact replot request to 03.

## Explanation-to-figure linkage

For every selected SVG, retain:

- Absolute or project-relative source path.
- Corresponding explanation source.
- Evidence ID or exact evidence wording from 02.
- Content decision and form decision.
- Selection reason when multiple candidates are content- and form-correct.

Treat an unlinked explanation or ambiguous figure name as unresolved, not as a match.
