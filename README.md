# BizSpec

> **Work in progress.** This project is at an early, experimental stage. APIs and file formats may change.

A tool for decomposing business processes into small, executable units (BizSpec YAML), using Claude Code skills and a CLI together. Each unit describes what to do, who executes it (script / AI agent / human), and how it connects to other units. The goal is to make implicit workflows explicit enough that an AI agent or script can run them without ambiguity.

## What it does

- **Install skills** — Install Claude Code skills into `.claude/skills/` with an interactive prompt (`bizspec init`)
- **Decompose** — Break a business process into minimum units using the `/bizspec-refine` Claude Code skill
- **Refactor** — Analyze processes cross-process and propose refactoring with the `/bizspec-refactor` Claude Code skill
- **Scaffold** — Generate a skeleton YAML for a new unit (`bizspec new`)
- **Search** — Find units by keyword across all processes (`bizspec search`)
- **Validate** — Check BizSpec YAML files for schema errors and link consistency (`bizspec validate`)
- **List** — Show a unit summary table for a process (`bizspec list`)
- **Rename** — Rename a unit and update all `link.up/down` references in one shot (`bizspec rename`)
- **Remove** — Delete a unit and remove all references, with flow-break detection (`bizspec rm`)
- **Renumber** — Rename unit files with execution-order prefixes based on topological sort (`bizspec renumber`)
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
  type: ai_agent        # script / ai_agent / manual — target executor (design intent)
  reason: Requires synthesis of multiple evaluation results
# optional fields
depends_on:             # cross-process dependencies
  - other-process:UnitName  # format: process-name:unit-name
effort:
  duration: 0.5         # hours per execution (Fibonacci: 0.5/1/2/3/5/8/13/21)
  frequency: 4          # monthly execution count (positive integer)
automation:
  difficulty: medium    # low / medium / high — how hard to automate
  status: manual        # manual / partially-automated / automated — current state
```

`core: true` means the unit is directly required to reach the process goal. `link.up/down` represents execution order, not data dependency.

`executor.type` captures the **design intent** — whether this unit should be run by a script, an AI agent, or a human. `automation.status` captures the **current reality** — whether that intent has been implemented yet. A unit with `executor.type: script` and `automation.status: manual` means "we want to automate this, but haven't done it yet."

`depends_on` lists units in other processes that this unit depends on (optional). The `effort` and `automation` fields are also optional; when present they appear in `bizspec list` columns and the `bizspec viz` detail panel. `duration × frequency` gives monthly cost, which drives the heatmap coloring in `bizspec viz`.

### Field responsibility rubric

Each field has a distinct responsibility. Do not duplicate the same content across fields.

| Field | Responsibility | Do NOT write here |
|-------|---------------|-------------------|
| `aim` | The purpose of this unit in **one sentence** | Steps, constraints, data |
| `job` | **Work instructions** for the executor (person / AI / script) — list of actions | Constraints, judgment criteria |
| `rule` | **Constraints, judgment criteria, guidelines** to follow | Work steps, data |
| `io.in` | **Input data (things)** this unit receives | Actions, constraints |
| `io.run` | **Processing steps from a data perspective** (re-expression of `job` as data flow) | Constraints, judgment criteria |
| `io.out` | **Output data (things)** this unit produces | Actions, constraints |

**Quick disambiguation:**
- "must …" / "if … then …" → `rule`
- "do …" / "perform …" (steps) → `job` (execution view) or `io.run` (data flow view)
- Nouns (document, list, result, flag) → `io.in` / `io.out`

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

# Scaffold a new unit YAML
bizspec new issue-refinement ReadinessCheck
bizspec new issue-refinement ReadinessCheck --executor ai_agent --phase spec --core true

# Search across all processes
bizspec search "Google Drive"
bizspec search "PdM" --field aim job

bizspec validate                    # validate all processes
bizspec validate issue-refinement   # validate one process

bizspec list                        # list all units
bizspec list issue-refinement       # list units in one process

bizspec rename issue-refinement Ready判定 Ready判定v2  # rename unit + update all links
bizspec rm issue-refinement Ready判定               # delete unit + remove all references
bizspec rm issue-refinement Ready判定 --force       # skip flow-break warning

bizspec renumber issue-refinement           # rename unit files with execution-order prefixes
bizspec renumber issue-refinement --dry-run # preview only

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
  bizspec-refactor/
.claude/skills/         # skills installed for use in Claude Code
  bizspec-refine/
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
- **リファクタリング** — `/bizspec-refactor` スキル（Claude Code）を使って複数プロセスを横断分析し、リファクタリング提案を行う
- **スケルトン生成** — 新規 unit のスケルトン YAML を生成する（`bizspec new`）
- **検索** — 全プロセス横断でキーワード検索する（`bizspec search`）
- **検証** — BizSpec YAML のスキーマエラーや link の整合性チェック（`bizspec validate`）
- **一覧表示** — プロセスの unit 一覧をテーブル表示（`bizspec list`）
- **リネーム** — unit 名を変更し、同プロセス内の `link.up/down` 参照を一括更新する（`bizspec rename`）
- **削除** — unit を削除し、参照エントリを一括削除する。フロー分断を事前検知（`bizspec rm`）
- **採番リネーム** — unit ファイルをトポロジカル順で採番リネームし、ディレクトリ表示を実行順に揃える（`bizspec renumber`）
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
  type: ai_agent        # script / ai_agent / manual — あるべき実行主体（設計意図）
  reason: 複数評価結果の統合判断が必要なため
# オプションフィールド
depends_on:             # 他プロセスの unit への依存（省略可）
  - other-process:UnitName  # 形式: プロセス名:unit名
effort:
  duration: 0.5         # 1回あたりの所要時間（フィボナッチ数列: 0.5/1/2/3/5/8/13/21）
  frequency: 4          # 月間実行回数（1以上の整数）
automation:
  difficulty: medium    # low / medium / high — 自動化の難易度
  status: manual        # manual / partially-automated / automated — 現在の対応状況
```

`core: true` はそのプロセスのゴール達成に直接必要な unit であることを示します。`link.up/down` はデータの依存関係ではなく実行順序を表します。

`executor.type` は**設計意図**を表します（スクリプト化できる / AI で自動化できる / 手動でないと無理）。`automation.status` は**現在の対応状況**を表します。`executor.type: script` かつ `automation.status: manual` は「スクリプト化したいが、まだ対応していない」を意味します。

`depends_on` は他プロセスの unit への依存を記述します（省略可）。`effort` / `automation` も省略可能なオプションフィールドで、設定すると `bizspec list` の列と `bizspec viz` の詳細パネルに表示されます。`duration × frequency` で月間コストを算出し、`bizspec viz` のヒートマップ色分けに反映されます。

### フィールド責務ルーブリック

各フィールドには明確な責務があります。同じ内容を複数のフィールドに重複させないでください。

| フィールド | 責務 | ここには書かない |
|-----------|------|----------------|
| `aim` | この unit が達成する目的を **1文で** | 手順・制約・データ |
| `job` | 実行主体（人 / AI / スクリプト）への **作業指示**（アクションの羅列） | 制約・判断基準 |
| `rule` | 守るべき **制約・判断基準・ガイドライン** | 作業手順・データ |
| `io.in` | この unit が受け取る **入力データ（モノ）** | アクション・制約 |
| `io.run` | データ視点での **処理ステップ**（`job` をデータの流れとして言い換えたもの） | 制約・判断基準 |
| `io.out` | この unit が渡す **出力データ（モノ）** | アクション・制約 |

**迷ったときの判別:**
- 「〇〇しなければならない / 〇〇の場合は…」→ `rule`
- 「〇〇する / 〇〇を行う」という作業手順 → `job`（実行視点）または `io.run`（データ視点）
- 名詞（ドキュメント・リスト・結果・フラグ）→ `io.in` / `io.out`

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

# 新規 unit のスケルトン YAML を生成
bizspec new issue-refinement Ready判定
bizspec new issue-refinement Ready判定 --executor ai_agent --phase spec --core true

# 全プロセス横断でキーワード検索
bizspec search "Google Drive"
bizspec search "PdM" --field aim job

bizspec validate                    # 全プロセスを検証
bizspec validate issue-refinement   # 特定プロセスのみ検証

bizspec list                        # 全 unit を一覧表示
bizspec list issue-refinement       # 特定プロセスの unit を一覧表示

bizspec rename issue-refinement Ready判定 Ready判定v2  # unit リネーム + link 参照一括更新
bizspec rm issue-refinement Ready判定               # unit 削除 + 参照一括削除
bizspec rm issue-refinement Ready判定 --force       # フロー分断警告を無視して削除

bizspec renumber issue-refinement           # unit ファイルを実行順に採番リネーム
bizspec renumber issue-refinement --dry-run # 変更内容のプレビューのみ

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
  bizspec-refactor/
.claude/skills/         # Claude Code で使用するスキル
  bizspec-refine/       # プロセスを unit に分解する Claude Code スキル
  bizspec-refactor/     # 複数プロセスを横断してリファクタリング提案を行う Claude Code スキル
docs/
  cli.md                # CLI・スキルリファレンス
```
