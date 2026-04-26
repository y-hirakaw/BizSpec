---
name: bizspec-run
description: BizSpec プロセスを unit 単位で順に実行する。全プロセスまたは指定プロセスを対象にできる。
argument-hint: [プロセス名（省略時は全プロセス）]
disable-model-invocation: true
---

## あなたの役割

`bizspec/<プロセス名>/` の unit を実行順（トポロジカル順）に沿って 1 つずつ実行する。
実行の記録はファイルに残し、後から参照・再開できるようにする。

## 実行ディレクトリ

実行開始時に以下のディレクトリを作成する。

```
bizspec/_run/<YYYYMMDD-HHMMSS>/<プロセス名>/
  state.json          # 全 unit のステータスと出力
  <unit名>.out.md     # unit ごとの出力内容（ai_agent / manual のみ）
```

`<YYYYMMDD-HHMMSS>` は実行開始時刻（例: `20260426-153042`）。

### state.json の構造

```json
{
  "process": "issue-refinement",
  "run_dir": "bizspec/_run/20260426-153042/issue-refinement",
  "started_at": "2026-04-26T15:30:42",
  "status": "running",
  "units": {
    "PBI情報取得": {
      "status": "done",
      "output": "PBI データ（JSON）: { ... }"
    },
    "記載内容妥当性評価": {
      "status": "running"
    },
    "Ready判定": {
      "status": "pending"
    }
  }
}
```

`status` の値:

| 値 | 意味 |
|----|------|
| `pending` | 未実行 |
| `running` | 実行中 |
| `done` | 完了（出力あり） |
| `failed` | エラーで停止 |
| `skipped` | `link.up` の unit が `failed` のため実行不可 |

## 実行手順

### 1. 準備

1. 引数からプロセス名を取得する。省略時は `bizspec/` 以下の全プロセスを順に処理する
2. `bizspec/<プロセス名>/` の YAML を読み込み、`link.up/down` からトポロジカル順を計算する
3. 実行ディレクトリを作成し、全 unit を `pending` で `state.json` を初期化する
4. 最初の unit の `io.in` に必要な初期入力をユーザーに確認する（例: 「PBI番号を教えてください」）

### 2. unit の実行ループ

トポロジカル順に unit を処理する。`link.up` の unit が全て `done` になってから次の unit に進む。

各 unit の処理は `executor.type` によって以下のように分岐する。

#### `script`

1. `state.json` の該当 unit を `running` に更新する
2. `io.run` のコマンドを Bash で実行する（前 unit の出力を変数として渡す）
3. 標準出力を `io.out` の期待値と照合し、出力内容を `state.json` に記録する
4. 成功なら `done`、失敗なら `failed` に更新して停止する

#### `ai_agent`

1. `state.json` の該当 unit を `running` に更新する
2. 以下の情報を入力として処理を実行する：
   - `aim` / `job` / `rule`
   - `io.in`（前 unit の `state.json` の出力から解決する）
   - `io.run`（実行手順）
3. 処理結果（`io.out` に対応するもの）を `<unit名>.out.md` に書き出す
4. `state.json` に出力の要約を記録し `done` に更新する

#### `manual`

1. `state.json` の該当 unit を `running` に更新する
2. ユーザーに以下を表示して作業を促す：
   ```
   ── 手動作業が必要です ───────────────────
   unit  : <unit名>
   aim   : <aim>
   入力  : <前 unit の出力から解決した io.in>
   作業  : <job の各項目>
   ルール: <rule の各項目>
   出力  : <io.out に期待されるもの>
   ─────────────────────────────────────────
   作業が完了したら出力内容を教えてください。
   ```
3. ユーザーの回答を `<unit名>.out.md` と `state.json` に記録し `done` に更新する

### 3. 完了報告

全 unit の処理が終わったら結果を表示する：

```
── 実行完了 ──────────────────────────────
プロセス : issue-refinement
実行記録 : bizspec/_run/20260426-153042/issue-refinement/
─────────────────────────────────────────
✓ done     PBI情報取得
✓ done     記載内容妥当性評価
✓ done     Ready判定
...
```

`failed` や `skipped` がある場合はその旨と原因を合わせて表示する。

## unit 間のデータ受け渡し

前 unit の出力は `state.json` の `units.<unit名>.output` から取得する。
`io.in` の各項目と前 unit の `io.out` の対応は名称の類似性で判断する。
対応が取れない場合はユーザーに入力を求める。

## エラー時の方針

- `script` が非ゼロで終了した場合: `failed` に記録して実行を停止し、原因と `state.json` のパスを報告する
- `ai_agent` の処理で出力が `io.out` の期待と大きく異なる場合: ユーザーに確認してから `done` / `failed` を選ぶ
- ユーザーが `manual` 作業をスキップしたい場合: `skipped` として記録し、依存する後続 unit も `skipped` にする

## 注意事項

- `core: false` の unit も通常通り実行する（スキップしない）
- 分岐（1 unit に複数の `link.down`）がある場合、分岐先を並列扱いせず出現順に順次実行する
- `bizspec/_run/` ディレクトリは `.gitignore` に追加することを推奨する（実行ログはリポジトリに含めないため）
