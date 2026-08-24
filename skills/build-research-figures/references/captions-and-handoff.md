# Captions and completion handoff

## Create the same-name caption

Pair every product as:

```text
04_结果主库/Fig/Fig_N.svg
04_结果主库/Fig/Fig_N.txt
```

Derive the caption from three authoritative sources:

1. The evidence mapping approved in `图片规划.md`.
2. The 03 explanation associated with each selected source.
3. The panels that actually exist in the verified final Fig.

Describe the overall question first, then each panel in label order. Include biological material, groups, axes/encodings, units or normalization, summary statistics, error bars, sample size, statistical test, multiple-testing correction, and significance notation only when those facts are explicitly documented upstream.

Never infer a p-value, sample size, statistical test, taxonomic level, normalization, or group meaning from visual appearance alone. Insert a clearly marked unresolved field in the write preview and request the missing fact instead of writing a plausible value.

Keep the caption publication-independent. Leave journal style, word limits, abbreviations policy, and typesetting to 05.

## Cross-check caption coverage

Before writing:

- Confirm that every visible panel label has exactly one caption segment.
- Confirm that every caption segment names an existing panel.
- Confirm that the evidence claim does not exceed the mapped 02 claim.
- Confirm that no rejected or removed panel remains in the caption.

Treat an existing `.txt` as a conflict; show its intended revision before replacement.

## Report completion

Report:

- Mode executed and approved scope.
- Created and modified 04 paths.
- Source SVG paths and unchanged-source hash evidence when collected.
- Technical verification result and visual-QA status.
- Evidence gaps, unresolved caption facts, and return-to-03 requests.
- Explicit exclusions: upstream files, `PROJECT.md`, and journal adaptation.

Provide this structured handoff for `$manage-research-project`; do not edit `PROJECT.md` directly:

```text
04 status: <not-started|in-progress|blocked|complete>
Completed: <planned/built/refined/captioned Fig identifiers>
Next: <next concrete action>
Blocks: <none or exact upstream gap>
Artifacts: <relative 04 paths>
```
