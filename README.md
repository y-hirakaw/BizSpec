# BizSpec

> The YAML-first BPMN for the AI agent era — design business processes your agents can actually run.

[![CI](https://github.com/y-hirakaw/BizSpec/actions/workflows/test.yml/badge.svg)](https://github.com/y-hirakaw/BizSpec/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-experimental-orange)

English | [日本語](README.ja.md)

> **Work in progress.** This project is at an early, experimental stage. APIs and file formats may change.

> ⚠️ **Direction is currently being reworked (May 2026).**
> The original "decompose every process into YAML" approach is being narrowed.
> The new direction is **CSV-first inventory (`bizspec/portfolio.csv`) for triage, with YAML reserved for units that actually escalate to AI-executable specs**.
> The screenshots and skill descriptions below still reflect the YAML-first design and will be updated once the new model is validated by dogfooding.
> Background and rationale: see [`BizSpec_設計メモ_2026-05-08.md`](BizSpec_設計メモ_2026-05-08.md) (Japanese).

**BizSpec** decomposes a business workflow into the smallest executable units (YAML), tags each one as `script` / `ai_agent` / `manual`, and visualizes the flow as clickable HTML. Pair it with Claude Code skills (`/bizspec-refine`, `/bizspec-refactor`) to refine processes interactively.

![Leverage heatmap — units sorted by cost × ease × automation gap. The top-left "Quick Win" cell is high-cost, easy-to-automate, manual work.](design/readme1.png)

<details>
<summary>More views</summary>

<br>

**Process detail** — DAG of one process plus per-unit metrics (effort × frequency × difficulty), IO, scope, and rules.

![Process detail view: PR review with Logic review selected](design/readme2.png)

**All processes overview** — KPIs and a cross-process table at a glance.

![Overview view: 12 processes summarized](design/readme3.png)

</details>

## Quick start

```sh
git clone https://github.com/y-hirakaw/BizSpec.git
cd BizSpec
uv pip install -e .
bizspec init                      # install Claude Code skills
bizspec viz                       # generate bizspec/_viz/index.html on the bundled samples
```

## Why BizSpec?

- **Executable, not decorative** — Mermaid and draw.io are drawing tools. BizSpec defines `executor` / IPO / `link` in YAML so that an AI agent, script, or human can actually run the steps.
- **Git-native and AI-refactorable** — YAML diffs cleanly, reviews well in PRs, and is grep-friendly. Claude Code Skills (`/bizspec-refine`, `/bizspec-refactor`) let an AI refactor processes directly.
- **Cost-aware visualization** — `effort × frequency` drives a heatmap in `bizspec viz`, surfacing where monthly time is being spent.

## What it does

- **Install skills** — `bizspec init` copies Claude Code skills into `.claude/skills/`
- **Decompose / refactor** — `/bizspec-refine` and `/bizspec-refactor` Claude Code skills
- **Scaffold / search / list / validate** — `bizspec new` / `search` / `list` / `validate` (with `--format json` for CI)
- **Rename / remove / renumber** — `bizspec rename` / `rm` / `renumber` (one-shot link-reference updates, flow-break detection)
- **Visualize** — `bizspec viz` produces per-process HTML diagrams and a unified `index.html` for all processes

The `bizspec/` directory contains two worked examples:
- `issue-refinement/` — a PBI refinement process decomposed into 9 units
- `pr-review/` — a PR review process with branching and merging (4 units)

## Documentation

- [YAML schema reference](docs/yaml-spec.md) — fields, responsibility rubric, disambiguation rules
- [CLI reference](docs/cli.md) — all commands, options, and examples

## Repository layout

```
bizspec/
  <process-name>/      # one directory per process
    <unit-name>.yaml   # one file per unit
  _viz/                # generated HTML diagrams (bizspec viz output)
    index.html         # unified view of all processes
src/bizspec/
  core/                # shared layer (loader / errors / model)
  viz/                 # bizspec viz implementation (layout / builder / cmd / templates)
  skills/              # skills bundled with the package (source of truth, copied by bizspec init)
.claude/skills/        # skills copied for use in Claude Code
docs/
  yaml-spec.md
  cli.md
```

## Contributing

Bug reports, feature requests, and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, project layout, and the development workflow.

Looking for a starting point? Issues labeled `good first issue` are designed for first-time contributors.

## License

MIT License — see [LICENSE](LICENSE).
