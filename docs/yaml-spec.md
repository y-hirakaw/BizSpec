# BizSpec YAML schema reference

[日本語](#bizspec-yaml-スキーマリファレンス日本語) | English

## YAML format

Each unit is one YAML file:

```yaml
unit: ReadinessCheck
aim: Determine whether a PBI is ready for development
phase: spec
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
status: stable          # draft | review | stable | deprecated — lifecycle state
# optional fields
effort:
  duration: 0.5         # hours per execution (Fibonacci: 0/0.25/0.5/1/2/3/5/8/13/21)
  frequency: 4          # monthly execution count (positive integer)
automation:
  difficulty: medium    # low / medium / high — how hard to automate
  status: manual        # manual / partially-automated / automated — current state
deprecated_reason: ...  # only when status: deprecated
```

`core: true` means the unit is directly required to reach the process goal. `link.up/down` represents execution order, not data dependency.

`executor.type` is the **design intent** (script / ai_agent / manual). `automation.status` is the **current reality** — `executor.type: script` with `automation.status: manual` means "planned for automation but not yet done."

`status` is the lifecycle state: `draft` → `review` → `stable` → `deprecated`. Add `deprecated_reason` when deprecating.

The optional fields `effort` and `automation` appear in `bizspec list` columns and the `bizspec viz` detail panel. `duration × frequency` drives the heatmap in `bizspec viz`.

## Field responsibility rubric

Each field has a distinct responsibility. Do not duplicate the same content across fields.

| Field | Responsibility | Do NOT write here |
|-------|---------------|-------------------|
| `aim` | The purpose of this unit in **one sentence** | Steps, constraints, data |
| `rule` | **Constraints, judgment criteria, guidelines** to follow | Work steps, data |
| `io.in` | **Input data (things)** this unit receives | Actions, constraints |
| `io.process` | **Processing steps** from input to output (the P in IPO; verb phrases) | Constraints, judgment criteria |
| `io.out` | **Output data (things)** this unit produces | Actions, constraints |

**Quick disambiguation:**
- "must …" / "if … then …" → `rule`
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
status: stable          # draft | review | stable | deprecated — ライフサイクル状態
# オプションフィールド
effort:
  duration: 0.5         # 1回あたりの所要時間（フィボナッチ数列: 0/0.25/0.5/1/2/3/5/8/13/21）
  frequency: 4          # 月間実行回数（1以上の整数）
automation:
  difficulty: medium    # low / medium / high — 自動化の難易度
  status: manual        # manual / partially-automated / automated — 現在の対応状況
deprecated_reason: ...  # status: deprecated のときのみ
```

`core: true` はそのプロセスのゴール達成に直接必要な unit であることを示します。`link.up/down` はデータ依存ではなく実行順序を表します。

`executor.type` は**設計意図**（script / ai_agent / manual）。`automation.status` は**現在の対応状況** — `executor.type: script` かつ `automation.status: manual` は「スクリプト化したいが未対応」を意味します。

`status` はライフサイクル状態：`draft` → `review` → `stable` → `deprecated`。廃止時は `deprecated_reason` で理由を記録できます。

省略可能フィールド（`effort` / `automation`）は `bizspec list` の列と `bizspec viz` の詳細パネルに表示されます。`duration × frequency` で月間コストを算出し viz のヒートマップに反映されます。

## フィールド責務ルーブリック

各フィールドには明確な責務があります。同じ内容を複数のフィールドに重複させないでください。

| フィールド | 責務 | ここには書かない |
|-----------|------|----------------|
| `aim` | この unit が達成する目的を **1文で** | 手順・制約・データ |
| `rule` | 守るべき **制約・判断基準・ガイドライン** | 作業手順・データ |
| `io.in` | この unit が受け取る **入力データ（モノ）** | アクション・制約 |
| `io.process` | 入力 → 出力への **処理ステップ**（IPO の P。動詞句） | 制約・判断基準 |
| `io.out` | この unit が渡す **出力データ（モノ）** | アクション・制約 |

**迷ったときの判別:**
- 「〇〇しなければならない / 〇〇の場合は…」→ `rule`
- 「〇〇する / 〇〇を行う」という手順 → `io.process`
- 名詞（ドキュメント・リスト・結果・フラグ）→ `io.in` / `io.out`
