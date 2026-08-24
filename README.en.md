# Research Codex Skills

[中文说明](README.md) · [MIT License](LICENSE)

A Chinese-first suite of 13 Codex Skills for end-to-end research-paper projects: project management, question framing, study design, reproducible data analysis, figure assembly, manuscript work, peer-review responses, presentations, and reader-facing GitHub repositories.

> [!IMPORTANT]
> This is a community-maintained project, not an official OpenAI Skill collection. Researchers remain responsible for scientific design, statistical choices, evidence interpretation, citation accuracy, privacy, and final publication decisions.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `manage-research-project` | Initialize the project scaffold, maintain `PROJECT.md`, and safely copy selected materials |
| `research-project-framing` | Refine the research question, gap, novelty, and expected contribution |
| `research-study-design` | Expand a question into evidence, one main technical route, data products, and figure intentions |
| `data-analysis-explanation` | Maintain the data-unit explanation system |
| `data-analysis-auto` | Plan, execute, reproduce, and document data-analysis tasks |
| `data-analysis-audit` | Read-only semantic audit of task descriptions, plans, and business source code |
| `build-research-figures` | Plan and assemble publication-independent SVG figure sets and captions |
| `05-sci-publish` | Route publication-stage work to the correct manuscript or review Skill |
| `05-sci-manuscript-writing` | Draft, revise, translate, format, and maintain manuscripts |
| `05-sci-reviewer-parsing` | Parse reviewer comments into a structured Chinese issue list |
| `05-sci-reviewer-response` | Draft and maintain reviewer-response letters |
| `build-research-presentations` | Create editable research-project presentations |
| `github-research-repo` | Build and audit reproducible reader-facing methods-and-code repositories |

The detailed Skill instructions are primarily in Chinese because they encode a Chinese-language research workflow. English contributions are welcome.

## Install

### Install one Skill with Codex

```text
$skill-installer install the Skill from https://github.com/Cris-du/research-codex-skills/tree/main/skills/manage-research-project
```

### Install the complete suite

```bash
git clone https://github.com/Cris-du/research-codex-skills.git
cd research-codex-skills
python scripts/install.py
```

Install selected Skills only:

```bash
python scripts/install.py --skill data-analysis-auto --skill data-analysis-explanation
```

The default destination is `$CODEX_HOME/skills/` when `CODEX_HOME` is set, otherwise `~/.codex/skills/`. The installer performs a complete conflict preflight and never overwrites an existing Skill directory. Start a new Codex task after installation.

You may also copy an entire `skills/<skill-name>/` directory into `<CODEX_HOME>/skills/`. Keep its `agents/`, `scripts/`, `references/`, and `assets/` resources with `SKILL.md`.

## Configure Your Paths

The public release contains no author-specific drive, username, or sync-root path.

### `RESEARCH_PROJECTS_ROOT`

Recommended. Point it to the directory that contains your research-project folders:

```powershell
$env:RESEARCH_PROJECTS_ROOT = 'D:\Research\Projects'
```

```bash
export RESEARCH_PROJECTS_ROOT="/data/research/projects"
```

The analysis Skills resolve the project root in this order:

1. a path explicitly supplied in the current request;
2. `RESEARCH_PROJECTS_ROOT`;
3. a root derived from the fixed project scaffold under the current working directory;
4. one unique scaffold candidate inside the open workspace.

They do not scan the whole computer. If resolution is ambiguous, they stop and ask.

### `RESEARCH_PLOT_LIBRARY_ROOT` (optional)

Point this to your reusable R plotting-template library if you have one:

```bash
export RESEARCH_PLOT_LIBRARY_ROOT="/data/research/plot-library"
```

It may contain optional `Rscript_exe.txt` and `R.txt` configuration files. When no shared plotting library exists, `data-analysis-auto` uses a parameterized, task-local R script instead of referring to a private library.

### `RESEARCH_RSCRIPT` (optional)

If `Rscript` is not on `PATH`, provide its absolute executable path:

```bash
export RESEARCH_RSCRIPT="/opt/R/bin/Rscript"
```

The runtime checks `RESEARCH_RSCRIPT`, an optional plotting-library candidate list, and then `PATH`.

## Expected Project Scaffold

`RESEARCH_PROJECTS_ROOT` may be anywhere, but each project follows this internal structure:

```text
<RESEARCH_PROJECTS_ROOT>/<project-name>/
├── PROJECT.md
├── 01_立项与选题论证.md
├── 02_实验设计.md
├── 03_数据与分析/
├── 04_结果主库/
├── 05_论文全周期/
├── 项目汇报/
└── Git/
```

Invoke `$manage-research-project` to preview and, after explicit approval, create the full scaffold.

## Requirements

- A Codex environment with Skills support.
- Python 3.10+ for bundled helpers; the helpers use only the standard library.
- PowerShell and Python for the full `data-analysis-auto` pipeline; R/Rscript is required for plotting tasks.
- Codex Spreadsheets for planning and explanation workbooks.
- Codex Documents for DOCX manuscript and response work; Zotero is optional.
- Codex Presentations for PPTX reports.
- Git plus a GitHub connection or authenticated GitHub CLI for `github-research-repo`.

These dependencies are modular. For example, question framing and study design do not require R.

## Validate

```bash
python scripts/validate_skills.py
python -m compileall -q skills scripts
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and [SECURITY.md](SECURITY.md) for private-data and credential reporting guidance.

## License

Released under the [MIT License](LICENSE). Third-party tools, data, papers, fonts, and templates retain their own licenses.
