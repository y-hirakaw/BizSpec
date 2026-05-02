// Sample data extracted from BizSpec examples
// Each process has units; each unit has executor type, effort, status, links

window.BIZSPEC_DATA = {
  processes: [
    {
      id: "api-design",
      name: "api-design",
      phase: "spec",
      units: [
        { name: "要件確認",        executor: "manual",   core: true,  duration: 2, frequency: 1, status: "stable", aim: "API 化対象の業務要件・制約条件を整理し、ステークホルダーで合意する" },
        { name: "インターフェース設計", executor: "ai_agent", core: true,  duration: 4, frequency: 1, status: "stable", aim: "REST 原則に従い、エンドポイント・スキーマを設計する" },
        { name: "設計レビュー",    executor: "manual",   core: true,  duration: 2, frequency: 2, status: "stable", aim: "設計の一貫性・RESTful 原則・セキュリティ要件を確認する" },
        { name: "OpenAPI定義作成",  executor: "ai_agent", core: true,  duration: 4, frequency: 2, status: "stable", aim: "承認済み設計を OpenAPI 3.0 形式の機械可読定義に変換する" },
        { name: "モックサーバー構築", executor: "script", core: false, duration: 2, frequency: 1, status: "review", aim: "OpenAPI 定義からモックサーバーを生成し、フロントエンドの並行開発を可能にする" },
      ],
      edges: [["要件確認","インターフェース設計"],["インターフェース設計","設計レビュー"],["設計レビュー","OpenAPI定義作成"],["OpenAPI定義作成","モックサーバー構築"]],
    },
    {
      id: "bug-fix",
      name: "bug-fix",
      phase: "dev",
      units: [
        { name: "再現確認",     executor: "script",   core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "原因調査",     executor: "ai_agent", core: true, duration: 3, frequency: 4, status: "stable" },
        { name: "修正方針決定",  executor: "manual",   core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "実装",        executor: "ai_agent", core: true, duration: 2, frequency: 4, status: "stable" },
        { name: "回帰テスト",   executor: "script",   core: true, duration: 1, frequency: 4, status: "stable" },
      ],
      edges: [["再現確認","原因調査"],["原因調査","修正方針決定"],["修正方針決定","実装"],["実装","回帰テスト"]],
    },
    {
      id: "dependency-update",
      name: "dependency-update",
      phase: "ops",
      units: [
        { name: "更新検出",   executor: "script",   core: true, duration: 0.5, frequency: 4, status: "stable" },
        { name: "影響評価",   executor: "ai_agent", core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "更新実行",   executor: "script",   core: true, duration: 0.5, frequency: 4, status: "stable" },
        { name: "検証",      executor: "ai_agent", core: true, duration: 1, frequency: 4, status: "stable" },
      ],
      edges: [["更新検出","影響評価"],["影響評価","更新実行"],["更新実行","検証"]],
    },
    {
      id: "implementation",
      name: "implementation",
      phase: "dev",
      units: [
        { name: "設計確認",    executor: "manual",   core: true,  duration: 1, frequency: 8, status: "stable" },
        { name: "テスト作成",  executor: "ai_agent", core: true,  duration: 2, frequency: 8, status: "stable" },
        { name: "実装",       executor: "ai_agent", core: true,  duration: 4, frequency: 8, status: "stable" },
        { name: "セルフレビュー", executor: "manual", core: true,  duration: 1, frequency: 8, status: "stable" },
        { name: "PR作成",     executor: "script",   core: false, duration: 0.5, frequency: 8, status: "stable" },
      ],
      edges: [["設計確認","テスト作成"],["テスト作成","実装"],["実装","セルフレビュー"],["セルフレビュー","PR作成"]],
    },
    {
      id: "incident-response",
      name: "incident-response",
      phase: "ops",
      units: [
        { name: "検知",          executor: "script",   core: true, duration: 0.5, frequency: 2, status: "stable" },
        { name: "トリアージ",    executor: "manual",   core: true, duration: 1, frequency: 2, status: "stable" },
        { name: "暫定対処",      executor: "manual",   core: true, duration: 2, frequency: 2, status: "stable" },
        { name: "原因分析",      executor: "ai_agent", core: true, duration: 3, frequency: 2, status: "review" },
        { name: "恒久対策",      executor: "ai_agent", core: true, duration: 4, frequency: 1, status: "stable" },
        { name: "ポストモーテム", executor: "manual",   core: true, duration: 1, frequency: 2, status: "stable" },
      ],
      edges: [["検知","トリアージ"],["トリアージ","暫定対処"],["暫定対処","原因分析"],["原因分析","恒久対策"],["恒久対策","ポストモーテム"]],
    },
    {
      id: "issue-refinement",
      name: "PBIリファインメント",
      phase: "spec",
      units: [
        { name: "課題ヒアリング", executor: "manual",   core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "ゴール定義",     executor: "ai_agent", core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "受け入れ条件",   executor: "ai_agent", core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "技術調査",       executor: "ai_agent", core: true, duration: 2, frequency: 4, status: "review" },
        { name: "見積り",         executor: "manual",   core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "依存整理",       executor: "manual",   core: true, duration: 1, frequency: 4, status: "stable" },
        { name: "Ready判定",      executor: "manual",   core: true, duration: 0.5, frequency: 4, status: "stable" },
        { name: "PBI作成",        executor: "script",   core: false, duration: 0.5, frequency: 4, status: "stable" },
        { name: "通知",           executor: "script",   core: false, duration: 0.1, frequency: 4, status: "stable" },
      ],
      edges: [["課題ヒアリング","ゴール定義"],["ゴール定義","受け入れ条件"],["受け入れ条件","技術調査"],["技術調査","見積り"],["見積り","依存整理"],["依存整理","Ready判定"],["Ready判定","PBI作成"],["PBI作成","通知"]],
    },
    {
      id: "onboarding",
      name: "onboarding",
      phase: "ops",
      units: [
        { name: "アカウント発行", executor: "manual", core: true, duration: 1, frequency: 1, status: "stable" },
        { name: "環境構築",       executor: "manual", core: true, duration: 4, frequency: 1, status: "review" },
        { name: "ドキュメント案内", executor: "manual", core: true, duration: 1, frequency: 1, status: "stable" },
        { name: "ペアプロ",       executor: "manual", core: true, duration: 8, frequency: 1, status: "stable" },
        { name: "1on1",          executor: "manual", core: true, duration: 1, frequency: 1, status: "stable" },
      ],
      edges: [["アカウント発行","環境構築"],["環境構築","ドキュメント案内"],["ドキュメント案内","ペアプロ"],["ペアプロ","1on1"]],
    },
    {
      id: "pr-review",
      name: "PRレビュー",
      phase: "dev",
      units: [
        { name: "差分確認",     executor: "ai_agent", core: true, duration: 0.5, frequency: 12, status: "stable" },
        { name: "コードレビュー", executor: "manual",   core: true, duration: 1, frequency: 12, status: "stable" },
        { name: "修正反映",     executor: "ai_agent", core: true, duration: 1, frequency: 8,  status: "stable" },
        { name: "マージ",       executor: "script",   core: true, duration: 0.1, frequency: 12, status: "stable" },
      ],
      edges: [["差分確認","コードレビュー"],["コードレビュー","修正反映"],["修正反映","マージ"]],
    },
    {
      id: "release",
      name: "release",
      phase: "release",
      units: [
        { name: "リリース計画", executor: "manual", core: true, duration: 1, frequency: 2, status: "stable" },
        { name: "ビルド",      executor: "script", core: true, duration: 0.5, frequency: 2, status: "stable" },
        { name: "ステージング検証", executor: "ai_agent", core: true, duration: 2, frequency: 2, status: "stable" },
        { name: "本番デプロイ", executor: "script",  core: true, duration: 0.5, frequency: 2, status: "stable" },
        { name: "リリースノート", executor: "ai_agent", core: false, duration: 1, frequency: 2, status: "stable" },
      ],
      edges: [["リリース計画","ビルド"],["ビルド","ステージング検証"],["ステージング検証","本番デプロイ"],["本番デプロイ","リリースノート"]],
    },
    {
      id: "retrospective",
      name: "retrospective",
      phase: "spec",
      units: [
        { name: "データ収集", executor: "script",   core: true, duration: 1, frequency: 1, status: "stable" },
        { name: "ふりかえり会", executor: "manual",  core: true, duration: 2, frequency: 1, status: "stable" },
        { name: "改善案決定", executor: "manual",   core: true, duration: 1, frequency: 1, status: "stable" },
        { name: "アクション登録", executor: "ai_agent", core: false, duration: 0.5, frequency: 1, status: "stable" },
      ],
      edges: [["データ収集","ふりかえり会"],["ふりかえり会","改善案決定"],["改善案決定","アクション登録"]],
    },
    {
      id: "sprint-planning",
      name: "sprint-planning",
      phase: "spec",
      units: [
        { name: "ベロシティ確認", executor: "script",   core: true, duration: 0.5, frequency: 2, status: "stable" },
        { name: "スコープ選定",   executor: "manual",   core: true, duration: 1, frequency: 2, status: "stable" },
        { name: "タスク分解",     executor: "ai_agent", core: true, duration: 2, frequency: 2, status: "stable" },
        { name: "アサイン",       executor: "manual",   core: true, duration: 0.5, frequency: 2, status: "stable" },
        { name: "コミットメント", executor: "manual",   core: true, duration: 0.5, frequency: 2, status: "stable" },
      ],
      edges: [["ベロシティ確認","スコープ選定"],["スコープ選定","タスク分解"],["タスク分解","アサイン"],["アサイン","コミットメント"]],
    },
    {
      id: "testing",
      name: "testing",
      phase: "test",
      units: [
        { name: "テスト計画",   executor: "ai_agent", core: true,  duration: 2, frequency: 2, status: "stable" },
        { name: "ユニットテスト", executor: "ai_agent", core: true,  duration: 4, frequency: 4, status: "stable" },
        { name: "統合テスト",   executor: "ai_agent", core: true,  duration: 3, frequency: 2, status: "stable" },
        { name: "E2Eテスト",   executor: "manual",   core: true,  duration: 2, frequency: 2, status: "stable" },
        { name: "テスト結果報告", executor: "ai_agent", core: false, duration: 1, frequency: 2, status: "stable" },
      ],
      edges: [["テスト計画","ユニットテスト"],["ユニットテスト","統合テスト"],["統合テスト","E2Eテスト"],["E2Eテスト","テスト結果報告"]],
    },
  ],
  // Cross-process links (dependencies between processes)
  crossLinks: [
    ["api-design","implementation"],
    ["implementation","pr-review"],
    ["pr-review","testing"],
    ["testing","release"],
    ["bug-fix","pr-review"],
    ["issue-refinement","sprint-planning"],
    ["sprint-planning","implementation"],
    ["release","retrospective"],
    ["incident-response","bug-fix"],
    ["onboarding","implementation"],
    ["dependency-update","testing"],
  ],
};

// Helpers
window.BIZSPEC_HELPERS = {
  cost: (u) => (u.duration ?? 0) * (u.frequency ?? 0),
  totalCost: (p) => p.units.reduce((s, u) => s + (u.duration ?? 0) * (u.frequency ?? 0), 0),
  heatLevel: (cost, max) => {
    if (max <= 0) return "low";
    const ratio = cost / max;
    if (ratio < 0.33) return "low";
    if (ratio < 0.66) return "medium";
    return "high";
  },
  executorCounts: (p) => {
    const c = { script: 0, ai_agent: 0, manual: 0 };
    p.units.forEach(u => { c[u.executor]++; });
    return c;
  },
};
