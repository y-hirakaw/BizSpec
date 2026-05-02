/* Augments BIZSPEC_DATA units with `automation` fields + leverage helpers.
   Loaded after data.js. Mutates units in-place; falls back gracefully if
   automation is missing on a unit (treated as { difficulty: "medium", status: "manual" }
   for executor=manual, or { status: "automated" } for executor=script). */

(function () {
  const D = window.BIZSPEC_DATA;
  const H = window.BIZSPEC_HELPERS;

  // Curated automation values per unit so the heatmap is realistic.
  // Keys are "<process-id>::<unit-name>". Anything not listed gets a sensible default.
  const A = {
    // api-design
    "api-design::要件確認":           { difficulty: "high",   status: "manual" },
    "api-design::インターフェース設計":  { difficulty: "medium", status: "partially-automated" },
    "api-design::設計レビュー":        { difficulty: "high",   status: "manual" },
    "api-design::OpenAPI定義作成":     { difficulty: "low",    status: "partially-automated" },
    "api-design::モックサーバー構築":   { difficulty: "low",    status: "automated" },
    // bug-fix
    "bug-fix::再現確認":               { difficulty: "medium", status: "partially-automated" },
    "bug-fix::原因調査":               { difficulty: "high",   status: "manual" },
    "bug-fix::修正方針決定":            { difficulty: "high",   status: "manual" },
    "bug-fix::実装":                   { difficulty: "medium", status: "partially-automated" },
    "bug-fix::回帰テスト":              { difficulty: "low",    status: "automated" },
    // dependency-update
    "dependency-update::更新検出":      { difficulty: "low",    status: "automated" },
    "dependency-update::影響評価":      { difficulty: "medium", status: "partially-automated" },
    "dependency-update::更新実行":      { difficulty: "low",    status: "automated" },
    "dependency-update::検証":         { difficulty: "medium", status: "partially-automated" },
    // implementation
    "implementation::設計確認":         { difficulty: "high",   status: "manual" },
    "implementation::テスト作成":        { difficulty: "medium", status: "partially-automated" },
    "implementation::実装":             { difficulty: "high",   status: "partially-automated" },
    "implementation::セルフレビュー":     { difficulty: "high",   status: "manual" },
    "implementation::PR作成":           { difficulty: "low",    status: "automated" },
    // incident-response
    "incident-response::検知":          { difficulty: "low",    status: "automated" },
    "incident-response::トリアージ":     { difficulty: "high",   status: "manual" },
    "incident-response::暫定対処":       { difficulty: "high",   status: "manual" },
    "incident-response::原因分析":       { difficulty: "high",   status: "manual" },
    "incident-response::恒久対策":       { difficulty: "high",   status: "manual" },
    "incident-response::ポストモーテム":   { difficulty: "medium", status: "manual" },
    // issue-refinement (PBIリファインメント)
    "issue-refinement::課題ヒアリング":   { difficulty: "high",   status: "manual" },
    "issue-refinement::ゴール定義":      { difficulty: "medium", status: "manual" },
    "issue-refinement::受け入れ条件":     { difficulty: "medium", status: "partially-automated" },
    "issue-refinement::技術調査":        { difficulty: "high",   status: "partially-automated" },
    "issue-refinement::見積り":          { difficulty: "medium", status: "manual" },
    "issue-refinement::依存整理":        { difficulty: "medium", status: "manual" },
    "issue-refinement::Ready判定":       { difficulty: "low",    status: "manual" },
    "issue-refinement::PBI作成":         { difficulty: "low",    status: "automated" },
    "issue-refinement::通知":            { difficulty: "low",    status: "automated" },
    // onboarding
    "onboarding::アカウント発行":         { difficulty: "low",    status: "manual" },
    "onboarding::環境構築":              { difficulty: "low",    status: "partially-automated" },
    "onboarding::ドキュメント案内":        { difficulty: "low",    status: "manual" },
    "onboarding::ペアプロ":              { difficulty: "high",   status: "manual" },
    "onboarding::1on1":                 { difficulty: "high",   status: "manual" },
    // pr-review
    "pr-review::差分確認":               { difficulty: "low",    status: "partially-automated" },
    "pr-review::コードレビュー":          { difficulty: "high",   status: "manual" },
    "pr-review::修正反映":               { difficulty: "medium", status: "partially-automated" },
    "pr-review::マージ":                  { difficulty: "low",    status: "automated" },
    // release
    "release::リリース計画":              { difficulty: "high",   status: "manual" },
    "release::ビルド":                   { difficulty: "low",    status: "automated" },
    "release::ステージング検証":           { difficulty: "medium", status: "partially-automated" },
    "release::本番デプロイ":              { difficulty: "low",    status: "automated" },
    "release::リリースノート":            { difficulty: "low",    status: "partially-automated" },
    // retrospective
    "retrospective::データ収集":           { difficulty: "low",    status: "automated" },
    "retrospective::ふりかえり会":          { difficulty: "high",   status: "manual" },
    "retrospective::改善案決定":           { difficulty: "high",   status: "manual" },
    "retrospective::アクション登録":         { difficulty: "low",    status: "partially-automated" },
    // sprint-planning
    "sprint-planning::ベロシティ確認":      { difficulty: "low",    status: "automated" },
    "sprint-planning::スコープ選定":        { difficulty: "high",   status: "manual" },
    "sprint-planning::タスク分解":          { difficulty: "medium", status: "partially-automated" },
    "sprint-planning::アサイン":           { difficulty: "medium", status: "manual" },
    "sprint-planning::コミットメント":       { difficulty: "high",   status: "manual" },
    // testing
    "testing::テスト計画":                  { difficulty: "high",   status: "manual" },
    "testing::ユニットテスト":               { difficulty: "low",    status: "partially-automated" },
    "testing::統合テスト":                  { difficulty: "medium", status: "partially-automated" },
    "testing::E2Eテスト":                  { difficulty: "medium", status: "manual" },
    "testing::テスト結果報告":               { difficulty: "low",    status: "partially-automated" },
  };

  // Defaults from executor when key is missing
  function defaultAutomation(u) {
    if (u.executor === "script")    return { difficulty: "low",    status: "automated" };
    if (u.executor === "ai_agent")  return { difficulty: "medium", status: "partially-automated" };
    return                                  { difficulty: "medium", status: "manual" };
  }

  D.processes.forEach(p => {
    p.units.forEach(u => {
      const key = `${p.id}::${u.name}`;
      u.automation = A[key] || defaultAutomation(u);
    });
  });

  // Leverage scoring
  // Pain  = duration × frequency (h/mo)
  // Ease  = invert difficulty: low=3, medium=2, high=1
  // Gap   = manual=3, partially-automated=2, automated=0
  // Score = Pain × Ease × Gap
  H.ease = (u) => {
    const d = u.automation?.difficulty;
    return d === "low" ? 3 : d === "medium" ? 2 : 1;
  };
  H.gap = (u) => {
    const s = u.automation?.status;
    return s === "manual" ? 3 : s === "partially-automated" ? 2 : 0;
  };
  H.leverage = (u) => H.cost(u) * H.ease(u) * H.gap(u);
  H.leverageBand = (score, max) => {
    if (max <= 0 || score === 0) return "none";
    const r = score / max;
    if (r >= 0.66) return "hot";
    if (r >= 0.33) return "warm";
    return "cool";
  };

  // Flatten all units with their process for ranking views
  H.allUnits = () => {
    const out = [];
    D.processes.forEach(p => p.units.forEach(u => out.push({ unit: u, process: p })));
    return out;
  };
})();
