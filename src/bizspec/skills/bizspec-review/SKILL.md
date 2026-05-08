---
name: bizspec-review
description: BizSpec YAML を読んで「意味的に妥当か」をレビューし、Markdown レポートで指摘する。スキーマ検証では拾えない責務混線・粒度・core 妥当性などを人間に代わって読み解く。
argument-hint: [プロセス名（省略時は対話で選択）]
disable-model-invocation: true
---

## あなたの役割

`bizspec/` 配下の BizSpec YAML を読み、**意味的な妥当性**をレビューする。
スキーマ検証（`bizspec validate`）が拾うのは構造の正しさだけ。このスキルは、
人間が「全部読んでレビューする」負荷を肩代わりし、Markdown レポートで指摘を返す。

**他スキルとの役割分担:**
- `/bizspec-refine` = **書く**（プロセスを unit へ分解して YAML を生成・更新）
- `/bizspec-refactor` = **直す**（横断リファクタリング提案を YAML に適用）
- `/bizspec-review` = **読む**（意味整合をレビューしてレポート、修正は提案のみ）

このスキルは **YAML を書き換えない**。修正が必要な指摘は `/bizspec-refine` への引き継ぎを促す。

## 起動時の質問

引数でプロセス名が与えられていればその1つを対象にする。引数がなければ以下を聞く。

```
対象プロセスを選んでください:
  [1] issue-refinement  (9 units, 要レビュー: 2)
  [2] pr-review         (4 units, 要レビュー: 0)
  [a] すべて
番号を入力（複数可: 1 2）:
```

「要レビュー」件数は `bizspec viz` の Review フィルタと同じ判定基準で算出する：
- `status` が `draft` または `review`
- `core` が `undetermined`
- `executor.reason` が空

## データ取得

対象が決まったら以下の順で読む。

1. `bizspec list <プロセス名>` で構造サマリーを把握する
2. 対象プロセスの全 YAML ファイルを Read する（横断レビューでは複数プロセス）

## レビュー観点（7軸）

スキーマ検証が拾わない**意味的な指摘**だけを書く。スキーマ違反は `bizspec validate` の責務。

### 1. 責務混線（フィールドルーブリック違反）
各フィールドの責務に反する内容が混じっていないか。

**検出パターン:**
- `aim` が制約条件を含む（「〜以内に」「〜の場合のみ」）
- `rule` が手順を書いている（「〜する」「〜を行う」）
- `io.process` が動詞句でなくツール名・名詞だけになっている
- `io.in` / `io.out` がアクションや制約になっている
- 同じ内容が `aim` と `rule` の両方に書かれている

**指摘の形:**
> rule に「PR を作成する」という手順が含まれています。これは `io.process` 側に移し、rule は判断基準（例: 「テストが通っていない場合は作成しない」）に絞るべきです。

### 2. core 妥当性
`core` の判定がプロセスゴールから見て妥当か。

**検出パターン:**
- `core: undetermined` のまま放置されている（必ず指摘）
- `core: true` だが `link.down` が空かつゴールへの貢献が見えない
- `core: false` だが `aim` がゴールに直接寄与している

**指摘の形:**
> core が `undetermined` のままです。プロセスゴール「<ゴール>」の達成にこの unit が必須かを確認してください。

### 3. 粒度
1 unit が複数の独立した目的を持っていないか、または分割が細かすぎないか。

**検出パターン:**
- `aim` が「〜と〜」「〜および〜」と複数目的を含む
- `io.process` のステップ数が極端に多い（5 を超える）
- 隣接 unit と executor.type も io も同じで、`aim` が連続した手続きになっている

**指摘の形:**
> aim に「分析と通知」が同居しています。executor が異なる可能性があるため、unit を 2 つに分けることを検討してください。

### 4. executor の根拠
`executor.type` と `reason` が整合しているか。

**検出パターン:**
- `reason` が空（必ず指摘）
- `reason` が「〜だから」だけで具体的根拠がない
- `executor.type: ai_agent` だが reason が「定型処理」と書いてある（script 候補）
- `executor.type: manual` だが reason が「自動化したいが時間がない」など、技術的根拠でなく運用都合

**指摘の形:**
> executor は ai_agent ですが reason が「定型処理」となっており、script で代替できる可能性があります。判断・推論が必要な箇所を reason に明記するか、script への変更を検討してください。

### 5. ライフサイクル
`status` が確定的でない unit。

**検出パターン:**
- `status: draft` — 記入未完了の可能性
- `status: review` — レビュー待ち（このスキル自身がトリガ）
- `status: deprecated` で `deprecated_reason` が空

### 6. 命名
`unit` 名が動詞+目的語になっていない、または何をするか分からない名前。

**検出パターン:**
- 名詞のみ（例: 「PR」「テスト結果」）
- 略称・記号のみ（例: 「P1」「step-2」）

### 7. 入出力の整合
unit 単体内、および隣接 unit との間で in/out が辻褄が合っているか。

**検出パターン:**
- `io.out` が空なのに `link.down` がある
- 上流 unit の `io.out` と下流 unit の `io.in` が完全に乖離している
- `io.process` の動詞が `io.in` のデータをどう変換するかを示せていない

## 重大度の付与

各指摘に重大度を付ける。

| 記号 | 重大度 | 該当例 |
|---|---|---|
| 🔴 | Critical | core: undetermined / executor.reason 空 / 必須フィールドが空 |
| 🟡 | Major | 責務混線・粒度問題・core 妥当性疑義 |
| 🟢 | Minor | 命名・status: review 待ち |

## 出力フォーマット（Markdown レポート）

レポートは**チャットへインライン出力**する（ファイル保存はしない）。

```markdown
## Review Report — <プロセス名>

**対象:** N units  ·  **指摘:** 🔴M  🟡K  🟢L

---

### ⚠ <unit名> — `bizspec/<process>/<unit>.yaml`

`status: draft` · `core: undetermined` · `executor: manual`

- 🔴 **[core 妥当性]** core が undetermined のままです
  - プロセスゴール「<ゴール>」に対し、この unit が必須かを確認してください
  - 提案: ガバナンス目的なら `core: false`、ゴール直結なら `core: true`

- 🟡 **[責務混線]** rule に手順が含まれます
  - 「PRを作成する」は `io.process` 側に移すべき
  - 提案: rule は「テストが通っていない場合は作成しない」など制約に絞る

---

### ✓ <unit名>
指摘なし。

---

## サマリ

- 修正優先度の高いもの: <unit名> (🔴2件)
- `/bizspec-refine` で修正したい unit があれば指示してください
```

**サマリ末尾の案内文**（指摘が1件以上ある場合のみ）:

```
── 次のアクション ──
修正したい unit を選んでください（例: 「<unit名> を直して」）。
/bizspec-refine に引き継いで具体的な YAML 修正を行います。
```

## 進め方

1. 起動時の質問に答えてもらい対象プロセスを確定する
2. `bizspec list` で構造サマリー、続いて対象 YAML を Read
3. 各 unit に対して 7 軸で評価し、指摘を集める
4. Markdown レポートを出力する
5. ユーザーが特定の unit の修正を希望したら `/bizspec-refine` の利用を案内する（このスキル自身は YAML を書き換えない）

## やらないこと

- **YAML の書き換え**は行わない（修正は `/bizspec-refine` の責務）
- スキーマ検証で拾える指摘（必須フィールド欠落・型不正など）はレポートに含めない（`bizspec validate` の責務）
- 提案を勝手に適用しない。あくまで「読み手としての指摘」にとどめる
