# Handoff: BizSpec — Engineering Process Console

## Overview

BizSpec は社内の業務プロセスを **process → unit** という階層で構造化し、各 unit に effort / frequency / executor (human / script / ai_agent) / difficulty / automation status などを記録する内部ツールです。記録を貯めることで「どこを自動化すべきか」「どこに人手が集中しているか」を可視化します。

このハンドオフは、Engineering Console (PdM・エンジニア・経営の三者が触る画面群) のデザインリファレンスです。3 つの方向性 (A: Balanced / B: Document / C: Compact Power) を Light / Dark + 専用ビュー (Heatmap, DAG detail) で提示しています。最終的にどれをベースに採用するかはチームで決定する想定です。

## About the Design Files

このバンドル内のファイルは **HTML で作られたデザインリファレンス** です — 見た目と挙動を伝える prototype であって、本番コードではありません。

実装タスクは、このプロトタイプを **対象プロジェクトの環境 (React / Next.js / Vue など) で再現する** ことです。既存のデザインシステム / コンポーネントライブラリがあればそれに合わせ、まだ無ければプロジェクトに最も適したフレームワークを選んで実装してください。HTML を直接コピーするのではなく、その挙動と見た目を target stack のパターンで作り直すイメージです。

## Fidelity

**High-fidelity (hifi)** — 配色 / タイポグラフィ / 余白 / 状態は本番想定の値です。色は hex で固定、フォントは Inter / JetBrains Mono、間隔も明確に決まっています。**ピクセル相当の精度で再現してください**。各画面の「どんなデータが出るか」「どう操作するか」も決まっているのでそのまま実装可能です。

唯一の例外: アイコンは現状ほぼ Unicode 文字 (›, ●, ◇ など) や SVG 直書きで簡易描画しているので、実装時は target stack のアイコンライブラリ (Lucide / Heroicons / Phosphor 等) に置き換えてください。

## Architecture & Concepts

実装前に、以下のドメイン概念を必ず理解してください。`data.js` の構造がそのまま情報設計の骨格です。

### Data model

```
Process (例: api-design, testing, incident-response)
├── id, name, phase (spec/dev/test/release/ops), description
└── units: Unit[]
       ├── id, name, description
       ├── effort:        number (時間)
       ├── frequency:     number (回 / 月)
       ├── cost:          effort × frequency  (h / mo)
       ├── executor:      "human" | "script" | "ai_agent"
       ├── difficulty:    "low" | "medium" | "high"  (自動化の難しさ)
       ├── automation:    "manual" | "partially-automated" | "automated"
       ├── core:          boolean (中核業務か)
       ├── input / process / output: string[]
       ├── scope:         string[]
       └── rule:          string[]
```

派生:
- **DAG edges** (`data-dag.js`) — unit 間の依存・分岐 (`always` / `conditional` / `ref`) を保持。テスト実施 unit のように「結果が良ければ報告 / 不具合があればバグ起票」のような分岐を表現する。
- **Leverage score** (`data-leverage.js`) — `score = pain × ease × gap` で改善優先度を算出
  - `pain = cost (= effort × frequency)`
  - `ease = {low:3, medium:2, high:1}`
  - `gap  = {manual:3, partially-automated:2, automated:0}`
  - 高スコアほど「コストが大きく、自動化が易しく、まだ手作業」= Quick Win

### Visual system (共通)

すべての画面で共有される token は `console-tokens.jsx` に集約。Light / Dark のペアで定義されています。

| Token | Light | Dark | 用途 |
|---|---|---|---|
| `bg` | `#FCFCFC` | `#0B0B0F` | アプリ全体の背景 |
| `bgPanel` | `#FFFFFF` | `#121218` | カード / パネル |
| `bgSubtle` | `#F7F7F7` | `#16161D` | サイドバー等の少し沈んだ背景 |
| `bgInset` | `#FAFAFA` | `#0F0F14` | テーブルヘッダ等の凹み |
| `border` | `#E5E5E5` | `#23232C` | 通常境界線 |
| `borderSoft` | `#F0F0F0` | `#1A1A22` | サブの境界線 |
| `text` | `#0E0E0E` | `#EDEDF0` | 本文 |
| `textMid` | `#525252` | `#9A9AA8` | 副次テキスト |
| `textDim` | `#A3A3A3` | `#5F5F6E` | キャプション・ラベル |
| `accent` | `#2563EB` | `#7AA5FF` | ブランドアクセント (青) |
| `accentBg` | `#EEF2FF` | `rgba(122,165,255,0.10)` | アクセント背景 |
| `purple` | `#7C3AED` | `#B79DFF` | ai_agent / 二次アクセント |
| `purpleBg` | `#F5F3FF` | `rgba(183,157,255,0.10)` | 紫背景 |
| `ok` | `#10B981` | `#34D399` | 成功 / automated |
| `warn` | `#D97706` | `#F59E0B` | 警告 / partial |
| `danger` | `#DC2626` | `#F87171` | エラー / core |

**Phase pills** (process の phase ごとの色):
- `spec` → 紫 `#7C3AED`
- `dev` → 青 `#2563EB`
- `test` → 橙 `#D97706`
- `release` → 緑 `#059669`
- `ops` → ピンク `#DB2777`
すべて `rgba(色, 0.10)` の薄い背景の上に同色の文字。

**Executor pills**:
- `script` → accent (青)
- `ai_agent` → purple
- `human` → gray

### Typography

- 本文: **Inter** 400 / 500 / 600 / 700
- 数値・コード・ラベル: **JetBrains Mono** 400 / 500 / 600
- letter-spacing は見出しのみ `-0.02em` 〜 `-0.025em` 程度のタイト。本文は標準。
- スケール (px、line-height): 9.5 / 10 / 10.5 / 11 / 11.5 / 12 / 12.5 / 13 / 13.5 / 14 / 15 / 16 / 18 / 20 / 22 / 24 / 28 / 34 / 36
- 見出し階層: H1 = 22–36px / 700, H2 = 13–18px / 700, ラベル = 9.5–11px uppercase letter-spacing 0.05–0.1em

### Iconography

実装時は **Lucide** 推奨 (軽量 / 線が細め / Inter と相性が良い)。プロトタイプ内の SVG は再現用の placeholder です。

## Variants — どれを実装するか

3 系統 × 各 Light / Dark + 共通の Heatmap / DAG detail。すべて同じデータモデルから生成。

### A. Balanced (`va-balanced.jsx` + `va-detail-dag.jsx` + `va-heatmap.jsx`)

PdM・エンジニア・経営すべてが触れることを想定したバランス重視。情報量と密度の中間。**現時点での推奨デフォルト案**。

- **Index** — 上部に KPI 4 枚、左ナビにプロセス一覧、メインに process カードグリッド。
- **Unit detail (DAG)** — 中央に DAG 描画 (svg)、右に unit metadata、下に I/O。分岐ノードでは Outgoing branches テーブルを表示。
- **Heatmap** — `Difficulty (Y) × Cost (X) × automation (色)` の 2D heatmap 左、Top 10 leverage ranking 右。**Quick win セルは左上** に固定 (= 高コスト × 着手簡単 × manual)。

### B. Document (`vb-document.jsx`)

Notion 的な読み物寄り。PdM や非エンジニアが「読んで理解する」用途。

- 左に目次、中央に 720px 幅の article、見出し階層がはっきり / 余白広め / 本文 14–16px。
- Process カード、Unit detail (Scope / Rule / Input·Process·Output / Executor) を順序立てて表示。

### C. Compact Power (`vc-compact.jsx`)

Linear / Vercel 的な高密度ツール。エンジニアが速く扱う用途。

- ヘッダタブ → フィルタチップ → 密度の高いテーブル (zebra 行・モノスペース統計)。
- Unit detail は 2 ペイン構成、metric 6 セル grid、I/O / Scope·Rule / Executor·Links を左右に。

### Cross-cutting screens

- **Heatmap (`va-heatmap.jsx`)** — 改善レバレッジ可視化。どの variant を採用してもこの画面は必須。
- **DAG detail (`va-detail-dag.jsx`)** — 分岐を持つ unit の詳細。`testing` プロセスの「テスト実施」がサンプル。

## Screens & Layouts (詳細)

### Common chrome

すべての画面の最上段:

```
┌─────────────────────────────────────────────────────┐
│ [●] BizSpec │ workspace · default     ⌘K Search…  │  ← header (44px tall)
├─────────────────────────────────────────────────────┤
│ Overview │ Processes │ Heatmap │ Graph │ YAML       │  ← tabs (36px)
└─────────────────────────────────────────────────────┘
```

- header: `padding: 0 16px`, height `44px`, border-bottom `1px solid border`
- ロゴ: 16×16px の square (accent)、半径 4px、隣に "BizSpec" 13.5px / 600
- 検索ボックス: 11px / `padding: 4px 8px` / `border 1px border` / radius 5px / mono / placeholder "⌘ K  Search…"
- tabs: 12px / アクティブのみ accent 色 + 下線 2px

### Heatmap (`va-heatmap.jsx`)

- 上に KPI bar (Total units / Manual units / Manual hours / Top score) 4 セル
- メインを 2 カラム grid (1.4fr / 1fr):
  - **左: heatmap matrix**
    - Y 軸 (上→下): `low` / `medium` / `high` (= 自動化の難しさ)
    - X 軸 (左→右): `top 25%` / `≤50%` / `≤75%` / `≤100%` (= cost 4分位、左ほど高コスト)
    - 各セル: 該当 unit を最大 3 つ縦に並べる、unit chip = `padding 4px 8px` / `radius 4px` / 背景は automation status 色 (`STATUS_BG`) / 文字色は `STATUS_COLOR`
    - **左上セル** = `low difficulty × top-25% cost × manual` → セル枠を `2px solid accent`、右上に "★ QUICK WIN" ラベル (9px / accent / 700)
    - 軸ラベルは `bgInset` 背景の小さなセル、9.5px uppercase letter-spacing 0.06em
    - 下に `← high cost · low cost →`
  - **右: Top 10 leverage list**
    - 各行: unit name / score (mono) / 横バー (`accent` 50% opacity, 幅 = score / max)
    - クリックで unit detail へ
    - 下に "How score works" 説明枠 (`bgInset` / `borderSoft`)
- 下に Reading guide 3 列 (Quick wins / Strategic / Skip & monitor)

### DAG detail (`va-detail-dag.jsx`)

- header の breadcrumb: `BizSpec / testing / テスト実施`
- 右に Graph / List トグル
- 2 カラム grid (300px / 1fr):
  - **左: DAG canvas**
    - 凡例: `必ず` (実線) / `条件分岐` (破線 + 黄ラベル) / `参照` (点線 grey)
    - SVG ノードは `120 × 36` の rounded rect、選択ノードは accent 枠 / 背景 accentBg
    - エッジ条件ラベルは小さな黄色 chip
  - **右: detail panel**
    - H1 (24px / 700) + executor pill + core pill (該当時) + "fork point · 2 outgoing" pill
    - description (13px / textMid / max-width 640px)
    - metric grid 5 セル: Effort / Frequency / Cost / Difficulty / Branches、各セル `bgPanel` / 1px border / radius 8px
    - Outgoing branches テーブル: Kind / Next unit / Condition / Probability
    - Input · Process · Output 3 列カード、各 column 上部に色付きラベル (IN=accent, PROCESS=purple, OUT=ok)

### B Document — Index (`vb-document.jsx` VBIndex)

- 3 カラム grid (240px / 1fr / 240px)
  - 左: 目次 + Processes 一覧 (薄いボーダー / アクティブ accent + 左ボーダー 2px)
  - 中央: 最大 720px の article
    - eyebrow 11px uppercase letter-spacing 0.1em / textMid
    - H1 34px / 700 / -0.025em
    - lead 15px / textMid / lh 1.55
    - tip callout: `accentBg` 背景 / `borderLeft 3px accent` / radius 4px
    - Process card grid (2列): 各カード `bgPanel` / 1px border / radius 8px / `padding 16px 18px` — process name (16px / 600) + phase pill + description + units 数 + cost
- 内側 max-width 1080px, `padding 32px 40px`

### B Document — Detail (`vb-document.jsx` VBDetail)

- 同じ 3 カラム
  - 左: そのプロセスの units 一覧 (アクティブのみ accent ボーダー左)
  - 中央: 大きな article
    - eyebrow → H1 36px → lead 16px
    - metric 4 セル grid (Effort / Frequency / Cost / Difficulty)
    - H2 "Scope" → `<ol>` 14px / lh 1.7
    - H2 "Rule" → `warn` 縦ボーダーの黄色 callout
    - H2 "Input / Process / Output" → 縦並びカード (各 row = label chip + 内容リスト)
    - H2 "Executor" → script pill + 説明文

### C Compact — Index (`vc-compact.jsx` VCIndex)

- 上から:
  - super-header: 32px 高 / 文字 12px / breadcrumb 風タブ (Overview / Processes / Heatmap / Graph)
  - filter bar: 28px 高 / `bgInset` 背景 / Pill chips: `core: any`, `executor: *`, `phase: *`, `status: *`
  - KPI strip: 32px 高 / mono 数値
  - 高密度テーブル: 行高 ~32px, zebra (`bgInset` を奇数行)
    - 列: ▸ (展開) / name / phase / units / executors / cost / h/mo / auto%
    - hover で背景 `bgSubtle`

### C Compact — Detail (`vc-compact.jsx` VCDetail)

- 2 カラム grid (240px / 1fr):
  - 左: unit list (sidebar)
  - 右: detail
    - H1 22px / 700 + executor pill 一列
    - metric grid 6 セル (effort / freq / cost / lev / diff / status)
    - 2 カラム:
      - 左: I/O accordion 風カード
      - 右: Scope·Rule list / Executor·Links

## Interactions

### グローバル
- 言語切替: `i18n.js` の `window.setLang("ja" | "en")` を呼ぶ。Tweaks panel から行うのは prototype のみで、本番は user preference に保存。
- ダークモード: 現状 prototype は static prop 切替。本番では `prefers-color-scheme` + 手動トグル両対応。

### Heatmap
- セル hover → 1px accent 内側枠 + `bgSubtle` 背景
- unit chip click → DAG detail へ遷移
- Top 10 行 click → 同上
- KPI hover effect なし

### DAG
- ノード click → そのノードを選択 (右パネル更新)
- グラフは pan / zoom 想定 (実装時は `@xyflow/react` (旧 reactflow) または `dagre + d3` を推奨)

### Document
- 目次 click → スムーズスクロール
- Process card click → そのプロセス detail へ

### Compact
- 行 hover → 背景 `bgSubtle`
- 行展開 (▸ クリック) → unit 一覧をインライン展開
- ヘッダクリックでソート (cost / units / auto%)

### Tweaks panel
- これは **prototype 専用** です。本番の UI には不要。

## State management (推奨)

target stack 次第ですが、ざっくり想定:
- **Server state**: Process / Unit / DAG edges / Leverage score を SWR or React Query で取得 (源は YAML or DB)
- **Client state**:
  - `lang`: ja / en (LocalStorage 永続化)
  - `theme`: light / dark / system
  - filters (executor / phase / status / core)
  - 選択中の process / unit (URL state にすべき: `?process=...&unit=...`)
- **URL routing** 案: `/processes/:processId/units/:unitId`, `/heatmap`, `/graph`

## i18n

`i18n.js` に全固定文言を `STRINGS["domain.context.label"] = { ja, en }` 形式で集約。

- 解決: `window.t("heatmap.title")` / `window.t("kpi.ofTotal", { pct: 35 })`
- 切替: `window.setLang("en")` → `__lang_change` event を dispatch、`useLang()` で購読
- **本番実装時は** `react-i18next` / `next-intl` / `formatjs` のいずれかに移植。キー命名 (`domain.context.label`) はそのまま流用可能。
- 数値・複数形・日付は `Intl.NumberFormat` / `Intl.DateTimeFormat` / ICU MessageFormat を使うこと (現状 prototype は plain string interpolation)。
- データ側 (`data.js` の process / unit name や description) はまだ ja のみ。実装時は `name_i18n: { ja, en }` のような構造に拡張するか、別 translation table を持つ。

## Design Tokens (sumarry)

```ts
// colors (light)
const palette = {
  brand: "#2563EB",
  brandDark: "#7AA5FF",  // dark-mode equivalent
  purple: "#7C3AED",
  purpleDark: "#B79DFF",
  text: "#0E0E0E",
  textMid: "#525252",
  textDim: "#A3A3A3",
  bg: "#FCFCFC",
  bgPanel: "#FFFFFF",
  bgInset: "#FAFAFA",
  border: "#E5E5E5",
  ok: "#10B981",
  warn: "#D97706",
  danger: "#DC2626",
};

// type
const fontSans = "'Inter', sans-serif";
const fontMono = "'JetBrains Mono', monospace";

// spacing scale (used loosely)
// 2 / 4 / 6 / 8 / 10 / 12 / 14 / 16 / 18 / 20 / 24 / 28 / 32 / 40 px

// radius
// chip: 3-4px, button/input: 4-5px, card: 6-8px

// shadows — 基本フラット。hover/elevation で必要なら "0 1px 2px rgba(0,0,0,0.04)" 程度
```

## Files in this bundle

| File | 役割 |
|---|---|
| `console-variants.html` | エントリポイント。すべての variant を design canvas で並べる |
| `console-tokens.jsx` | 全画面共有の TOKENS / Pill / phase color / executor color |
| `i18n.js` | 言語別文言テーブル + `t()` / `setLang()` / `useLang()` フック |
| `data.js` | Process / Unit のサンプルデータ |
| `data-dag.js` | DAG edges (testing process がサンプル) |
| `data-leverage.js` | Leverage score 計算 + automation status 拡張 |
| `va-balanced.jsx` | A: Balanced — Index と線形 Detail (旧) |
| `va-detail-dag.jsx` | A: DAG detail (testing 分岐サンプル) |
| `va-heatmap.jsx` | A: Heatmap (Quick Win 可視化) |
| `vb-document.jsx` | B: Document — Atlas / Article |
| `vc-compact.jsx` | C: Compact Power — Table / Unit |
| `design-canvas.jsx` | prototype 用キャンバス (本番には不要) |
| `tweaks-panel.jsx` | prototype 用 ja/en トグル (本番には不要) |

## 実装の進め方 (推奨順)

1. **データモデルを確定** (`data.js` を眺めつつ TypeScript の型を引く)
2. **トークンを定義** (Tailwind config または CSS variables)
3. **共通 chrome** (header / tabs / phase pill / executor pill) を atom として実装
4. **Variant A の Index** → **Unit DAG detail** → **Heatmap** の順
5. B / C のどちらか (もしくは両方) を別ルートとして実装
6. i18n を `react-i18next` に移植
7. ダークモードの実装 (CSS variable 切替が一番ラク)

## Open questions (実装前に確認推奨)

- [ ] データソースは YAML ファイル / Postgres / Notion API のどれか
- [ ] 編集機能はあるか (現状 prototype はすべて閲覧のみ)
- [ ] DAG のレンダリングライブラリ選定 (xyflow / dagre / cytoscape)
- [ ] Leverage score の定義はチームで合意済か (重みの調整余地)
- [ ] data 側 i18n の方針 (name_i18n vs translation table)
- [ ] アクセシビリティ要件 (WCAG AA 想定で OK か)
