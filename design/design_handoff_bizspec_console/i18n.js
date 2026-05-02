/* i18n strings — ja / en
   Used by all variants. Resolve via window.t(key, lang).
   Defaults to "ja". Hooks listen for __lang_change postMessage. */

(function () {
  const STRINGS = {
    // ── shared chrome ─────────────────────────────────────────
    "app.name":                 { ja: "BizSpec",            en: "BizSpec" },
    "app.workspace":            { ja: "ワークスペース · default", en: "workspace · default" },
    "app.search":               { ja: "⌘ K  検索…",           en: "⌘ K  Search…" },
    "app.synced":               { ja: "同期済み",             en: "synced" },
    "app.updated":              { ja: "更新 2026·05·02",      en: "updated 2026·05·02" },

    // ── tabs ──────────────────────────────────────────────────
    "tab.overview":             { ja: "概要",                en: "Overview" },
    "tab.processes":            { ja: "プロセス",             en: "Processes" },
    "tab.heatmap":              { ja: "ヒートマップ",          en: "Heatmap" },
    "tab.graph":                { ja: "グラフ",               en: "Graph" },
    "tab.yaml":                 { ja: "YAML",                en: "YAML" },

    // ── filters ───────────────────────────────────────────────
    "filter.label":             { ja: "フィルタ",             en: "filter" },
    "filter.coreAny":           { ja: "core: 全て",           en: "core: any" },
    "filter.executorAll":       { ja: "executor: *",         en: "executor: *" },
    "filter.phaseAll":          { ja: "phase: *",            en: "phase: *" },
    "filter.statusAll":         { ja: "status: *",           en: "status: *" },

    // ── KPIs ──────────────────────────────────────────────────
    "kpi.processes":            { ja: "プロセス数",           en: "Processes" },
    "kpi.totalUnits":           { ja: "Unit 総数",           en: "Total units" },
    "kpi.monthlyCost":          { ja: "月間コスト",           en: "Monthly cost" },
    "kpi.automatable":          { ja: "自動化可能",           en: "Automatable" },
    "kpi.stable":               { ja: "安定",                 en: "stable" },
    "kpi.aiScript":             { ja: "ai+script",            en: "ai+script" },
    "kpi.totalUnitsShort":      { ja: "Unit 数",              en: "Total units" },
    "kpi.manualUnits":          { ja: "Manual unit",          en: "Manual units" },
    "kpi.manualHours":          { ja: "Manual 時間",          en: "Manual hours" },
    "kpi.topScore":             { ja: "最高スコア",            en: "Top score" },
    "kpi.ofTotal":              { ja: "全体の {pct}%",        en: "{pct}% of total" },
    "kpi.ofMonthly":            { ja: "{total}h/月 中",        en: "of {total}h/mo" },

    // ── tables ────────────────────────────────────────────────
    "th.process":               { ja: "プロセス",              en: "Process" },
    "th.phase":                 { ja: "フェーズ",              en: "Phase" },
    "th.units":                 { ja: "Unit数",               en: "Units" },
    "th.executors":             { ja: "実行主体",              en: "Executors" },
    "th.cost":                  { ja: "コスト",                en: "Cost" },
    "th.hpermo":                { ja: "h/月",                  en: "h/mo" },
    "th.name":                  { ja: "名前",                  en: "name" },
    "th.auto":                  { ja: "自動化",                en: "auto" },

    // ── overview body ─────────────────────────────────────────
    "overview.title":           { ja: "全プロセス",             en: "All processes" },
    "overview.summary":         { ja: "{p} プロセス · {u} unit · {c}h/月 を運用中",
                                  en: "{p} processes · {u} units · {c}h/mo committed" },
    "overview.eyebrow":         { ja: "プロセスアトラス",        en: "Process Atlas" },
    "overview.description":     { ja: "{p} 個の業務プロセスを {c} 時間 / 月 で運用中。executor の内訳から自動化レバレッジを把握できます。",
                                  en: "{p} business processes running at {c} hours / month. Use the executor breakdown to spot automation leverage." },
    "overview.tip":             { ja: "💡 ヒント — 各プロセスをクリックすると、unit の YAML 定義と effort × frequency のヒートマップを確認できます。",
                                  en: "💡 Tip — Click any process to see its unit YAML and the effort × frequency heatmap." },
    "overview.sectionH2":       { ja: "概要",                  en: "Overview" },
    "overview.unitsLabel":      { ja: "{n} unit",              en: "{n} units" },
    "overview.committed":       { ja: "を運用中",              en: "committed" },

    // ── unit detail ───────────────────────────────────────────
    "unit.metric.effort":       { ja: "Effort",               en: "Effort" },
    "unit.metric.frequency":    { ja: "Frequency",            en: "Frequency" },
    "unit.metric.cost":         { ja: "Cost",                 en: "Cost" },
    "unit.metric.difficulty":   { ja: "Difficulty",           en: "Difficulty" },
    "unit.metric.status":       { ja: "Status",               en: "Status" },
    "unit.metric.branches":     { ja: "Branches",             en: "Branches" },
    "unit.metric.leverage":     { ja: "Leverage",             en: "Leverage" },
    "unit.metric.perRun":       { ja: "/ 実行",                en: "per run" },
    "unit.metric.perMonth":     { ja: "/ 月",                  en: "/ month" },
    "unit.metric.permo":        { ja: "/月",                   en: "/mo" },
    "unit.metric.automation":   { ja: "自動化",                en: "automation" },
    "unit.metric.manualExec":   { ja: "手動実行",              en: "manual exec" },
    "unit.metric.reportBug":    { ja: "report / bug",         en: "report / bug" },

    "unit.io.label":            { ja: "Input · Process · Output", en: "Input · Process · Output" },
    "unit.io.in":               { ja: "IN",                   en: "IN" },
    "unit.io.process":          { ja: "PROCESS",              en: "PROCESS" },
    "unit.io.out":              { ja: "OUT",                  en: "OUT" },

    "unit.scope":               { ja: "Scope",                en: "Scope" },
    "unit.rule":                { ja: "Rule",                 en: "Rule" },
    "unit.executor":            { ja: "Executor",             en: "Executor" },
    "unit.links":               { ja: "Links",                en: "Links" },
    "unit.scopeRule":           { ja: "Scope · Rule",         en: "Scope · Rule" },
    "unit.executorLinks":       { ja: "Executor · Links",     en: "Executor · Links" },
    "unit.up":                  { ja: "UP",                   en: "UP" },
    "unit.down":                { ja: "DOWN",                 en: "DOWN" },
    "unit.prev":                { ja: "← 前",                  en: "← prev" },
    "unit.next":                { ja: "次 →",                  en: "next →" },
    "unit.edit":                { ja: "編集",                  en: "Edit" },
    "unit.unitOf":              { ja: "Unit {i} / {n}",        en: "Unit {i} of {n}" },

    // executor mini-strings
    "exec.scriptAutomatable":   { ja: "ツールで自動化可能",      en: "Automatable with scripts" },
    "exec.scriptDesc":          { ja: "OpenAPI 定義からのモックサーバー生成はツールで自動化できるため、人間の判断を介さずに実行できる。",
                                  en: "Mock server generation from OpenAPI definitions can be fully scripted — no human judgement required." },

    // unit content (shared sample — api-design / mock server)
    "sample.api.title":         { ja: "API モックサーバー稼働", en: "Run API mock server" },
    "sample.api.desc":          { ja: "OpenAPI 定義からモックサーバーを生成し、フロントエンド開発の並行作業を可能にする",
                                  en: "Generate a mock server from the OpenAPI spec so frontend can develop in parallel" },
    "sample.api.in1":           { ja: "OpenAPI Specification ファイル",
                                  en: "OpenAPI Specification file" },
    "sample.api.proc1":         { ja: "モックサーバーを生成・起動",
                                  en: "Generate and start the mock server" },
    "sample.api.proc2":         { ja: "動作確認・共有",          en: "Verify and share" },
    "sample.api.out1":          { ja: "稼働中のモックサーバー",   en: "Running mock server" },
    "sample.api.out2":          { ja: "接続情報ドキュメント",     en: "Connection info doc" },
    "sample.api.scope1":        { ja: "OpenAPI 定義に基づくモックサーバーの稼働",
                                  en: "Run a mock server backed by the OpenAPI definition" },
    "sample.api.scope2":        { ja: "接続情報・使い方の関係者共有",
                                  en: "Share connection info and usage with stakeholders" },
    "sample.api.rule1":         { ja: "本番 API と同じエンドポイント・スキーマで動作させる",
                                  en: "Mirror prod endpoints and schema exactly" },
    "sample.api.rule2":         { ja: "モックデータは実際の値に近いものを使う",
                                  en: "Use mock data that resembles real values" },
    "sample.api.upstream":      { ja: "OpenAPI定義作成",         en: "Create OpenAPI spec" },

    // testing dag sample
    "sample.test.title":        { ja: "テスト実施",              en: "Execute test" },
    "sample.test.desc":         { ja: "計画されたテストケースを実行し、結果を記録する。不具合検出時はバグ起票を経由する。",
                                  en: "Run planned test cases and log results. On defects, branch into bug filing." },
    "sample.test.forkPoint":    { ja: "fork point · 2 outgoing", en: "fork point · 2 outgoing" },
    "sample.test.outBranches":  { ja: "Outgoing branches",      en: "Outgoing branches" },
    "sample.test.kind":         { ja: "種別",                    en: "Kind" },
    "sample.test.next":         { ja: "次の unit",                en: "Next unit" },
    "sample.test.cond":         { ja: "条件",                    en: "Condition" },
    "sample.test.prob":         { ja: "確率",                    en: "Probability" },
    "sample.test.next1":        { ja: "テスト結果報告",            en: "Report test results" },
    "sample.test.next2":        { ja: "バグ起票",                 en: "File bug" },
    "sample.test.cond2":        { ja: "不具合あり",               en: "On defect" },
    "sample.test.in1":          { ja: "テストケース一式",          en: "Test case set" },
    "sample.test.in2":          { ja: "テスト環境",               en: "Test environment" },
    "sample.test.proc1":        { ja: "手順に沿って実行",          en: "Follow the steps" },
    "sample.test.proc2":        { ja: "結果を記録 · 不具合は起票へ", en: "Log results · file defects" },
    "sample.test.out1":         { ja: "テスト結果ログ",            en: "Test result log" },
    "sample.test.out2":         { ja: "(分岐) 起票チケット",        en: "(branch) bug ticket" },

    // dag legend / tip
    "dag.always":               { ja: "必ず",                    en: "always" },
    "dag.conditional":          { ja: "条件分岐",                 en: "conditional" },
    "dag.ref":                  { ja: "参照",                    en: "reference" },
    "dag.tip":                  { ja: "ノードをクリックで選択。⌘ドラッグでパン、⌘+/− でズーム。",
                                  en: "Click a node to select. ⌘-drag to pan, ⌘+/− to zoom." },
    "dag.tipLabel":             { ja: "Tip",                    en: "Tip" },
    "dag.viewGraph":            { ja: "グラフ",                  en: "Graph" },
    "dag.viewList":             { ja: "リスト",                  en: "List" },

    // heatmap
    "heatmap.title":            { ja: "Leverage heatmap",        en: "Leverage heatmap" },
    "heatmap.subtitleA":        { ja: "改善レバレッジが大きい unit を可視化。",
                                  en: "Visualizes units with the largest improvement leverage. " },
    "heatmap.subtitleB":        { ja: "左上のセル",                en: "Top-left cell" },
    "heatmap.subtitleC":        { ja: "= 高コスト × 着手簡単 = quick win.",
                                  en: " = high cost × easy = quick win." },
    "heatmap.formula":          { ja: "score = cost × ease × gap", en: "score = cost × ease × gap" },
    "heatmap.gridTitle":        { ja: "Effort × Difficulty",     en: "Effort × Difficulty" },
    "heatmap.gridSub":          { ja: "Y: 自動化の難易度 · X: 月間コスト · 色: status",
                                  en: "Y: difficulty · X: monthly cost · color: status" },
    "heatmap.diff":             { ja: "↓ diff",                  en: "↓ diff" },
    "heatmap.costPrefix":       { ja: "cost",                    en: "cost" },
    "heatmap.col.top25":        { ja: "上位25%",                  en: "top 25%" },
    "heatmap.col.le50":         { ja: "≤50%",                    en: "≤50%" },
    "heatmap.col.le75":         { ja: "≤75%",                    en: "≤75%" },
    "heatmap.col.le100":        { ja: "≤100%",                   en: "≤100%" },
    "heatmap.diff.high":        { ja: "high",                    en: "high" },
    "heatmap.diff.medium":      { ja: "medium",                  en: "medium" },
    "heatmap.diff.low":         { ja: "low",                     en: "low" },
    "heatmap.diff.highHint":    { ja: "難しい",                    en: "hard" },
    "heatmap.diff.medHint":     { ja: "中",                       en: "medium" },
    "heatmap.diff.lowHint":     { ja: "簡単",                     en: "easy" },
    "heatmap.axisX":            { ja: "← 高コスト · 低コスト →",   en: "← high cost · low cost →" },
    "heatmap.quickWin":         { ja: "★ QUICK WIN",             en: "★ QUICK WIN" },
    "heatmap.legend.manual":    { ja: "manual",                  en: "manual" },
    "heatmap.legend.partial":   { ja: "partial",                 en: "partial" },
    "heatmap.legend.automated": { ja: "automated",               en: "automated" },
    "heatmap.guide.qwTitle":    { ja: "Quick wins (左上)",         en: "Quick wins (top-left)" },
    "heatmap.guide.qwBody":     { ja: "高コスト × 着手簡単 × manual。最初に取り組むべき領域。",
                                  en: "High cost × easy × manual. Start here." },
    "heatmap.guide.stratTitle": { ja: "Strategic (左下)",          en: "Strategic (bottom-left)" },
    "heatmap.guide.stratBody":  { ja: "高コスト だが difficulty=high。中長期で計画的に。",
                                  en: "High cost but difficulty=high. Plan for the medium term." },
    "heatmap.guide.skipTitle":  { ja: "Skip / monitor (右)",       en: "Skip / monitor (right)" },
    "heatmap.guide.skipBody":   { ja: "コストが小さいので投資対効果が低い。後回しでよい。",
                                  en: "Low cost, low ROI. Defer." },
    "heatmap.top10":            { ja: "Top 10 leverage",         en: "Top 10 leverage" },
    "heatmap.top10.tag":        { ja: "quick wins",              en: "quick wins" },
    "heatmap.top10.desc":       { ja: "score 順 (cost × ease × gap)。クリックで unit 詳細へ。",
                                  en: "Sorted by score (cost × ease × gap). Click for details." },
    "heatmap.scoreHow":         { ja: "How score works",         en: "How score works" },
    "heatmap.score.pain":       { ja: "Pain",                     en: "Pain" },
    "heatmap.score.painDef":    { ja: "= duration × frequency",   en: "= duration × frequency" },
    "heatmap.score.ease":       { ja: "Ease",                     en: "Ease" },
    "heatmap.score.easeDef":    { ja: "= low:3 / med:2 / high:1",  en: "= low:3 / med:2 / high:1" },
    "heatmap.score.gap":        { ja: "Gap",                      en: "Gap" },
    "heatmap.score.gapDef":     { ja: " = manual:3 / partial:2 / auto:0", en: " = manual:3 / partial:2 / auto:0" },

    // doc-style
    "doc.toc":                  { ja: "ページ内",                 en: "On this page" },
    "doc.byPhase":              { ja: "フェーズ別",               en: "By phase" },
    "doc.crossLinks":           { ja: "プロセス間リンク",           en: "Cross-process links" },
    "doc.processCount":         { ja: "プロセス ({n})",            en: "Processes ({n})" },
    "doc.unitsList":            { ja: "{name} · units",           en: "{name} · units" },
    "doc.subtitle":             { ja: "Process documentation",    en: "Process documentation" },

    // misc
    "lang.label":               { ja: "言語",                     en: "Language" },
  };

  function makeT(lang) {
    return function t(key, vars) {
      const entry = STRINGS[key];
      if (!entry) return key;
      let s = entry[lang] != null ? entry[lang] : entry.ja;
      if (vars) {
        for (const k in vars) s = s.replace(new RegExp(`\\{${k}\\}`, "g"), vars[k]);
      }
      return s;
    };
  }

  // Default lang
  window.__lang = window.__lang || "ja";
  window.t = makeT(window.__lang);
  window.setLang = function (lang) {
    window.__lang = lang;
    window.t = makeT(lang);
    window.dispatchEvent(new CustomEvent("__lang_change", { detail: { lang } }));
  };

  // React hook — re-renders subscribers when lang flips
  window.useLang = function () {
    const [lang, setLangState] = React.useState(window.__lang);
    React.useEffect(() => {
      const onChange = (e) => setLangState(e.detail.lang);
      window.addEventListener("__lang_change", onChange);
      return () => window.removeEventListener("__lang_change", onChange);
    }, []);
    return [lang, window.setLang];
  };
})();
