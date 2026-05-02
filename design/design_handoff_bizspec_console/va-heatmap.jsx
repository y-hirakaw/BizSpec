/* Variant A — Leverage Heatmap view
   2D scatter (Cost × Difficulty) coloured by automation status,
   plus a "Top 10 Quick Wins" ranked list on the right.
   Goal: surface the units with greatest improvement leverage. */

function VAHeatmap({ mode = "light" }) {
  window.useLang();
  const T = window.t;
  const t = window.TOKENS[mode];
  const H = window.BIZSPEC_HELPERS;

  // Status colour mapping (gap)
  const STATUS_COLOR = {
    manual:                 mode === "dark" ? "#F87171" : "#DC2626", // danger
    "partially-automated":  mode === "dark" ? "#F59E0B" : "#D97706", // warn
    automated:              mode === "dark" ? "#5F5F6E" : "#A3A3A3", // dim grey
  };
  const STATUS_BG = {
    manual:                 mode === "dark" ? "rgba(248,113,113,0.16)" : "rgba(220,38,38,0.10)",
    "partially-automated":  mode === "dark" ? "rgba(245,158,11,0.18)"  : "rgba(217,119,6,0.12)",
    automated:              mode === "dark" ? "rgba(154,154,168,0.16)" : "rgba(163,163,163,0.18)",
  };

  // Plot config
  const all = H.allUnits();
  const maxCost = Math.max(...all.map(({unit}) => H.cost(unit))) || 1;
  const maxLev  = Math.max(...all.map(({unit}) => H.leverage(unit))) || 1;

  // Difficulty order top→bottom: low (easy, top) → high (hard).
  // Combined with reversed cost columns, Quick Win lands top-LEFT.
  const DIFF_ROWS = ["low", "medium", "high"];
  const ROW_LABEL = { high: T("heatmap.diff.high"), medium: T("heatmap.diff.medium"), low: T("heatmap.diff.low") };
  const ROW_HINT  = { high: T("heatmap.diff.highHint"), medium: T("heatmap.diff.medHint"), low: T("heatmap.diff.lowHint") };

  // Cost columns: 4 buckets quartile-ish based on maxCost
  // Cost columns reversed: highest on the LEFT so quick-wins land top-left.
  const colBoundaries = [0.0, 0.25, 0.5, 0.75, 1.0];
  const COL_LABEL = [T("heatmap.col.top25"), T("heatmap.col.le50"), T("heatmap.col.le75"), T("heatmap.col.le100")];
  function colIndex(cost) {
    const r = cost / maxCost;
    if (r > colBoundaries[3]) return 0; // highest cost → leftmost
    if (r > colBoundaries[2]) return 1;
    if (r > colBoundaries[1]) return 2;
    return 3;
  }

  // Group units into cells
  const cells = {};
  DIFF_ROWS.forEach(d => COL_LABEL.forEach((_, ci) => { cells[`${d}|${ci}`] = []; }));
  all.forEach(({ unit, process }) => {
    const row = unit.automation.difficulty;
    const col = colIndex(H.cost(unit));
    cells[`${row}|${col}`].push({ unit, process });
  });

  // Top 10 leverage list
  const top = [...all]
    .map(({unit, process}) => ({ unit, process, score: H.leverage(unit) }))
    .filter(x => x.score > 0)
    .sort((a,b) => b.score - a.score)
    .slice(0, 10);

  // Stats
  const totalUnits = all.length;
  const manualUnits = all.filter(({unit}) => unit.automation.status === "manual").length;
  const manualHours = all
    .filter(({unit}) => unit.automation.status === "manual")
    .reduce((s, {unit}) => s + H.cost(unit), 0);
  const totalHours = all.reduce((s, {unit}) => s + H.cost(unit), 0);

  return (
    <div style={{
      fontFamily: "'Inter', 'Hiragino Kaku Gothic ProN', sans-serif",
      background: t.bg, color: t.text,
      width: "100%", height: "100%", fontSize: "12px",
      display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      {/* Top bar */}
      <div style={{ height: "44px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 16px", gap: "14px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "20px", height: "20px", borderRadius: "5px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "11px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
          <span style={{ fontWeight: 600, fontSize: "13.5px", letterSpacing: "-0.01em" }}>{T("app.name")}</span>
        </div>
        <div style={{ width: "1px", height: "16px", background: t.border }}></div>
        <span style={{ color: t.textMid, fontSize: "12px" }}>{T("app.workspace")}</span>
        <div style={{ flex: 1 }}></div>
        <div style={{ fontSize: "11px", padding: "4px 8px", background: t.bgSubtle, border: `1px solid ${t.border}`, borderRadius: "5px", color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>{T("app.search")}</div>
      </div>

      {/* Tabs */}
      <div style={{ borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", padding: "0 16px", height: "32px", alignItems: "center", gap: "16px" }}>
        {[[T("tab.overview"), false], [T("tab.processes"), false], [T("tab.heatmap"), true], [T("tab.graph"), false], [T("tab.yaml"), false]].map(([n, a]) => (
          <div key={n} style={{
            fontSize: "12px",
            color: a ? t.text : t.textMid,
            fontWeight: a ? 600 : 400,
            paddingBottom: "1px",
            borderBottom: a ? `2px solid ${t.accent}` : "2px solid transparent",
            height: "32px", display: "flex", alignItems: "center",
          }}>{n}</div>
        ))}
        <div style={{ flex: 1 }}></div>
        <span style={{ fontSize: "10.5px", color: t.textDim, fontFamily: "'JetBrains Mono', monospace" }}>
          {T("heatmap.formula")}
        </span>
      </div>

      {/* Body */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Main — heatmap */}
        <div style={{ flex: 1, overflow: "auto", padding: "20px 24px" }}>
          {/* Header */}
          <div style={{ marginBottom: "8px" }}>
            <h1 style={{ fontSize: "20px", fontWeight: 600, letterSpacing: "-0.02em", margin: 0 }}>{T("heatmap.title")}</h1>
            <div style={{ fontSize: "12px", color: t.textMid, marginTop: "3px" }}>
              {T("heatmap.subtitleA")}<span style={{ color: t.accent, fontWeight: 600 }}>{T("heatmap.subtitleB")}</span>{T("heatmap.subtitleC")}
            </div>
          </div>

          {/* KPIs */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px", marginBottom: "16px" }}>
            {[
              [T("kpi.totalUnitsShort"), totalUnits, ""],
              [T("kpi.manualUnits"), manualUnits, T("kpi.ofTotal", { pct: (manualUnits/totalUnits*100).toFixed(0) })],
              [T("kpi.manualHours"), `${manualHours}h`, T("kpi.ofMonthly", { total: totalHours })],
              [T("kpi.topScore"), top[0]?.score ?? 0, top[0] ? top[0].unit.name : "—"],
            ].map(([k, v, sub]) => (
              <div key={k} style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "10px 12px" }}>
                <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "4px" }}>{k}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
                  <div style={{ fontSize: "18px", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "-0.01em" }}>{v}</div>
                </div>
                {sub && <div style={{ fontSize: "10.5px", color: t.textDim, marginTop: "2px" }}>{sub}</div>}
              </div>
            ))}
          </div>

          {/* Heatmap grid */}
          <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "16px 18px 14px", marginBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <div>
                <div style={{ fontSize: "11px", fontWeight: 700, color: t.textMid, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "2px" }}>{T("heatmap.gridTitle")}</div>
                <div style={{ fontSize: "11.5px", color: t.textDim }}>{T("heatmap.gridSub")}</div>
              </div>
              <div style={{ display: "flex", gap: "10px", fontSize: "10.5px", color: t.textMid }}>
                <LegendDot color={STATUS_COLOR.manual} bg={STATUS_BG.manual}>{T("heatmap.legend.manual")}</LegendDot>
                <LegendDot color={STATUS_COLOR["partially-automated"]} bg={STATUS_BG["partially-automated"]}>{T("heatmap.legend.partial")}</LegendDot>
                <LegendDot color={STATUS_COLOR.automated} bg={STATUS_BG.automated}>{T("heatmap.legend.automated")}</LegendDot>
              </div>
            </div>

            {/* grid: 60px row label + 4 columns */}
            <div style={{ display: "grid", gridTemplateColumns: "62px repeat(4, 1fr)", gap: "1px", background: t.border, border: `1px solid ${t.border}`, borderRadius: "6px", overflow: "hidden" }}>
              {/* Header row */}
              <div style={{ background: t.bgInset, padding: "6px 8px", fontSize: "9.5px", color: t.textDim, letterSpacing: "0.06em", textTransform: "uppercase", display: "flex", alignItems: "center", justifyContent: "flex-end" }}>
                {T("heatmap.diff")}
              </div>
              {COL_LABEL.map((c, i) => (
                <div key={c} style={{ background: t.bgInset, padding: "6px 8px", fontSize: "9.5px", color: t.textDim, letterSpacing: "0.06em", textTransform: "uppercase", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span>{T("heatmap.costPrefix")} {c}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", color: t.textMid }}>≤ {Math.round(maxCost * colBoundaries[i+1])}h</span>
                </div>
              ))}
              {/* Body */}
              {DIFF_ROWS.map((d, ri) => (
                <React.Fragment key={d}>
                  <div style={{ background: t.bgInset, padding: "8px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "flex-end" }}>
                    <div style={{ fontSize: "11.5px", fontWeight: 600, color: t.text, fontFamily: "'JetBrains Mono', monospace" }}>{ROW_LABEL[d]}</div>
                    <div style={{ fontSize: "9.5px", color: t.textDim }}>{ROW_HINT[d]}</div>
                  </div>
                  {COL_LABEL.map((c, ci) => {
                    const items = cells[`${d}|${ci}`];
                    const isSweet = d === "low" && ci === 0;
                    return (
                      <div key={ci} style={{
                        background: t.bgPanel,
                        padding: "8px",
                        minHeight: "92px",
                        position: "relative",
                        outline: isSweet ? `2px solid ${t.accent}` : "none",
                        outlineOffset: "-2px",
                      }}>
                        {isSweet && (
                          <div style={{ position: "absolute", top: "4px", right: "4px", fontSize: "9px", color: t.accent, fontWeight: 700, letterSpacing: "0.05em" }}>{T("heatmap.quickWin")}</div>
                        )}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                          {items.length === 0 && (
                            <span style={{ fontSize: "10.5px", color: t.textDim, fontStyle: "italic" }}>—</span>
                          )}
                          {items.map(({ unit, process }) => {
                            const sc = STATUS_COLOR[unit.automation.status];
                            const sb = STATUS_BG[unit.automation.status];
                            return (
                              <div key={`${process.id}::${unit.name}`} title={`${process.name} · ${unit.name}\nstatus: ${unit.automation.status}\ncost: ${H.cost(unit)}h/mo · score: ${H.leverage(unit)}`}
                                style={{
                                  fontSize: "10.5px",
                                  padding: "3px 6px",
                                  borderRadius: "3px",
                                  background: sb,
                                  color: sc,
                                  border: `1px solid ${sc}33`,
                                  whiteSpace: "nowrap",
                                  fontWeight: 500,
                                  cursor: "pointer",
                                }}>
                                {unit.name}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </React.Fragment>
              ))}
            </div>
            <div style={{ display: "flex", justifyContent: "flex-start", marginTop: "6px", paddingLeft: "62px", fontSize: "9.5px", color: t.textDim, letterSpacing: "0.06em", textTransform: "uppercase" }}>
              {T("heatmap.axisX")}
            </div>
          </div>

          {/* Reading guide */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
            <Guide t={t} title={T("heatmap.guide.qwTitle")} body={T("heatmap.guide.qwBody")} tone={t.accent} />
            <Guide t={t} title={T("heatmap.guide.stratTitle")} body={T("heatmap.guide.stratBody")} tone={t.warn} />
            <Guide t={t} title={T("heatmap.guide.skipTitle")} body={T("heatmap.guide.skipBody")} tone={t.textDim} />
          </div>
        </div>

        {/* Right rail — Top 10 */}
        <div style={{ width: "340px", borderLeft: `1px solid ${t.border}`, background: t.bgPanel, padding: "20px 18px", overflow: "auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "4px" }}>
            <h2 style={{ fontSize: "13px", fontWeight: 700, letterSpacing: "-0.01em", margin: 0 }}>{T("heatmap.top10")}</h2>
            <span style={{ fontSize: "10px", color: t.textDim, letterSpacing: "0.06em", textTransform: "uppercase" }}>{T("heatmap.top10.tag")}</span>
          </div>
          <div style={{ fontSize: "11.5px", color: t.textMid, marginBottom: "14px", lineHeight: 1.5 }}>
            {T("heatmap.top10.desc")}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1px", background: t.borderSoft, border: `1px solid ${t.border}`, borderRadius: "6px", overflow: "hidden" }}>
            {top.map(({unit, process, score}, i) => {
              const band = H.leverageBand(score, maxLev);
              const barColor = band === "hot" ? t.danger : band === "warm" ? t.warn : t.accent;
              const ratio = score / (top[0]?.score || 1);
              const sc = STATUS_COLOR[unit.automation.status];
              return (
                <div key={`${process.id}::${unit.name}`} style={{
                  background: t.bgPanel, padding: "10px 12px", cursor: "pointer",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "5px" }}>
                    <span style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace", color: t.textDim, minWidth: "16px" }}>
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span style={{ fontSize: "12.5px", fontWeight: 600, color: t.text, flex: 1 }}>{unit.name}</span>
                    <span style={{ fontSize: "11.5px", fontWeight: 700, fontFamily: "'JetBrains Mono', monospace", color: barColor }}>
                      {score}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "5px", fontSize: "10.5px", color: t.textMid }}>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>{process.name}</span>
                    <span style={{ color: t.textDim }}>·</span>
                    <span>{H.cost(unit)}h/mo</span>
                    <span style={{ color: t.textDim }}>·</span>
                    <span style={{ color: sc }}>{unit.automation.status === "partially-automated" ? "partial" : unit.automation.status}</span>
                    <span style={{ color: t.textDim }}>·</span>
                    <span>diff: {unit.automation.difficulty}</span>
                  </div>
                  <div style={{ height: "3px", background: t.bgInset, borderRadius: "1px", overflow: "hidden" }}>
                    <div style={{ width: (ratio * 100) + "%", height: "100%", background: barColor }}></div>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: "16px", padding: "10px 12px", background: t.bgInset, border: `1px solid ${t.borderSoft}`, borderRadius: "6px" }}>
            <div style={{ fontSize: "10px", fontWeight: 700, color: t.textMid, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "5px" }}>{T("heatmap.scoreHow")}</div>
            <div style={{ fontSize: "11px", color: t.textMid, lineHeight: 1.55 }}>
              <div><span style={{ color: t.text, fontFamily: "'JetBrains Mono', monospace" }}>{T("heatmap.score.pain")}</span> {T("heatmap.score.painDef")}</div>
              <div><span style={{ color: t.text, fontFamily: "'JetBrains Mono', monospace" }}>{T("heatmap.score.ease")}</span> {T("heatmap.score.easeDef")}</div>
              <div><span style={{ color: t.text, fontFamily: "'JetBrains Mono', monospace" }}>{T("heatmap.score.gap")}</span>{T("heatmap.score.gapDef")}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LegendDot({ children, color, bg }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
      <span style={{ width: "9px", height: "9px", borderRadius: "2px", background: bg, border: `1px solid ${color}66`, display: "inline-block" }}></span>
      <span>{children}</span>
    </span>
  );
}

function Guide({ t, title, body, tone }) {
  return (
    <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderLeft: `3px solid ${tone}`, borderRadius: "6px", padding: "10px 12px" }}>
      <div style={{ fontSize: "11.5px", fontWeight: 700, color: t.text, marginBottom: "3px" }}>{title}</div>
      <div style={{ fontSize: "11.5px", color: t.textMid, lineHeight: 1.5 }}>{body}</div>
    </div>
  );
}

window.VAHeatmap = VAHeatmap;
