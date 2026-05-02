/* Variant A — DAG detail view
   Replaces the linear left rail with a graph that supports:
   - parallel branches (siblings on same row)
   - conditional / skip edges (different stroke styles)
   - reference edges (dashed)
   Renders SVG over a positioned grid of node cards. */

function VADetailDAG({ mode = "light" }) {
  window.useLang();
  const T = window.t;
  const t = window.TOKENS[mode];
  const dag = window.BIZSPEC_DAG.testing;
  const H = window.BIZSPEC_HELPERS;

  // Selected node — pick "テスト実施" to showcase a fork point
  const selectedId = "exec";
  const selected = dag.units.find(u => u.id === selectedId);

  // Layout constants (px) — within a fixed 360w left graph panel
  const PANEL_W = 380;
  const COL_W = 168;
  const ROW_H = 84;
  const PAD_X = 18;
  const PAD_Y = 16;
  const NODE_W = 152;
  const NODE_H = 64;

  const nodeXY = (id) => {
    const { col, row } = dag.layout[id];
    return {
      x: PAD_X + col * COL_W,
      y: PAD_Y + row * ROW_H,
      cx: PAD_X + col * COL_W + NODE_W / 2,
      cy: PAD_Y + row * ROW_H + NODE_H / 2,
    };
  };

  const totalH = PAD_Y * 2 + dag.rows * ROW_H;
  const totalW = PAD_X * 2 + (dag.cols - 1) * COL_W + NODE_W;

  // Edge geometry — orthogonal with arrow at end
  function edgePath(from, to) {
    const a = nodeXY(from);
    const b = nodeXY(to);
    const sx = a.cx, sy = a.y + NODE_H;       // bottom-center
    const tx = b.cx, ty = b.y - 2;            // top-center (arrow lands just above)
    if (Math.abs(sx - tx) < 1) {
      return `M ${sx} ${sy} L ${tx} ${ty}`;
    }
    // step path: down to mid, across, down to target
    const midY = sy + (ty - sy) / 2;
    return `M ${sx} ${sy} L ${sx} ${midY} L ${tx} ${midY} L ${tx} ${ty}`;
  }

  // Edge between siblings on same row — dashed horizontal
  function edgePathSibling(from, to) {
    const a = nodeXY(from);
    const b = nodeXY(to);
    const sx = a.x + NODE_W;
    const sy = a.cy;
    const tx = b.x;
    const ty = b.cy;
    return `M ${sx} ${sy} L ${tx} ${ty}`;
  }

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
          <span style={{ color: t.textMid }}>{dag.name}</span>
          <span style={{ color: t.textDim }}>/</span>
          <span style={{ fontWeight: 500 }}>{T("sample.test.title")}</span>
        </div>
        <div style={{ flex: 1 }}></div>
        <div style={{ display: "flex", border: `1px solid ${t.border}`, borderRadius: "5px", overflow: "hidden", background: t.bgPanel }}>
          <button style={{ fontSize: "11px", padding: "4px 10px", border: "none", background: t.bgSubtle, color: t.text, cursor: "pointer", fontFamily: "inherit", borderRight: `1px solid ${t.border}`, fontWeight: 500 }}>{T("dag.viewGraph")}</button>
          <button style={{ fontSize: "11px", padding: "4px 10px", border: "none", background: "transparent", color: t.textMid, cursor: "pointer", fontFamily: "inherit" }}>{T("dag.viewList")}</button>
        </div>
        <button style={{ fontSize: "11px", padding: "4px 10px", border: `1px solid ${t.border}`, background: t.bgPanel, borderRadius: "5px", color: t.text, cursor: "pointer", fontFamily: "inherit" }}>{ "{ }" } YAML</button>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left — DAG */}
        <div style={{
          width: PANEL_W + "px", borderRight: `1px solid ${t.border}`,
          background: t.bgPanel, padding: "14px 0 14px 14px",
          overflow: "auto", display: "flex", flexDirection: "column",
        }}>
          <div style={{ paddingRight: "14px", display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "8px" }}>
            <div style={{ fontSize: "13px", fontWeight: 600 }}>{dag.name}</div>
            <Pill bg={PHASE_COLOR.test.bg} fg={PHASE_COLOR.test.fg} mono={false}>{dag.phase}</Pill>
          </div>
          <div style={{ paddingRight: "14px", fontSize: "10.5px", color: t.textMid, marginBottom: "12px", fontFamily: "'JetBrains Mono', monospace" }}>
            {dag.units.length} units · {dag.units.reduce((s,u)=>s+H.cost(u),0)}h/mo
          </div>

          {/* Legend */}
          <div style={{ paddingRight: "14px", display: "flex", gap: "10px", flexWrap: "wrap", fontSize: "10px", color: t.textMid, marginBottom: "10px" }}>
            <LegendLine t={t} kind="always" label={T("dag.always")} />
            <LegendLine t={t} kind="conditional" label={T("dag.conditional")} />
            <LegendLine t={t} kind="ref" label={T("dag.ref")} />
          </div>

          {/* SVG canvas + nodes */}
          <div style={{ position: "relative", width: totalW + "px", height: totalH + "px" }}>
            <svg width={totalW} height={totalH} style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
              <defs>
                <marker id={`arrow-${mode}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={t.textMid} />
                </marker>
                <marker id={`arrow-cond-${mode}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={t.warn} />
                </marker>
              </defs>
              <defs>
                <marker id={`arrow-hl-${mode}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={t.accent} />
                </marker>
                <marker id={`arrow-hl-cond-${mode}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={t.warn} />
                </marker>
              </defs>
              {/* Two-pass: render dimmed edges first, highlighted on top */}
              {[false, true].map(highlightPass => dag.edges.map((e, i) => {
                const related = e.from === selectedId || e.to === selectedId;
                if (highlightPass !== related) return null;
                const fromXY = nodeXY(e.from);
                const toXY = nodeXY(e.to);
                const sameRow = fromXY.cy === toXY.cy;
                const path = sameRow ? edgePathSibling(e.from, e.to) : edgePath(e.from, e.to);
                const dim = !related;
                const opacity = dim ? 0.28 : 1;

                if (e.kind === "ref") {
                  return (
                    <path key={`${highlightPass}-${i}`} d={path}
                      stroke={related ? t.accent : t.textDim}
                      strokeWidth={related ? 1.6 : 1.2}
                      strokeDasharray="3 3" fill="none" opacity={opacity} />
                  );
                }
                if (e.kind === "conditional") {
                  return (
                    <g key={`${highlightPass}-${i}`} opacity={opacity}>
                      <path d={path} stroke={t.warn}
                        strokeWidth={related ? 2 : 1.5}
                        strokeDasharray="5 3" fill="none"
                        markerEnd={`url(#${related ? `arrow-hl-cond-${mode}` : `arrow-cond-${mode}`})`} />
                      {e.label && (() => {
                        const a = nodeXY(e.from), b = nodeXY(e.to);
                        const lx = (a.cx + b.cx) / 2;
                        const ly = a.y + NODE_H + (b.y - (a.y + NODE_H)) / 2;
                        const tw = e.label.length * 6 + 12;
                        return (
                          <g>
                            <rect x={lx - tw/2} y={ly - 8} width={tw} height={16} rx="3"
                              fill={t.bgPanel} stroke={t.warn}
                              strokeOpacity={related ? 0.7 : 0.4} />
                            <text x={lx} y={ly + 3} fontSize="10" fill={t.warn}
                              textAnchor="middle" fontFamily="Inter, sans-serif"
                              fontWeight={related ? 600 : 400}>{e.label}</text>
                          </g>
                        );
                      })()}
                    </g>
                  );
                }
                return (
                  <path key={`${highlightPass}-${i}`} d={path}
                    stroke={related ? t.accent : t.textMid}
                    strokeWidth={related ? 2 : 1.5}
                    fill="none" opacity={opacity}
                    markerEnd={`url(#${related ? `arrow-hl-${mode}` : `arrow-${mode}`})`} />
                );
              }))}
            </svg>

            {dag.units.map(u => {
              const xy = nodeXY(u.id);
              const sel = u.id === selectedId;
              const ex = exTone(mode, u.executor);
              const cost = H.cost(u);
              return (
                <div key={u.id} style={{
                  position: "absolute",
                  left: xy.x + "px", top: xy.y + "px",
                  width: NODE_W + "px", height: NODE_H + "px",
                  background: sel ? t.accentBg : t.bgPanel,
                  border: sel ? `1.5px solid ${t.accent}` : `1px solid ${t.border}`,
                  borderRadius: "6px",
                  padding: "7px 9px",
                  boxSizing: "border-box",
                  display: "flex", flexDirection: "column", gap: "5px",
                  cursor: "pointer",
                  boxShadow: sel ? "0 1px 3px rgba(37,99,235,0.15)" : "none",
                }}>
                  <div style={{
                    fontSize: "12px", fontWeight: sel ? 600 : 500,
                    color: sel ? t.accent : t.text,
                    lineHeight: 1.25,
                    display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}>{u.name}</div>
                  <div style={{ display: "flex", gap: "3px", alignItems: "center", flexWrap: "wrap" }}>
                    <Pill bg={ex.bg} fg={ex.fg}>{u.executor === "ai_agent" ? "ai" : u.executor}</Pill>
                    {u.core && <Pill bg={mode === "dark" ? "rgba(248,113,113,0.12)" : "#FEE2E2"} fg={t.danger}>core</Pill>}
                    <span style={{ marginLeft: "auto", fontSize: "10px", color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>{cost}h/mo</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ flex: 1 }}></div>
          <div style={{ paddingRight: "14px", marginTop: "12px", paddingTop: "10px", borderTop: `1px solid ${t.borderSoft}` }}>
            <div style={{ fontSize: "9.5px", color: t.textDim, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>{T("dag.tipLabel")}</div>
            <div style={{ fontSize: "10.5px", color: t.textMid, lineHeight: 1.5 }}>
              {T("dag.tip")}
            </div>
          </div>
        </div>

        {/* Main — selected unit detail */}
        <div style={{ flex: 1, overflow: "auto", padding: "24px 28px", background: t.bg }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px", flexWrap: "wrap" }}>
            <h1 style={{ fontSize: "24px", fontWeight: 700, letterSpacing: "-0.02em", margin: 0 }}>{T("sample.test.title")}</h1>
            <Pill bg={exTone(mode, selected.executor).bg} fg={exTone(mode, selected.executor).fg} padding="3px 8px">{selected.executor}</Pill>
            {selected.core && <Pill bg={mode === "dark" ? "rgba(248,113,113,0.12)" : "#FEE2E2"} fg={t.danger} padding="3px 8px">core</Pill>}
            <Pill bg={t.bgSubtle} fg={t.textMid} padding="3px 8px" mono={false}>{T("sample.test.forkPoint")}</Pill>
          </div>
          <div style={{ fontSize: "13px", color: t.textMid, marginBottom: "18px", maxWidth: "640px", lineHeight: 1.55 }}>
            {T("sample.test.desc")}
          </div>

          {/* metric strip */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "1px", background: t.border, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden", marginBottom: "20px" }}>
            {[
              [T("unit.metric.effort"), "6h", T("unit.metric.perRun")],
              [T("unit.metric.frequency"), "1 / mo", ""],
              [T("unit.metric.cost"), "6h", T("unit.metric.perMonth")],
              [T("unit.metric.difficulty"), "med", T("unit.metric.manualExec")],
              [T("unit.metric.branches"), "2", T("unit.metric.reportBug")],
            ].map(([k, v, sub]) => (
              <div key={k} style={{ background: t.bgPanel, padding: "12px 14px" }}>
                <div style={{ fontSize: "10.5px", color: t.textMid, marginBottom: "4px" }}>{k}</div>
                <div style={{ fontSize: "16px", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "-0.01em" }}>{v}</div>
                {sub && <div style={{ fontSize: "10px", color: t.textDim, marginTop: "2px" }}>{sub}</div>}
              </div>
            ))}
          </div>

          {/* Branch panel */}
          <SectionLabel t={t}>{T("sample.test.outBranches")}</SectionLabel>
          <div style={{ background: t.bgPanel, border: `1px solid ${t.border}`, borderRadius: "8px", overflow: "hidden", marginBottom: "20px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "100px 1.4fr 0.8fr 1fr", padding: "8px 14px", fontSize: "10px", color: t.textMid, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", background: t.bgInset, borderBottom: `1px solid ${t.border}` }}>
              <div>{T("sample.test.kind")}</div><div>{T("sample.test.next")}</div><div>{T("sample.test.cond")}</div><div>{T("sample.test.prob")}</div>
            </div>
            <BranchRow t={t} mode={mode} kind="always" next={T("sample.test.next1")} cond="—" prob="100%" first />
            <BranchRow t={t} mode={mode} kind="conditional" next={T("sample.test.next2")} cond={T("sample.test.cond2")} prob="~ 35%" />
          </div>

          {/* IO */}
          <SectionLabel t={t}>{T("unit.io.label")}</SectionLabel>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.1fr 1fr", gap: "10px" }}>
            {[
              [T("unit.io.in"), [T("sample.test.in1"), T("sample.test.in2")], t.accent],
              [T("unit.io.process"), [T("sample.test.proc1"), T("sample.test.proc2")], t.purple],
              [T("unit.io.out"), [T("sample.test.out1"), T("sample.test.out2")], t.ok],
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
        </div>
      </div>
    </div>
  );
}

function LegendLine({ t, kind, label }) {
  const stroke = kind === "conditional" ? t.warn : kind === "ref" ? t.textDim : t.textMid;
  const dash = kind === "conditional" ? "5,3" : kind === "ref" ? "3,3" : "0";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
      <svg width="20" height="6">
        <line x1="0" y1="3" x2="20" y2="3" stroke={stroke} strokeWidth="1.5" strokeDasharray={dash} />
      </svg>
      <span>{label}</span>
    </span>
  );
}

function BranchRow({ t, mode, kind, next, cond, prob, first }) {
  const isCond = kind === "conditional";
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "100px 1.4fr 0.8fr 1fr",
      padding: "10px 14px", fontSize: "12px",
      borderTop: first ? "none" : `1px solid ${t.borderSoft}`,
      alignItems: "center",
    }}>
      <div>
        <Pill bg={isCond ? (mode === "dark" ? "rgba(245,158,11,0.12)" : "#FEF3C7") : t.bgSubtle}
              fg={isCond ? t.warn : t.textMid} mono={false}>
          {kind}
        </Pill>
      </div>
      <div style={{ color: t.text, fontWeight: 500 }}>→ {next}</div>
      <div style={{ color: isCond ? t.text : t.textDim, fontFamily: cond === "—" ? "inherit" : "'JetBrains Mono', monospace", fontSize: "11.5px" }}>{cond}</div>
      <div style={{ color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>{prob}</div>
    </div>
  );
}

window.VADetailDAG = VADetailDAG;
