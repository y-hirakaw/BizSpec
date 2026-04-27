# BizSpec

> **Work in progress.** This project is at an early, experimental stage. APIs and file formats may change.

A tool for decomposing business processes into small, executable units (BizSpec YAML), using Claude Code skills and a CLI together. Each unit describes what to do, who executes it (script / AI agent / human), and how it connects to other units. The goal is to make implicit workflows explicit enough that an AI agent or script can run them without ambiguity.

## What it does

- **Install skills** — Install Claude Code skills into `.claude/skills/` with an interactive prompt (`bizspec init`)
- **Decompose** — Break a business process into minimum units using the `/bizspec-refine` Claude Code skill
- **Run** — Execute a process unit by unit in topological order using the `/bizspec-run` Claude Code skill
- **Refactor** — Analyze processes cross-process and propose refactoring with the `/bizspec-refactor` Claude Code skill
- **Validate** — Check BizSpec YAML files for schema errors and link consistency (`bizspec validate`)
- **List** — Show a unit summary table for a process (`bizspec list`)
- **Visualize** — Generate a clickable HTML flow diagram from the YAML link graph (`bizspec viz`)

The `bizspec/` directory contains two worked examples:
- `issue-refinement/` — a PBI refinement process decomposed into 9 units
- `pr-review/` — a PR review process with a branch-and-merge flow (4 units)

## BizSpec YAML format

Each unit is one YAML file:

```yaml
unit: ReadinessCheck
aim: Determine whether a PBI is ready for development
phase: spec
job:
  - Judge Ready / Not Ready based on the validity evaluation results
rule:
  - All of summary, scope, and acceptance criteria must be OK to mark Ready
link:
  up:
    - ContentValidation
  down:
    - StoryPointEstimation
core: true
io:
  in:
    - Evaluation results for each item
  run:
    - Aggregate evaluation results and make a judgment
  out:
    - Readiness result
executor:
  type: ai_agent
  reason: Requires synthesis of multiple evaluation results
```

`core: true` means the unit is directly required to reach the process goal. `link.up/down` represents execution order, not data dependency.

## Installation

Requires Python 3.9+.

```sh
git clone https://github.com/y-hirakaw/BizSpec.git
cd BizSpec
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

Add the installed script to your PATH if needed. The exact path depends on your environment:

```sh
# macOS system Python 3.9
export PATH="$PATH:/Users/<your-username>/Library/Python/3.9/bin"

# pyenv
pyenv rehash
```

## CLI usage

```sh
# Install Claude Code skills (interactive: local or global)
bizspec init

bizspec validate                    # validate all processes
bizspec validate issue-refinement   # validate one process

bizspec list                        # list all units
bizspec list issue-refinement       # list units in one process

bizspec viz                         # generate HTML diagrams for all processes
                                    # also generates bizspec/_viz/index.html (unified view)
bizspec viz issue-refinement        # generate HTML diagram for one process
```

The unified `index.html` shows all processes as overview cards and lets you drill into each process flow. Clicking a node highlights its connected edges.

## Repository layout

```
bizspec/
  <process-name>/       # one directory per process
    <unit-name>.yaml    # one file per unit
  _viz/                 # generated HTML diagrams (bizspec viz output)
    index.html          # unified view of all processes
src/bizspec/skills/     # skills bundled with the package (copied by bizspec init)
  bizspec-refine/
  bizspec-run/
  bizspec-refactor/
.claude/skills/         # skills installed for use in Claude Code
  bizspec-refine/
  bizspec-run/
  bizspec-refactor/
docs/
  cli.md                # CLI and skill reference
```

---

# BizSpec（日本語）

> **試作中です。** 初期の実験的な段階にあります。API やファイルフォーマットは変更される可能性があります。

Claude Code スキルと CLI を組み合わせて、業務プロセスをスクリプトや AI エージェントが迷わず実行できる最小単位（BizSpec YAML）へ分解するためのツールです。各 unit は「何をするか」「誰が実行するか（script / AI エージェント / 人間）」「前後の unit との接続」を記述します。暗黙的なワークフローを、AI エージェントやスクリプトが曖昧さなく動かせる形に明文化することを目指しています。

## できること

- **スキルのインストール** — 対話形式で Claude Code スキルを `.claude/skills/` に配置する（`bizspec init`）
- **分解** — `/bizspec-refine` スキル（Claude Code）を使って業務プロセスを最小 unit に分解する
- **実行** — `/bizspec-run` スキル（Claude Code）を使ってプロセスをトポロジカル順に unit 単位で実行する
- **リファクタリング** — `/bizspec-refactor` スキル（Claude Code）を使って複数プロセスを横断分析し、リファクタリング提案を行う
- **検証** — BizSpec YAML のスキーマエラーや link の整合性チェック（`bizspec validate`）
- **一覧表示** — プロセスの unit 一覧をテーブル表示（`bizspec list`）
- **可視化** — YAML の link グラフからクリッカブルな HTML フロー図を生成（`bizspec viz`）

`bizspec/` には 2 つのサンプルが入っています：
- `issue-refinement/` — PBI リファインメントプロセスを 9 unit に分解した例
- `pr-review/` — 分岐と合流を含む PR レビュープロセス（4 unit）

## BizSpec YAML フォーマット

unit ごとに 1 つの YAML ファイル：

```yaml
unit: Ready判定
aim: PBI が開発着手可能な状態かを判定する
phase: spec
job:
  - 妥当性評価結果をもとに Ready / Not Ready を判定する
rule:
  - 概要・スコープ・受入基準がすべて OK でなければ Ready にしない
link:
  up:
    - 記載内容妥当性評価
  down:
    - ストーリーポイント算出
core: true
io:
  in:
    - 各項目の評価結果
  run:
    - 評価結果を総合して判定する
  out:
    - Ready判定結果
executor:
  type: ai_agent
  reason: 複数評価結果の統合判断が必要なため
```

`core: true` はそのプロセスのゴール達成に直接必要な unit であることを示します。`link.up/down` はデータの依存関係ではなく実行順序を表します。

## インストール

Python 3.9 以上が必要です。

```sh
git clone https://github.com/y-hirakawa/BizSpec.git
cd BizSpec
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

PATH が通っていない場合は環境に合わせて設定する：

```sh
# macOS system Python 3.9
export PATH="$PATH:/Users/<your-username>/Library/Python/3.9/bin"

# pyenv の場合
pyenv rehash
```

## CLI の使い方

```sh
# Claude Code スキルをインストール（対話形式: ローカル or グローバルを選択）
bizspec init

bizspec validate                    # 全プロセスを検証
bizspec validate issue-refinement   # 特定プロセスのみ検証

bizspec list                        # 全 unit を一覧表示
bizspec list issue-refinement       # 特定プロセスの unit を一覧表示

bizspec viz                         # 全プロセスの HTML 図を生成
                                    # bizspec/_viz/index.html（統合ビュー）も生成
bizspec viz issue-refinement        # 特定プロセスの HTML 図を生成
```

`index.html` は全プロセスを俯瞰カードで一覧表示し、クリックで各プロセスのフロー図に遷移できます。ノードをクリックすると接続する矢印がハイライトされます。

## ディレクトリ構成

```
bizspec/
  <プロセス名>/          # プロセスごとにフォルダを切る
    <unit名>.yaml       # unit ごとに 1 ファイル
  _viz/                 # 生成された HTML 図（bizspec viz の出力先）
    index.html          # 全プロセス統合ビュー
src/bizspec/skills/     # パッケージ同梱スキル（bizspec init のコピー元）
  bizspec-refine/
  bizspec-run/
  bizspec-refactor/
.claude/skills/         # Claude Code で使用するスキル
  bizspec-refine/       # プロセスを unit に分解する Claude Code スキル
  bizspec-run/          # プロセスを unit 単位で実行する Claude Code スキル
  bizspec-refactor/     # 複数プロセスを横断してリファクタリング提案を行う Claude Code スキル
docs/
  cli.md                # CLI・スキルリファレンス
```
