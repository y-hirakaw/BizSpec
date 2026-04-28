# bizspec リファレンス

## インストール

```sh
git clone https://github.com/y-hirakaw/BizSpec.git
cd BizSpec
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

インストール後、`bizspec` コマンドのパスを通す（`~/.zshrc` 等に追記）。環境によって設定方法が異なる。

```sh
# macOS system Python 3.9 の場合
export PATH="$PATH:/Users/<your-username>/Library/Python/3.9/bin"

# pyenv の場合
pyenv rehash
```

## コマンドリファレンス

### `bizspec init`

Claude Code スキルを `.claude/skills/` にインストールする。実行すると対話形式でインストール先を選択できる。

```sh
bizspec init
```

```
スキルのインストール先を選択してください:
  [1] ローカル（このプロジェクトの .claude/skills/）
  [2] グローバル（~/.claude/skills/）
選択 [1]:
```

- そのままエンター（または `1`）→ カレントディレクトリの `.claude/skills/` にインストール
- `2` → `~/.claude/skills/` にインストール（全プロジェクトで使用可能）

インストールされるスキル: `/bizspec-refine`、`/bizspec-refactor`

### `bizspec new <process> <unit-name>`

`bizspec/<process>/` に unit のスケルトン YAML を生成する。

```sh
bizspec new issue-refinement Ready判定
bizspec new issue-refinement Ready判定 --executor ai_agent --phase spec --core true
bizspec new issue-refinement Ready判定 --up 記載内容妥当性評価 --down ストーリーポイント算出
```

**オプション:**

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--executor` | `script` / `ai_agent` / `manual` | `manual` |
| `--phase` | フェーズ名 | `TODO` |
| `--core` | `true` / `false` | `false` |
| `--up UNIT ...` | `link.up` に追加する unit 名（複数可） | なし |
| `--down UNIT ...` | `link.down` に追加する unit 名（複数可） | なし |
| `--force` | 既存ファイルを上書きする | false |

プロセスディレクトリが存在しない場合は自動作成される。生成後は `bizspec validate` で検証し、`TODO` 箇所を埋める。

### `bizspec search <keyword>`

全プロセス横断でキーワードを検索する。

```sh
bizspec search "Google Drive"
bizspec search "PdM" --field aim job
bizspec search "ai_agent" --field executor
bizspec search "API" --field executor
```

**オプション:**

| オプション | 説明 |
|-----------|------|
| `--field FIELD ...` | 検索対象フィールドを絞る（`unit` / `aim` / `job` / `rule` / `io` / `executor`）。省略時は全フィールドを対象 |

マッチした unit のプロセス名・unit 名・ヒットしたフィールドと内容を一覧表示する。ヒットが0件の場合は終了コード 1。

**終了コード:** `0` = 1件以上ヒット、`1` = ヒットなし or エラー

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
- `effort.duration`（設定時）がフィボナッチ数列（0.5 / 1 / 2 / 3 / 5 / 8 / 13 / 21）のいずれかであること
- `effort.frequency`（設定時）が 1 以上の整数（月間実行回数）であること
- `automation.difficulty`（設定時）が `low` / `medium` / `high` のいずれかであること
- `automation.status`（設定時）が `manual` / `partially-automated` / `automated` のいずれかであること

**終了コード:** `0` = OK、`1` = エラーあり

### `bizspec list [process]`

`bizspec/` 以下の unit 一覧を表示する。

```sh
bizspec list                    # 全プロセスを表示
bizspec list issue-refinement   # 特定プロセスのみ表示
```

unit名・core・executor.type をプロセスごとに一覧表示する。いずれかの unit に `effort.duration` / `effort.frequency` / `automation.difficulty` が設定されている場合は、対応する列が自動的に追加される。

### `bizspec viz [process]`

`bizspec/` 以下の unit から HTML フロー図を生成する。

```sh
bizspec viz                    # 全プロセスを出力（index.html も生成）
bizspec viz issue-refinement   # 特定プロセスのみ出力
```

**引数なし（全プロセス）の出力:**

| ファイル | 内容 |
|---------|------|
| `bizspec/_viz/index.html` | 全プロセス統合ビュー |
| `bizspec/_viz/<プロセス名>.html` | プロセスごとの個別フロー図 |

**`index.html` の構成:**
- サイドバー: プロセス一覧（unit数バッジ付き）
- デフォルト表示: 全プロセスの俯瞰カード（unit数・phase・executor内訳・core率）
- カードをクリック: そのプロセスのフロー図 + unit 詳細パネルに切り替わる
- 「← 一覧」ボタンで俯瞰に戻る

**フロー図の共通機能:**
- 左ペイン: `link.up/down` をもとにした DAG フロー図
- 右ペイン: unit の詳細（aim / job / rule / io / executor / effort・automation（設定時）/ link）
- ノードをクリックすると詳細表示 + 接続する矢印がハイライト（青）、無関係な矢印はフェード
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

### `/bizspec-refactor`

複数の BizSpec プロセスを横断してリファクタリング提案を行う。引数なしで起動し、対話形式で対象プロセスと観点を設定する。

```
/bizspec-refactor
```

**起動後の質問:**

1. **対象プロセスの選択** — `bizspec/` 以下のプロセスを番号で選択（複数可、`a` で全選択）
2. **リファクタリングの観点**（省略可）— 例: `manual を減らしたい` / `AI 化できる unit を探したい`

**分析の7軸:**

| 軸 | 内容 |
|----|------|
| 重複（横断） | 複数プロセスにまたがって aim や job が意味的に近い unit を検出 |
| 不要候補 | ゴール達成への貢献が薄い unit を検出（core: false / 末端ノード / manual など） |
| 統合候補 | 同一プロセス内で分割しすぎている隣接 unit を検出 |
| 順序最適化 | 直列になっているが実は並列実行できる unit を検出 |
| Dead End | フロー途中に後続がなく、ゴールに繋がっていない孤立末端 unit を検出 |
| Serial Bottleneck | 多数の上流が1 unit に集中しており流れを絞り込んでいる箇所を検出 |
| Context Fragmentation | 同一文脈の処理が不必要に複数 unit に断片化されている箇所を検出 |

**提案の適用:**
- **順序最適化 / 不要候補の削除 / 統合マージ**: ユーザー確認後に YAML を直接更新
- **重複の統合**: 複数プロセス横断の構造変更は提案のみ。適用後に `/bizspec-refine` の利用を案内
