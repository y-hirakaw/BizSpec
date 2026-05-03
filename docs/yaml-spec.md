# BizSpec YAML schema reference

[日本語](#bizspec-yaml-スキーマリファレンス日本語) | English

## YAML format

Each unit is one YAML file:

```yaml
unit: ReadinessCheck
aim: Determine whether a PBI is ready for development
phase: spec
scope:
  - Ready / Not Ready judgment with documented basis
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
  process:
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
  duration: 0.5         # hours per execution (Fibonacci: 0.25/0.5/1/2/3/5/8/13/21)
  frequency: 4          # monthly execution count (positive integer)
automation:
  difficulty: medium    # low / medium / high — how hard to automate
  status: manual        # manual / partially-automated / automated — current state
status: stable          # draft | review | stable | deprecated — lifecycle state
deprecated_reason: ...  # only when status: deprecated
execution:              # execution coordination hints (optional)
  parallel_with:        # units that can run concurrently with this unit
    - AnotherUnit
```

`core: true` means the unit is directly required to reach the process goal. `link.up/down` represents execution order, not data dependency.

`executor.type` is the **design intent** (script / ai_agent / manual). `automation.status` is the **current reality** — `executor.type: script` with `automation.status: manual` means "planned for automation but not yet done."

`status` is the lifecycle state: `draft` → `review` → `stable` → `deprecated`. Add `deprecated_reason` when deprecating.

The optional fields `depends_on`, `effort`, `automation`, `status`, and `execution.parallel_with` are all omittable. When present, `effort` and `automation` appear in `bizspec list` columns and the `bizspec viz` detail panel. `duration × frequency` drives the heatmap in `bizspec viz`. `execution.parallel_with` is rendered as green dotted edges.

## Field responsibility rubric

Each field has a distinct responsibility. Do not duplicate the same content across fields.

| Field | Responsibility | Do NOT write here |
|-------|---------------|-------------------|
| `aim` | The purpose of this unit in **one sentence** | Steps, constraints, data |
| `scope` | **What this unit is responsible for** — responsibility scope expressed as noun phrases | Step-by-step actions, constraints |
| `rule` | **Constraints, judgment criteria, guidelines** to follow | Work steps, data |
| `io.in` | **Input data (things)** this unit receives | Actions, constraints |
| `io.process` | **Processing steps** from input to output (the P in IPO; verb phrases) | Constraints, judgment criteria |
| `io.out` | **Output data (things)** this unit produces | Actions, constraints |

`scope` and `io.process` differ in abstraction: `scope` describes **what is owned** (noun phrase), `io.process` describes **how the transformation happens** (verb phrase).

**Quick disambiguation:**
- "must …" / "if … then …" → `rule`
- "responsible for …" / "guarantees …" (noun phrase) → `scope`
- "do …" / "perform …" (procedure) → `io.process`
- Nouns (document, list, result, flag) → `io.in` / `io.out`

---

# BizSpec YAML スキーマリファレンス（日本語）

## YAML フォーマット

unit ごとに 1 つの YAML ファイル：

```yaml
unit: Ready判定
aim: PBI が開発着手可能な状態かを判定する
phase: spec
scope:
  - Ready / Not Ready 判定と判定根拠の明示
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
  process:
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
status: stable          # draft | review | stable | deprecated — ライフサイクル状態
deprecated_reason: ...  # status: deprecated のときのみ
execution:              # 実行制御ヒント（省略可）
  parallel_with:        # この unit と並行実行できる unit 名
    - AnotherUnit
```

`core: true` はそのプロセスのゴール達成に直接必要な unit であることを示します。`link.up/down` はデータ依存ではなく実行順序を表します。

`executor.type` は**設計意図**（script / ai_agent / manual）。`automation.status` は**現在の対応状況** — `executor.type: script` かつ `automation.status: manual` は「スクリプト化したいが未対応」を意味します。

`status` はライフサイクル状態：`draft` → `review` → `stable` → `deprecated`。廃止時は `deprecated_reason` で理由を記録できます。

省略可能フィールド（`depends_on` / `effort` / `automation` / `status` / `execution.parallel_with`）はすべて任意です。`effort` / `automation` は `bizspec list` の列と `bizspec viz` の詳細パネルに表示されます。`duration × frequency` で月間コストを算出し viz のヒートマップに反映されます。`execution.parallel_with` は viz で緑の点線エッジとして可視化されます。

## フィールド責務ルーブリック

各フィールドには明確な責務があります。同じ内容を複数のフィールドに重複させないでください。

| フィールド | 責務 | ここには書かない |
|-----------|------|----------------|
| `aim` | この unit が達成する目的を **1文で** | 手順・制約・データ |
| `scope` | この unit が **責任を持つ範囲・成果物**（責務スコープを名詞句で表現） | アクション手順・制約 |
| `rule` | 守るべき **制約・判断基準・ガイドライン** | 作業手順・データ |
| `io.in` | この unit が受け取る **入力データ（モノ）** | アクション・制約 |
| `io.process` | 入力 → 出力への **処理ステップ**（IPO の P。動詞句） | 制約・判断基準 |
| `io.out` | この unit が渡す **出力データ（モノ）** | アクション・制約 |

`scope` と `io.process` は抽象度で分離する：`scope` は **何に責任を持つか**（名詞句）、`io.process` は **どう変換するか**（動詞句）。

**迷ったときの判別:**
- 「〇〇しなければならない / 〇〇の場合は…」→ `rule`
- 「〇〇に責任を持つ / 〇〇を保証する」という名詞句 → `scope`
- 「〇〇する / 〇〇を行う」という手順 → `io.process`
- 名詞（ドキュメント・リスト・結果・フラグ）→ `io.in` / `io.out`
