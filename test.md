# 実装方針：決済フロー

ここでは、複雑なバリデーションロジックを扱います。

<!-- フロー図の部分だけHTML/SVGでリッチに記述 -->
<div align="center">
  <svg width="200" height="100">
    <rect x="10" y="10" width="180" height="80" fill="lightblue" stroke="black" />
    <text x="100" y="55" font-family="Arial" font-size="14" text-anchor="middle">注文バリデーション</text>
  </svg>
</div>

<details>
<summary>詳細なバリデーションルールを表示</summary>

1. 在庫チェック
2. ユーザー与信チェック
3. クーポン有効性

</details>
