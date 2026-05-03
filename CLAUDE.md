# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

BizSpec は、既存の業務プロセスを AI-Native 形式にリファクタリングするための設計支援ツール。暗黙的な業務を「最小仕様（BizSpec YAML）」へ分解し、価値提供に必要な作業を抽出する。

詳細な要件は `BizSpec_要求仕様.md` を参照。

## ファイル構成

```
.claude/skills/
  bizspec-refine/SKILL.md       # /bizspec-refine スキル（プロセス分解 → YAML生成・更新）
  bizspec-refactor/SKILL.md     # /bizspec-refactor スキル（横断リファクタリング提案）
bizspec/
  <プロセス名>/                  # プロセスごとにフォルダを切る
    <unit名>.yaml               # unit ごとに1ファイル
  _viz/                         # 生成物（bizspec viz の HTML 出力先）
    index.html                  # 全プロセス統合ビュー（引数なし時のみ生成）
    <プロセス名>.html
src/bizspec/
  core/                         # 共有レイヤー（公開 API は core/__init__.py を参照）
    errors.py                   # VError（検証ダイアグノスティクス）
    loader.py                   # YAML 読込・プロセス走査
    model.py                    # Unit / IO / Link 等の TypedDict
    prompt.py                   # 対話プロンプト（confirm）
  viz/                          # bizspec viz 実装
    layout.py                   # DAG レイアウト（純関数）
    builder.py                  # HTML 組み立て + テンプレ読込
    cmd.py                      # run_viz エントリ
    templates/{process,index}.html  # 外部テンプレ（importlib.resources で読込）
  skills/                       # パッケージ同梱スキル（bizspec init でコピー元になる）
    bizspec-refine/SKILL.md
    bizspec-refactor/SKILL.md
BizSpec_要求仕様.md              # 要件定義書
```

**core 公開 API:** 共有 helper は `from bizspec.core import VError, load_units, Unit, ...` で import する。`bizspec.viz_cmd` は後方互換 shim（中身は `bizspec.viz` に移譲）。

Skills のコマンド名は `bizspec-` prefix で統一（CLI の `bizspec xxxx` と揃える）。

**Skills の正本ルール:** SKILL.md の編集は **必ず `src/bizspec/skills/` 側を正本** として行うこと。`.claude/skills/` 側は `bizspec init` で `src/bizspec/skills/` から **コピーされる出力** であり、`init` 実行時に既存ディレクトリは無警告で `rmtree` される。両方を編集した場合は `src/bizspec/skills/` の内容で上書きされる。CI / リリース前に `diff -r src/bizspec/skills/ .claude/skills/` で同期されていることを確認する。

## CLI コマンド

| コマンド | 概要 |
|---------|------|
| `bizspec init` | Claude Code スキルをインタラクティブに `.claude/skills/` へインストールする（ローカル / グローバル選択） |
| `bizspec new <process> <unit>` | unit のスケルトン YAML を生成する（`--executor` / `--phase` / `--core` / `--up` / `--down`） |
| `bizspec search <keyword>` | 全プロセス横断でキーワード検索する（`--field` で対象フィールドを絞れる、`--format json` で構造化出力） |
| `bizspec list` | `bizspec/` 内の unit 一覧を表示（unit名・core・executor.type、effort/automationフィールドがあれば列追加） |
| `bizspec rename <process> <old> <new>` | unit をリネームし同プロセス内の link 参照を一括更新する（`--dry-run` でプレビュー） |
| `bizspec rm <process> <unit>` | unit を削除し link 参照を一括削除する。フロー分断検知あり（`--force` で強制） |
| `bizspec renumber <process>` | unit ファイルをトポロジカル順に採番リネームする（`--dry-run` でプレビュー） |
| `bizspec validate` | BizSpec YAML のスキーマ検証（`--format json` で CI 連携用構造化出力） |
| `bizspec viz` | `link.up/down` を元にフロー図を生成する。引数なし時は全プロセス統合ビュー（`index.html`）も生成 |

## BizSpec YAML データ構造 (v1)

プロジェクトの中核となるデータ形式：

```yaml
unit: 〇〇判定
aim: 目的
phase: spec | dev | test | release | ops  # 自由記述だが推奨語彙あり
scope: [この unit が責任を持つ範囲・成果物（名詞句）]
rule: [制約・判断基準]
link:
  up: [実行順序として前に来る unit]   # データ依存ではなく実行順序
  down: [実行順序として後に来る unit]
core: true | false | undetermined
io:
  in: [入力データ]
  process: [処理手順（IPO の P。動詞句）]
  out: [出力データ]
executor:
  type: script | ai_agent | manual
  reason: なぜその主体を選んだかの根拠
depends_on:              # 他プロセスの unit への依存（省略可）
  - other-process:UnitName  # 形式: プロセス名:unit名
# オプションフィールド（省略可）
effort:
  duration: 0.5           # 1回あたりの所要時間（時間単位、フィボナッチ数列: 0/0.25/0.5/1/2/3/5/8/13/21）
  frequency: 4            # 月間実行回数（1以上の整数）
automation:
  difficulty: low | medium | high
  status: manual | partially-automated | automated
status: draft | review | stable | deprecated  # ライフサイクル状態（省略可）
deprecated_reason: 廃止理由  # status: deprecated のときのみ（省略可）
execution:                 # 実行制御ヒント（省略可）
  parallel_with:           # 並行実行できる unit 名のリスト
    - AnotherUnit
```

フィールドの補足：
- `core: undetermined` — ユーザー確認が必要な場合に使用
- `phase` — 自由記述。フォルダではなくフィールドで管理。推奨語彙は `spec` / `dev` / `test` / `release` / `ops`（外れた値は `bizspec validate` で warn 表示、エラーにはならない）
- `depends_on` — 他プロセスの unit への依存を `プロセス名:unit名` 形式で記述（省略可）
- `effort` / `automation` / `status` — 省略可。`bizspec list` の列と `bizspec viz` 詳細パネルに表示
- `effort.duration × effort.frequency` — 月間コストを算出し viz ヒートマップに反映
- `status` — viz でノード色分けに使用（draft=黄、review=橙、stable=緑、deprecated=グレー）
- `execution.parallel_with` — 並行実行できる unit 名のリスト（省略可）。viz で緑の点線エッジとして可視化

## 開発環境

- **Python:** 3.9 以上（3.9 で動く構文・API に限定）
- **依存インストール:** `uv pip install -e ".[dev]"`
- **テスト実行:** `uv run --with pytest pytest tests/ -v`
- **動作確認:** `uv run bizspec validate`
- **CI:** GitHub Actions（`.github/workflows/test.yml`）— main への push と PR で自動テスト

## フィールド責務ルーブリック

`scope` / `rule` / `io.process` への書き分け基準：

| フィールド | 責務 | ここには書かない |
|-----------|------|----------------|
| `aim` | この unit が達成する目的を 1 文で | 手順・制約・データ |
| `scope` | この unit が責任を持つ範囲・成果物（名詞句で表現する責務スコープ） | アクション手順・制約 |
| `rule` | 守るべき制約・判断基準・ガイドライン | 作業手順・データ |
| `io.in` | この unit が受け取る入力データ（モノ） | アクション・制約 |
| `io.process` | 入力 → 出力への処理ステップ（IPO の P。動詞句） | 制約・判断基準 |
| `io.out` | この unit が渡す出力データ（モノ） | アクション・制約 |

`scope` と `io.process` は抽象度で分離する：`scope` は **何に責任を持つか**（名詞句）、`io.process` は **どう変換するか**（動詞句）。

## Skills の設計方針

- **分解の基準:** IPO（Input-Process-Output）ベースで `unit`（最小単位）へ再帰的分解
- **executor の判断基準:**
  - 入出力が定型的（API、正規表現）→ `script`
  - 推論・自然言語解析・状況判断が必要 → `ai_agent`
  - 判断がつかない → `manual`（理由必記）
- **Human-in-the-loop 重視:** AIが `core` 判定に迷う場合は独断せずユーザーに問いかける
- **過剰な作り込みを避ける:** AI と人間の協調を優先し、最小限の仕様から始める
