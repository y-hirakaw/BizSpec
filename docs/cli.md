# bizspec CLI

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
