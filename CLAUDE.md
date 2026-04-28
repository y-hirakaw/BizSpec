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
src/bizspec/skills/             # パッケージ同梱スキル（bizspec init でコピー元になる）
  bizspec-refine/SKILL.md
  bizspec-refactor/SKILL.md
BizSpec_要求仕様.md              # 要件定義書
```

Skills のコマンド名は `bizspec-` prefix で統一（CLI の `bizspec xxxx` と揃える）。

## CLI コマンド

| コマンド | 概要 |
|---------|------|
| `bizspec init` | Claude Code スキルをインタラクティブに `.claude/skills/` へインストールする（ローカル / グローバル選択） |
| `bizspec new <process> <unit>` | unit のスケルトン YAML を生成する（`--executor` / `--phase` / `--core` / `--up` / `--down`） |
| `bizspec search <keyword>` | 全プロセス横断でキーワード検索する（`--field` で対象フィールドを絞れる） |
| `bizspec list` | `bizspec/` 内の unit 一覧を表示（unit名・core・executor.type、effort/automationフィールドがあれば列追加） |
| `bizspec validate` | BizSpec YAML のスキーマ検証 |
| `bizspec viz` | `link.up/down` を元にフロー図を生成する。引数なし時は全プロセス統合ビュー（`index.html`）も生成 |

## BizSpec YAML データ構造 (v1)

プロジェクトの中核となるデータ形式：

```yaml
unit: 〇〇判定
aim: 目的
phase: spec | dev | test | release  # 自由記述。フォルダではなくフィールドで管理
job: [具体的な作業内容]
rule: [制約・判断基準]
link:
  up: [実行順序として前に来る unit]   # データ依存ではなく実行順序
  down: [実行順序として後に来る unit]
core: true | false | undetermined
io:
  in: [入力データ]
  run: [実行手順]
  out: [出力データ]
executor:
  type: script | ai_agent | manual
  reason: なぜその主体を選んだかの根拠
depends_on:              # 他プロセスの unit への依存（省略可）
  - other-process:UnitName  # 形式: プロセス名:unit名
# オプションフィールド（省略可）
effort:
  duration: 0.5           # 1回あたりの所要時間（時間単位、フィボナッチ数列: 0.5/1/2/3/5/8/13/21）
  frequency: 4            # 月間実行回数（1以上の整数）
automation:
  difficulty: low | medium | high
  status: manual | partially-automated | automated
```

`core: undetermined` はユーザー確認が必要な場合に使用。`phase` は自由記述でフォルダ分けではなくフィールドで管理する。`depends_on` は他プロセスの unit への依存を `プロセス名:unit名` 形式で記述する（省略可）。`effort` / `automation` は省略可能なオプションフィールド。存在する場合は `bizspec list` の列と `bizspec viz` の詳細パネルに表示される。`effort.duration × effort.frequency` で月間コストを算出し、`bizspec viz` のヒートマップ（低/中/高）に反映される。

## 開発環境

- **Python:** macOS 標準搭載の Python 3.9 を対象とする（3.9 で動く構文・APIに限定）
- **依存インストール:** `python3 -m pip install -e ".[dev]"`
- **テスト実行:** `python3 -m pytest tests/ -v`（または `uv run --with pytest pytest tests/ -v`）
- **動作確認:** `bizspec validate`（PATH が通っていること）
- **CI:** GitHub Actions（`.github/workflows/test.yml`）— main への push と PR で自動テスト

## Skills の設計方針

- **分解の基準:** IPO（Input-Process-Output）ベースで `unit`（最小単位）へ再帰的分解
- **executor の判断基準:**
  - 入出力が定型的（API、正規表現）→ `script`
  - 推論・自然言語解析・状況判断が必要 → `ai_agent`
  - 判断がつかない → `manual`（理由必記）
- **Human-in-the-loop 重視:** AIが `core` 判定に迷う場合は独断せずユーザーに問いかける
- **過剰な作り込みを避ける:** AI と人間の協調を優先し、最小限の仕様から始める
