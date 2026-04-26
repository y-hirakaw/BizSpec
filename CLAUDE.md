# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

BizSpec は、既存の業務プロセスを AI-Native 形式にリファクタリングするための設計支援ツール。暗黙的な業務を「最小仕様（BizSpec YAML）」へ分解し、価値提供に必要な作業を抽出する。

詳細な要件は `BizSpec_要求仕様.md` を参照。

## ファイル構成

```
.claude/skills/
  bizspec-refine/SKILL.md       # /bizspec-refine スキル（プロセス分解 → YAML生成・更新）
bizspec/
  <プロセス名>/                  # プロセスごとにフォルダを切る
    <unit名>.yaml               # unit ごとに1ファイル
  _viz/                         # 生成物（bizspec viz の HTML 出力先）
    <プロセス名>.html
BizSpec_要求仕様.md              # 要件定義書
```

Skills のコマンド名は `bizspec-` prefix で統一（CLI の `bizspec xxxx` と揃える）。

## 開発フェーズと優先順位

1. **BizSpec Skills（最優先）** — AIエージェントが業務を「分解・仕様化」するためのプロンプトセット・指示セット
2. **BizSpec CLI** — BizSpec YAML のバリデーションおよび `takt` フォーマットへの変換

### CLI コマンド（予定）

| コマンド | 概要 |
|---------|------|
| `bizspec list` | `bizspec/` 内の unit 一覧を表示（unit名・core・executor.type） |
| `bizspec validate` | BizSpec YAML のスキーマ検証 |
| `bizspec viz` | `link.up/down` を元にフロー図を生成し、unit 詳細を参照できる HTML を `bizspec/_viz/<プロセス名>.html` に出力 |

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
```

`core: undetermined` はユーザー確認が必要な場合に使用。`phase` は自由記述でフォルダ分けではなくフィールドで管理する。

## 開発環境

- **Python:** macOS 標準搭載の Python 3.9 を対象とする（3.9 で動く構文・APIに限定）
- **依存インストール:** `python3 -m pip install -e ".[dev]"`
- **テスト実行:** `python3 -m pytest tests/ -v`
- **動作確認:** `bizspec validate`（PATH が通っていること）

## Skills の設計方針

- **分解の基準:** IPO（Input-Process-Output）ベースで `unit`（最小単位）へ再帰的分解
- **executor の判断基準:**
  - 入出力が定型的（API、正規表現）→ `script`
  - 推論・自然言語解析・状況判断が必要 → `ai_agent`
  - 判断がつかない → `manual`（理由必記）
- **Human-in-the-loop 重視:** AIが `core` 判定に迷う場合は独断せずユーザーに問いかける
- **過剰な作り込みを避ける:** AI と人間の協調を優先し、最小限の仕様から始める
