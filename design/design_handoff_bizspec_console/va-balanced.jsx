/* Variant A — BALANCED Console
   Default density. Light/dark toggle. Friendly to PdM + Eng.
   Names: "Cost" / "Effort" instead of YAML keys. */

function VAIndex({ mode = "light" }) {
  window.useLang();
  const T = window.t;
  const t = window.TOKENS[mode];
  const data = window.BIZSPEC_DATA;
  const H = window.BIZSPEC_HELPERS;
  const allMax = Math.max(...data.processes.map(H.totalCost));
  const totalUnits = data.processes.reduce((s, p) => s + p.units.length, 0);
  const totalCost = data.processes.reduce((s, p) => s + H.totalCost(p), 0);

  return (
    <div style={{
      fontFamily: "'Inter', 'Hiragino Kaku Gothic ProN', sans-serif",
      background: t.bg, color: t.text,
      width: "100%", height: "100%",
      fontSize: "12px",
      display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      {/* Top bar */}
      <div style={{
        height: "44px", borderBottom: `1px solid ${t.border}`,
        background: t.bgPanel, display: "flex", alignItems: "center",
        padding: "0 16px", gap: "14px",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "20px", height: "20px", borderRadius: "5px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "11px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
          <span style={{ fontWeight: 600, fontSize: "13.5px", letterSpacing: "-0.01em" }}>{T("app.name")}</span>
        </div>
        <div style={{ width: "1px", height: "16px", background: t.border }}></div>
        <span style={{ color: t.textMid, fontSize: "12px" }}>{T("app.workspace")}</span>
        <div style={{ flex: 1 }}></div>
        <div style={{ fontSize: "11px", padding: "4px 8px", background: t.bgSubtle, border: `1px solid ${t.border}`, borderRadius: "5px", color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>{T("app.search")}</div>
        <div style={{ display: "flex", gap: "6px", alignItems: "center", color: t.ok, fontSize: "11px" }}>
          <window.StatusDot color={t.ok} />
          <span>{T("app.synced")}</span>
        </div>
      </div>

      {/* Sub bar — tabs */}
      <div style={{ borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", padding: "0 16px", height: "32px", alignItems: "center", gap: "16px" }}>
        {[[T("tab.overview"), true], [T("tab.processes"), false], [T("tab.heatmap"), false], [T("tab.graph"), false], [T("tab.yaml"), false]].map(([n, a]) => (
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
        <Pill bg={t.bgSubtle} fg={t.textMid}>core: any</Pill>
        <Pill bg={t.bgSubtle} fg={t.textMid}>executor: *</Pill>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Sidebar */}
        <div style={{ width: "212px", borderRight: `1px solid ${t.border}`, background: t.bgPanel, padding: "12px 8px", overflow: "auto" }}>
          <div style={{ padding: "0 8px 8px", fontSize: "10px", color: t.textDim, letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 600 }}>{T("tab.processes")}</div>
          {data.processes.map((p, i) => {
            const ec = H.executorCounts(p);
            return (
              <div key={p.id} style={{ padding: "6px 8px", borderRadius: "5px", background: i === 0 ? t.bgSubtle : "transparent", marginBottom: "1px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "3px" }}>
                  <span style={{ fontSize: "12px", color: t.text, fontWeight: i === 0 ? 600 : 500 }}>{p.name}</span>
                  <span style={{ marginLeft: "auto", fontSize: "10px", color: t.textDim, fontFamily: "'JetBrains Mono', monospace" }}>{p.units.length}</span>
                </div>
                <div style={{ display: "flex", gap: "2px" }}>
                  <div style={{ width: ec.script * 6, height: "3px", background: t.accent, borderRadius: "1px" }}></div>
                  <div style={{ width: ec.ai_agent * 6, height: "3px", background: t.purple, borderRadius: "1px" }}></div>
                  <div style={{ width: ec.manual * 6, height: "3px", background: t.gray, borderRadius: "1px" }}></div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Main */}
        <div style={{ flex: 1, overflow: "auto", padding: "20px 24px", background: t.bg }}>
          {/* Header */}
          <div style={{ marginBottom: "16px" }}>
            <h1 style={{ fontSize: "20px", fontWeight: 600, letterSpacing: "-0.02em", margin: 0, color: t.text }}>{T("overview.title")}</h1>
            <div style={{ fontSize: "12px", color: t.textMid, marginTop: "3px" }}
              dangerouslySetInnerHTML={{ __html: T("overview.summary", { p: data.processes.length, u: totalUnits, c: `<span style="color:${t.text};font-weight:500">${totalCost}h/mo</span>` }) }} />
          </div>

          {/* KPIs */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px", marginBottom: "18px" }}>
            {[
              [T("kpi.processes"), data.processes.length, T("kpi.stable")],
              [T("kpi.totalUnits"), totalUnits, ""],
              [T("kpi.monthlyCost"), totalCost + "h", "↗ 4%"],
              [T("kpi.automatable"), "62%", T("kpi.aiScript")],
            ].map(([k, v, sub]) => (
              <div key={k} style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "12px 14px" }}>
                <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "6px" }}>{k}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
                  <div style={{ fontSize: "22px", fontWeight: 600, letterSpacing: "-0.02em", fontFamily: "'JetBrains Mono', monospace" }}>{v}</div>
                  {sub && <div style={{ fontSize: "10.5px", color: t.textDim }}>{sub}</div>}
                </div>
              </div>
            ))}
          </div>

          {/* Table */}
          <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden" }}>
            <div style={{
              display: "grid",
              gridTemplateColumns: "20px 1.4fr 0.6fr 0.5fr 1.5fr 1.2fr 0.7fr",
              padding: "8px 14px",
              fontSize: "10.5px", color: t.textMid, fontWeight: 500,
              letterSpacing: "0.04em", textTransform: "uppercase",
              borderBottom: `1px solid ${t.border}`, background: t.bgInset,
            }}>
              <div></div>
              <div>{T("th.process")}</div>
              <div>{T("th.phase")}</div>
              <div>{T("th.units")}</div>
              <div>{T("th.executors")}</div>
              <div>{T("th.cost")}</div>
              <div style={{ textAlign: "right" }}>{T("th.hpermo")}</div>
            </div>
            {data.processes.map((p, i) => {
              const cost = H.totalCost(p);
              const ec = H.executorCounts(p);
              const ratio = cost / allMax;
              const ph = PHASE_COLOR[p.phase] || PHASE_COLOR.spec;
              return (
                <div key={p.id} style={{
                  display: "grid",
                  gridTemplateColumns: "20px 1.4fr 0.6fr 0.5fr 1.5fr 1.2fr 0.7fr",
                  padding: "10px 14px", fontSize: "12px",
                  borderBottom: i < data.processes.length - 1 ? `1px solid ${t.borderSoft}` : "none",
                  alignItems: "center",
                }}>
                  <div><StatusDot color={t.ok} /></div>
                  <div style={{ color: t.text, fontWeight: 500 }}>{p.name}</div>
                  <div><Pill bg={ph.bg} fg={ph.fg} mono={false}>{p.phase}</Pill></div>
                  <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "11px", color: t.textMid }}>{p.units.length}</div>
                  <div style={{ display: "flex", gap: "3px" }}>
                    {ec.script > 0 && <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg}>script · {ec.script}</Pill>}
                    {ec.ai_agent > 0 && <Pill bg={exTone(mode, "ai_agent").bg} fg={exTone(mode, "ai_agent").fg}>ai · {ec.ai_agent}</Pill>}
                    {ec.manual > 0 && <Pill bg={exTone(mode, "manual").bg} fg={exTone(mode, "manual").fg}>manual · {ec.manual}</Pill>}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{ flex: 1, height: "5px", background: t.bgInset, border: `1px solid ${t.borderSoft}`, borderRadius: "2px", overflow: "hidden", maxWidth: "100px" }}>
                      <div style={{ width: (ratio * 100) + "%", height: "100%", background: ratio > 0.66 ? t.danger : ratio > 0.33 ? t.warn : t.accent }}></div>
                    </div>
                  </div>
                  <div style={{ textAlign: "right", fontFamily: "'JetBrains Mono', monospace", fontSize: "12px", fontWeight: 600, color: t.text }}>{cost}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function VADetail({ mode = "light" }) {
  window.useLang();
  const T = window.t;
  const t = window.TOKENS[mode];
  const data = window.BIZSPEC_DATA;
  const H = window.BIZSPEC_HELPERS;
  const proc = data.processes[0];
  const selected = proc.units[4];

  return (
    <div style={{
      fontFamily: "'Inter', 'Hiragino Kaku Gothic ProN', sans-serif",
      background: t.bg, color: t.text,
      width: "100%", height: "100%", fontSize: "12px",
      display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      {/* top bar */}
      <div style={{ height: "44px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 16px", gap: "14px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "20px", height: "20px", borderRadius: "5px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "11px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
          <span style={{ fontWeight: 600, fontSize: "13.5px" }}>{T("app.name")}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
          <span style={{ color: t.textDim }}>/</span>
          <span style={{ color: t.textMid }}>api-design</span>
          <span style={{ color: t.textDim }}>/</span>
          <span style={{ fontWeight: 500 }}>{T("sample.api.title")}</span>
        </div>
        <div style={{ flex: 1 }}></div>
        <button style={{ fontSize: "11px", padding: "4px 10px", border: `1px solid ${t.border}`, background: t.bgPanel, borderRadius: "5px", color: t.textMid, cursor: "pointer", fontFamily: "inherit" }}>{T("unit.prev")}</button>
        <button style={{ fontSize: "11px", padding: "4px 10px", border: `1px solid ${t.border}`, background: t.bgPanel, borderRadius: "5px", color: t.textMid, cursor: "pointer", fontFamily: "inherit" }}>{T("unit.next")}</button>
        <button style={{ fontSize: "11px", padding: "4px 10px", border: `1px solid ${t.border}`, background: t.bgPanel, borderRadius: "5px", color: t.text, cursor: "pointer", fontFamily: "inherit" }}>{ "{ }" } YAML</button>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left — flow */}
        <div style={{ width: "270px", borderRight: `1px solid ${t.border}`, background: t.bgPanel, padding: "16px 14px", overflow: "auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "8px" }}>
            <div style={{ fontSize: "13px", fontWeight: 600 }}>api-design</div>
            <Pill bg={PHASE_COLOR.spec.bg} fg={PHASE_COLOR.spec.fg} mono={false}>spec</Pill>
          </div>
          <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "14px", fontFamily: "'JetBrains Mono', monospace" }}>5 units · {H.totalCost(proc)}h/mo</div>
          {proc.units.map((u, i) => {
            const sel = u.name === selected.name;
            const cost = H.cost(u);
            const ex = exTone(mode, u.executor);
            return (
              <div key={u.name}>
                <div style={{
                  border: sel ? `1.5px solid ${t.accent}` : `1px solid ${t.border}`,
                  background: sel ? t.accentBg : t.bgPanel,
                  borderRadius: "6px",
                  padding: "8px 10px",
                  display: "flex", alignItems: "center", gap: "8px",
                  cursor: "pointer",
                }}>
                  <span style={{ fontSize: "10px", color: t.textDim, fontFamily: "'JetBrains Mono', monospace", minWidth: "16px" }}>{String(i + 1).padStart(2, "0")}</span>
                  <span style={{ fontSize: "12px", fontWeight: sel ? 600 : 500, flex: 1, color: sel ? t.accent : t.text }}>{T("sample.api.title")}</span>
                  <Pill bg={ex.bg} fg={ex.fg}>{u.executor === "ai_agent" ? "ai" : u.executor}</Pill>
                  <span style={{ fontSize: "10.5px", color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>{cost}h</span>
                </div>
                {i < proc.units.length - 1 && (
                  <div style={{ marginLeft: "16px", height: "10px", borderLeft: `1.5px solid ${t.border}` }}></div>
                )}
              </div>
            );
          })}
        </div>

        {/* Main */}
        <div style={{ flex: 1, overflow: "auto", padding: "24px 28px", background: t.bg }}>
          {/* breadcrumb already in topbar; show title */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px", flexWrap: "wrap" }}>
            <h1 style={{ fontSize: "24px", fontWeight: 700, letterSpacing: "-0.02em", margin: 0 }}>{T("sample.api.title")}</h1>
            <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg} padding="3px 8px">script</Pill>
            <Pill bg={mode === "dark" ? "rgba(245,158,11,0.12)" : "#FEF3C7"} fg={t.warn} padding="3px 8px">review</Pill>
            <Pill bg={t.bgSubtle} fg={t.textMid} padding="3px 8px" mono={false}>core: false</Pill>
          </div>
          <div style={{ fontSize: "13px", color: t.textMid, marginBottom: "18px", maxWidth: "640px", lineHeight: 1.55 }}>
            {T("sample.api.desc")}
          </div>

          {/* metrics */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "1px", background: t.border, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden", marginBottom: "20px" }}>
            {[
              [T("unit.metric.effort"), "1h", T("unit.metric.perRun")],
              [T("unit.metric.frequency"), "2 / mo", ""],
              [T("unit.metric.cost"), "2h", T("unit.metric.perMonth")],
              [T("unit.metric.difficulty"), "low", T("unit.metric.automation")],
              [T("unit.metric.status"), "automated", ""],
            ].map(([k, v, sub]) => (
              <div key={k} style={{ background: t.bgPanel, padding: "12px 14px" }}>
                <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "4px" }}>{k}</div>
                <div style={{ fontSize: "16px", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "-0.01em" }}>{v}</div>
                {sub && <div style={{ fontSize: "10px", color: t.textDim, marginTop: "2px" }}>{sub}</div>}
              </div>
            ))}
          </div>

          {/* IO */}
          <SectionLabel t={t}>{T("unit.io.label")}</SectionLabel>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.1fr 1fr", gap: "10px", marginBottom: "20px" }}>
            {[
              [T("unit.io.in"), [T("sample.api.in1")], t.accent],
              [T("unit.io.process"), [T("sample.api.proc1"), T("sample.api.proc2")], t.purple],
              [T("unit.io.out"), [T("sample.api.out1"), T("sample.api.out2")], t.ok],
            ].map(([label, items, color]) => (
              <div key={label} style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "12px 14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                  <StatusDot color={color} />
                  <span style={{ fontSize: "10px", fontWeight: 700, color: t.textMid, letterSpacing: "0.08em" }}>{label}</span>
                </div>
                {items.map((it, i) => (
                  <div key={i} style={{ fontSize: "12px", color: t.text, padding: "3px 0", lineHeight: 1.5 }}>{it}</div>
                ))}
              </div>
            ))}
          </div>

          {/* Two columns */}
          <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: "10px", marginBottom: "20px" }}>
            <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "14px 16px" }}>
              <SectionLabel t={t}>{T("unit.scope")}</SectionLabel>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "12.5px", lineHeight: 1.7 }}>
                <li style={{ paddingLeft: "14px", position: "relative" }}>
                  <span style={{ position: "absolute", left: 0, color: t.accent }}>›</span>
                  {T("sample.api.scope1")}
                </li>
                <li style={{ paddingLeft: "14px", position: "relative" }}>
                  <span style={{ position: "absolute", left: 0, color: t.accent }}>›</span>
                  {T("sample.api.scope2")}
                </li>
              </ul>
              <div style={{ height: "1px", background: t.borderSoft, margin: "12px -16px" }}></div>
              <SectionLabel t={t}>{T("unit.rule")}</SectionLabel>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "12.5px", lineHeight: 1.7 }}>
                <li style={{ paddingLeft: "14px", position: "relative" }}>
                  <span style={{ position: "absolute", left: 0, color: t.accent }}>›</span>
                  {T("sample.api.rule1")}
                </li>
                <li style={{ paddingLeft: "14px", position: "relative" }}>
                  <span style={{ position: "absolute", left: 0, color: t.accent }}>›</span>
                  {T("sample.api.rule2")}
                </li>
              </ul>
            </div>
            <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "14px 16px" }}>
              <SectionLabel t={t}>{T("unit.executor")}</SectionLabel>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg} padding="3px 9px">script</Pill>
                <span style={{ fontSize: "12px", color: t.textMid }}>{T("exec.scriptAutomatable")}</span>
              </div>
              <div style={{ height: "1px", background: t.borderSoft, margin: "12px 0" }}></div>
              <SectionLabel t={t}>{T("unit.links")}</SectionLabel>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "10px", color: t.textDim, width: "32px", letterSpacing: "0.05em" }}>{T("unit.up")}</span>
                  <span style={{ fontSize: "12px", padding: "3px 9px", border: `1px solid ${t.border}`, borderRadius: "5px", background: t.bgInset, color: t.text }}>{T("sample.api.upstream")}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "10px", color: t.textDim, width: "32px", letterSpacing: "0.05em" }}>{T("unit.down")}</span>
                  <span style={{ fontSize: "12px", color: t.textDim }}>—</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SectionLabel({ t, children }) {
  return (
    <div style={{
      fontSize: "10px",
      fontWeight: 700,
      color: t.textMid,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      marginBottom: "8px",
    }}>{children}</div>
  );
}

window.VAIndex = VAIndex;
window.VADetail = VADetail;
