/* Branching DAG sample data for the testing process — adds parallel + skip cases.
   Used by Variant A detail to demonstrate non-linear flows. */

window.BIZSPEC_DAG = {
  // testing process redrawn as a DAG
  testing: {
    name: "testing",
    phase: "test",
    units: [
      { id: "plan",       name: "テスト計画作成",  executor: "manual",   core: true,  duration: 2, frequency: 1, status: "stable" },
      { id: "cases",      name: "テストケース作成", executor: "ai_agent", core: true,  duration: 4, frequency: 1, status: "stable" },
      { id: "exec",       name: "テスト実施",      executor: "manual",   core: true,  duration: 6, frequency: 1, status: "stable" },
      { id: "report",     name: "テスト結果報告",  executor: "ai_agent", core: true,  duration: 2, frequency: 1, status: "stable" },
      { id: "bug_ticket", name: "バグ起票",        executor: "ai_agent", core: false, duration: 2, frequency: 1, status: "stable" },
    ],
    edges: [
      { from: "plan",  to: "cases" },
      { from: "cases", to: "exec"  },
      { from: "exec",  to: "report",     kind: "always" },           // always reported
      { from: "exec",  to: "bug_ticket", kind: "conditional", label: "if 不具合あり" }, // skip path
      { from: "report", to: "bug_ticket", kind: "ref" },             // weak/ref dependency (dashed)
    ],
    // grid layout — col, row (0-indexed); rendered top-to-bottom
    layout: {
      plan:       { col: 0, row: 0 },
      cases:      { col: 0, row: 1 },
      exec:       { col: 0, row: 2 },
      report:     { col: 0, row: 3 },
      bug_ticket: { col: 1, row: 3 },
    },
    cols: 2,
    rows: 4,
  },
};
