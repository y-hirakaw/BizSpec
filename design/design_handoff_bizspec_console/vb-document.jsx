/* Variant B — DOCUMENT
   Notion-like, lower density, larger type, more breathing room.
   PdM-friendly. Text-first detail, callouts, numbered list flow. */

function VBIndex({ mode = "light" }) {
  window.useLang();
  const T = window.t;
  const t = window.TOKENS[mode];
  const data = window.BIZSPEC_DATA;
  const H = window.BIZSPEC_HELPERS;
  const allMax = Math.max(...data.processes.map(H.totalCost));
  const totalCost = data.processes.reduce((s, p) => s + H.totalCost(p), 0);

  return (
    <div style={{
      fontFamily: "'Inter', 'Hiragino Kaku Gothic ProN', sans-serif",
      background: t.bg, color: t.text, width: "100%", height: "100%",
      fontSize: "13px", display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      <div style={{ height: "44px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 20px", gap: "14px" }}>
        <div style={{ width: "20px", height: "20px", borderRadius: "5px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "11px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
        <span style={{ fontWeight: 600, fontSize: "13.5px" }}>{T("app.name")}</span>
        <span style={{ color: t.textMid, fontSize: "12px" }}>· {T("doc.subtitle")}</span>
        <div style={{ flex: 1 }}></div>
        <span style={{ fontSize: "11px", color: t.textMid }}>{T("app.updated")}</span>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left TOC */}
        <div style={{ width: "240px", borderRight: `1px solid ${t.border}`, background: t.bgPanel, padding: "20px 14px", overflow: "auto" }}>
          <div style={{ fontSize: "10px", color: t.textDim, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: "10px" }}>{T("doc.toc")}</div>
          {[[T("tab.overview"), true], [T("doc.byPhase"), false], [T("tab.heatmap"), false], [T("doc.crossLinks"), false]].map(([n, a]) => (
            <div key={n} style={{ padding: "5px 8px", fontSize: "12.5px", color: a ? t.accent : t.textMid, fontWeight: a ? 600 : 400, borderLeft: `2px solid ${a ? t.accent : "transparent"}`, marginLeft: "-2px", marginBottom: "1px" }}>{n}</div>
          ))}
          <div style={{ fontSize: "10px", color: t.textDim, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, margin: "20px 0 10px" }}>{T("doc.processCount", { n: data.processes.length })}</div>
          {data.processes.slice(0, 8).map(p => (
            <div key={p.id} style={{ padding: "4px 8px", fontSize: "12px", color: t.textMid, display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ color: t.textDim, fontSize: "11px" }}>§</span>
              <span>{p.name}</span>
            </div>
          ))}
        </div>

        {/* Article */}
        <div style={{ flex: 1, overflow: "auto", padding: "32px 56px" }}>
          <div style={{ maxWidth: "780px", margin: "0 auto" }}>
            <div style={{ fontSize: "11px", color: t.textMid, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "8px", fontWeight: 600 }}>{T("overview.eyebrow")}</div>
            <h1 style={{ fontSize: "34px", fontWeight: 700, letterSpacing: "-0.025em", margin: 0, lineHeight: 1.15 }}>{T("overview.title")}</h1>
            <div style={{ fontSize: "15px", color: t.textMid, marginTop: "10px", lineHeight: 1.55 }}
              dangerouslySetInnerHTML={{ __html: T("overview.description", { p: data.processes.length, c: `<span style="color:${t.text};font-weight:600">${totalCost}</span>` }) }} />

            {/* callout */}
            <div style={{
              marginTop: "20px", padding: "12px 16px",
              background: t.accentBg, borderLeft: `3px solid ${t.accent}`,
              borderRadius: "4px", fontSize: "12.5px", color: t.text, lineHeight: 1.6,
            }}>
              {T("overview.tip")}
            </div>

            {/* Cards */}
            <h2 style={{ fontSize: "18px", fontWeight: 700, marginTop: "32px", marginBottom: "12px", letterSpacing: "-0.015em" }}>{T("overview.sectionH2")}</h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>
              {data.processes.slice(0, 8).map(p => {
                const cost = H.totalCost(p);
                const ec = H.executorCounts(p);
                const ph = PHASE_COLOR[p.phase] || PHASE_COLOR.spec;
                return (
                  <div key={p.id} style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", padding: "14px 16px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                      <Pill bg={ph.bg} fg={ph.fg} mono={false}>{p.phase}</Pill>
                      <span style={{ fontSize: "10.5px", color: t.textDim }}>{T("overview.unitsLabel", { n: p.units.length })}</span>
                      <span style={{ marginLeft: "auto", fontSize: "12px", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>{cost}h/mo</span>
                    </div>
                    <div style={{ fontSize: "15px", fontWeight: 600, marginBottom: "8px", letterSpacing: "-0.01em" }}>{p.name}</div>
                    <div style={{ display: "flex", gap: "4px", marginBottom: "8px" }}>
                      {ec.script > 0 && <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg}>script {ec.script}</Pill>}
                      {ec.ai_agent > 0 && <Pill bg={exTone(mode, "ai_agent").bg} fg={exTone(mode, "ai_agent").fg}>ai {ec.ai_agent}</Pill>}
                      {ec.manual > 0 && <Pill bg={exTone(mode, "manual").bg} fg={exTone(mode, "manual").fg}>manual {ec.manual}</Pill>}
                    </div>
                    <div style={{ height: "4px", background: t.bgInset, borderRadius: "2px", overflow: "hidden" }}>
                      <div style={{ width: (cost / allMax * 100) + "%", height: "100%", background: t.accent }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VBDetail({ mode = "light" }) {
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
      background: t.bg, color: t.text, width: "100%", height: "100%",
      fontSize: "13.5px", display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      <div style={{ height: "44px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 20px", gap: "14px" }}>
        <div style={{ width: "20px", height: "20px", borderRadius: "5px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "11px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
        <span style={{ fontWeight: 600, fontSize: "13.5px" }}>{T("app.name")}</span>
        <span style={{ color: t.textDim }}>/</span>
        <span style={{ color: t.textMid }}>api-design</span>
        <span style={{ color: t.textDim }}>/</span>
        <span style={{ fontWeight: 500 }}>{T("sample.api.title")}</span>
        <div style={{ flex: 1 }}></div>
        <button style={{ fontSize: "11px", padding: "4px 10px", border: `1px solid ${t.border}`, background: t.bgPanel, borderRadius: "5px", color: t.textMid, cursor: "pointer", fontFamily: "inherit" }}>{T("unit.edit")}</button>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* TOC */}
        <div style={{ width: "240px", borderRight: `1px solid ${t.border}`, background: t.bgPanel, padding: "20px 14px", overflow: "auto" }}>
          <div style={{ fontSize: "10px", color: t.textDim, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: "10px" }}>{T("doc.unitsList", { name: "api-design" })}</div>
          {proc.units.map((u, i) => {
            const sel = u.name === selected.name;
            return (
              <div key={u.name} style={{
                padding: "8px 10px",
                background: sel ? t.accentBg : "transparent",
                borderLeft: `2px solid ${sel ? t.accent : "transparent"}`,
                marginLeft: "-2px", marginBottom: "1px",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "10px", color: t.textDim, fontFamily: "'JetBrains Mono', monospace", minWidth: "16px" }}>{String(i + 1).padStart(2, "0")}</span>
                  <span style={{ fontSize: "12.5px", fontWeight: sel ? 600 : 400, color: sel ? t.accent : t.text }}>{sel ? T("sample.api.title") : u.name}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Article */}
        <div style={{ flex: 1, overflow: "auto", padding: "32px 56px", background: t.bg }}>
          <div style={{ maxWidth: "740px", margin: "0 auto" }}>
            <div style={{ fontSize: "11px", color: t.textMid, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "8px", fontWeight: 600 }}>
              api-design · {T("unit.unitOf", { i: "05", n: "05" })}
            </div>
            <h1 style={{ fontSize: "36px", fontWeight: 700, letterSpacing: "-0.025em", margin: 0, lineHeight: 1.1 }}>{T("sample.api.title")}</h1>
            <div style={{ fontSize: "16px", color: t.textMid, marginTop: "12px", lineHeight: 1.55 }}>
              {T("sample.api.desc")}
            </div>

            <div style={{ display: "flex", gap: "6px", marginTop: "14px", flexWrap: "wrap" }}>
              <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg} padding="3px 9px">executor: script</Pill>
              <Pill bg={mode === "dark" ? "rgba(245,158,11,0.12)" : "#FEF3C7"} fg={t.warn} padding="3px 9px">status: review</Pill>
              <Pill bg={t.bgSubtle} fg={t.textMid} padding="3px 9px" mono={false}>core: false</Pill>
              <Pill bg={PHASE_COLOR.spec.bg} fg={PHASE_COLOR.spec.fg} mono={false} padding="3px 9px">phase: spec</Pill>
            </div>

            {/* Effort callout */}
            <div style={{ marginTop: "24px", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1px", background: t.border, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden" }}>
              {[[T("unit.metric.effort"), "1h"], [T("unit.metric.frequency"), "2/mo"], [T("unit.metric.cost"), "2h"], [T("unit.metric.difficulty"), "low"]].map(([k, v]) => (
                <div key={k} style={{ background: t.bgPanel, padding: "12px 16px" }}>
                  <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "4px" }}>{k}</div>
                  <div style={{ fontSize: "18px", fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>{v}</div>
                </div>
              ))}
            </div>

            {/* Scope */}
            <h2 style={{ fontSize: "18px", fontWeight: 700, marginTop: "28px", marginBottom: "8px", letterSpacing: "-0.015em" }}>{T("unit.scope")}</h2>
            <ol style={{ fontSize: "14px", lineHeight: 1.7, paddingLeft: "20px", margin: 0, color: t.text }}>
              <li>{T("sample.api.scope1")}</li>
              <li>{T("sample.api.scope2")}</li>
            </ol>

            {/* Rule callout */}
            <h2 style={{ fontSize: "18px", fontWeight: 700, marginTop: "24px", marginBottom: "8px", letterSpacing: "-0.015em" }}>{T("unit.rule")}</h2>
            <div style={{
              padding: "12px 16px",
              background: mode === "dark" ? "rgba(245,158,11,0.08)" : "#FFFBEB",
              borderLeft: `3px solid ${t.warn}`,
              borderRadius: "4px",
              fontSize: "13.5px", color: t.text, lineHeight: 1.6,
            }}>
              <div style={{ marginBottom: "4px" }}>{T("sample.api.rule1")}</div>
              <div>{T("sample.api.rule2")}</div>
            </div>

            {/* IO */}
            <h2 style={{ fontSize: "18px", fontWeight: 700, marginTop: "24px", marginBottom: "12px", letterSpacing: "-0.015em" }}>{T("unit.io.label")}</h2>
            <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden" }}>
              {[
                [T("unit.io.in"), [T("sample.api.in1")], t.accent],
                [T("unit.io.process"), [T("sample.api.proc1"), T("sample.api.proc2")], t.purple],
                [T("unit.io.out"), [T("sample.api.out1"), T("sample.api.out2")], t.ok],
              ].map(([label, items, color], i) => (
                <div key={label} style={{
                  display: "grid", gridTemplateColumns: "100px 1fr",
                  borderTop: i > 0 ? `1px solid ${t.borderSoft}` : "none",
                }}>
                  <div style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 700, color, letterSpacing: "0.06em", borderRight: `1px solid ${t.borderSoft}`, background: t.bgInset }}>{label}</div>
                  <div style={{ padding: "10px 14px" }}>
                    {items.map((it, j) => <div key={j} style={{ fontSize: "13.5px", padding: "3px 0" }}>{it}</div>)}
                  </div>
                </div>
              ))}
            </div>

            {/* Executor reasoning */}
            <h2 style={{ fontSize: "18px", fontWeight: 700, marginTop: "24px", marginBottom: "8px", letterSpacing: "-0.015em" }}>{T("unit.executor")}</h2>
            <p style={{ fontSize: "14px", lineHeight: 1.7, margin: 0, color: t.text }}>
              <Pill bg={exTone(mode, "script").bg} fg={exTone(mode, "script").fg} padding="3px 9px">script</Pill>
              {" — "}
              {T("exec.scriptDesc")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

window.VBIndex = VBIndex;
window.VBDetail = VBDetail;
