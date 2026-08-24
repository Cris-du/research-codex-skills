# Modes and routing

## Mode table

| Mode | Use for | Persistent writes | Stop condition |
|---|---|---|---|
| Overview | State inspection and route recommendation | None | After reporting state and next route |
| Plan | A complete figure set or any figure needing user selection | `图片规划.md`, only after approval | After the approved plan is saved for user review |
| Assemble | An already approved figure plan | New approved Fig and build script | After technical and visual verification |
| Refine | Named corrections to an existing Fig | Only the named Fig and refinement script | When named changes pass verification |
| Full-auto | One named Fig, explicitly requested as full-auto/direct generation | That Fig, its build script, and later caption if requested | Immediately on ambiguity, a gap, conflict, or invalid input |
| Caption | Same-name Fig caption | One approved `.txt` sidecar | After evidence and panel coverage checks |

## Routing rules

1. Start in Overview when the request is exploratory, asks what is possible, or does not identify a Fig/set.
2. Use Plan for multiple Figs, a complete paper figure set, candidate selection, or any unresolved evidence mapping.
3. Use Assemble only when the user has approved the plan content, not merely the existence of a plan file.
4. Use Refine only after a preview exists and the user names concrete changes.
5. Use Full-auto only when all are true:
   - The user explicitly says `全自动`, `直接生成`, or an equivalent instruction.
   - Exactly one target Fig is named.
   - The project root and authoritative 02/03 inputs are unambiguous.
   - Evidence mapping and SVG inputs are complete.
   - No target output already exists unless the user explicitly approved replacing it.
6. Run Caption after Assemble/Refine, or independently when the final Fig and evidence mapping already exist.

## Interaction pattern

At the start of every run, state:

```text
模式：<Overview|Plan|Assemble|Refine|Full-auto|Caption>
项目根：<absolute path>
本轮写入：<none or exact 04 paths>
输入状态：<02, explanations, SVGs, approved plan>
```

Do not interpret selecting the skill chip alone as permission to write. Infer write permission only from the concrete request and the mode rules. In Plan, always present the plan before saving it. In Assemble, confirm that the displayed plan is the approved version. In Refine, preserve everything the user did not name.

## Route examples

- `先看看这个项目的 04 做到哪了` → Overview.
- `给整篇论文规划 Fig 1–5` → Plan.
- `按刚确认的图片规划拼 Fig 2` → Assemble.
- `把 Fig 2 的 B 标签右移，别改其他内容` → Refine.
- `全自动生成 Fig 2` → Full-auto, subject to all hard gates.
- `给 Fig 2 写图注` → Caption.
