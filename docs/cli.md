# bizspec リファレンス

## インストール

```sh
git clone https://github.com/y-hirakaw/BizSpec.git
cd BizSpec
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

インストール後、`bizspec` コマンドのパスを通す（`~/.zshrc` 等に追記）。

```sh
# macOS (Python 3.9)
export PATH="$PATH:/Users/<your-username>/Library/Python/3.9/bin"
```

## コマンドリファレンス

### `bizspec validate [process]`

`bizspec/` 以下の BizSpec YAML を検証する。

```sh
bizspec validate                    # 全プロセスを検証
bizspec validate issue-refinement   # 特定プロセスのみ検証
```

**チェック内容:**
- 必須フィールドの存在（unit / aim / phase / job / rule / link / core / io / executor）
- `core` が `true` / `false` であること
- `executor.type` が `script` / `ai_agent` / `manual` のいずれかであること
- `link.up/down` の参照先ファイルが存在すること
- `link.up/down` の双方向整合性

**終了コード:** `0` = OK、`1` = エラーあり

### `bizspec list [process]`

`bizspec/` 以下の unit 一覧を表示する。

```sh
bizspec list                    # 全プロセスを表示
bizspec list issue-refinement   # 特定プロセスのみ表示
```

unit名・core・executor.type をプロセスごとに一覧表示する。

### `bizspec viz [process]`

`bizspec/` 以下の unit から HTML フロー図を生成し、`bizspec/_viz/<プロセス名>.html` に出力する。

```sh
bizspec viz                    # 全プロセスを出力
bizspec viz issue-refinement   # 特定プロセスのみ出力
```

**出力内容:**
- 左ペイン: `link.up/down` をもとにした DAG フロー図（ノードをクリックで詳細表示）
- 右ペイン: unit の詳細（aim / job / rule / io / executor / link）
- ノード色: `core: true` = 青、`core: false` = グレー
- バッジ: `executor.type`（script / ai_agent / manual）

**終了コード:** `0` = OK、`1` = エラーあり

---

## Claude Code スキル

Claude Code（`claude` CLI またはデスクトップアプリ）上で `/` コマンドとして呼び出す。

### `/bizspec-refine [プロセスの説明]`

業務プロセスを BizSpec YAML（最小 unit）へ分解する。新規プロセスの作成と、既存プロセスへの unit 追加の両方に使う。

```
/bizspec-refine PBI のリファインメントプロセスを分解したい
/bizspec-refine issue-refinement に通知ステップを追加したい
```

**動作:**
1. プロセスゴールと IPO を確認する（不明点は最大 2 問まで質問）
2. unit に分解して YAML を提示する
3. `core: undetermined` の unit についてユーザーに確認する
4. `bizspec/<プロセス名>/<unit名>.yaml` に保存する
5. `bizspec validate` で検証し、結果を報告する

### `/bizspec-run [プロセス名]`

BizSpec プロセスを unit 単位でトポロジカル順に実行する。

```
/bizspec-run                    # 全プロセスを実行
/bizspec-run issue-refinement   # 特定プロセスのみ実行
```

**executor.type ごとの動作:**

| type | 動作 |
|------|------|
| `script` | `io.run` のコマンドを Bash で実行する |
| `ai_agent` | Claude が `job` / `rule` / `io` に従って処理を実行する |
| `manual` | 作業内容を表示してユーザーの完了報告を待つ |

**実行記録の出力先:**

```
bizspec/_run/<YYYYMMDD-HHMMSS>/<プロセス名>/
  state.json          # 全 unit のステータス（pending / running / done / failed / skipped）と出力
  <unit名>.out.md     # ai_agent / manual の出力内容
```

実行のたびに新しいディレクトリが作られるため、過去の実行記録は上書きされない。`bizspec/_run/` はリポジトリに含めない（`.gitignore` 済み）。
