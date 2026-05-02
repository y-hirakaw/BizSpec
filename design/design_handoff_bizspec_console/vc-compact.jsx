/* Variant C — COMPACT POWER
   Higher density, sharper. Linear-style table with sortable feel,
   tighter rows, monospace-forward stats. Still warm enough for PdM. */

function VCIndex({ mode = "light" }) {
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
      background: t.bg, color: t.text, width: "100%", height: "100%",
      fontSize: "11.5px", display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      <div style={{ height: "38px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 12px", gap: "10px" }}>
        <div style={{ width: "18px", height: "18px", borderRadius: "4px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "10px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
        <span style={{ fontWeight: 600, fontSize: "12px" }}>{T("app.name")}</span>
        <span style={{ color: t.textDim }}>·</span>
        {[T("tab.overview"),T("tab.processes"),T("tab.heatmap"),T("tab.graph")].map((n,i)=>(
          <span key={n} style={{fontSize:"11px",color:i===0?t.text:t.textMid,fontWeight:i===0?600:400,padding:"2px 6px",borderRadius:"4px",background:i===0?t.bgSubtle:"transparent"}}>{n}</span>
        ))}
        <div style={{ flex: 1 }}></div>
        <div style={{ fontSize: "10.5px", padding: "2px 6px", background: t.bgSubtle, border: `1px solid ${t.border}`, borderRadius: "4px", color: t.textMid, fontFamily: "'JetBrains Mono', monospace" }}>⌘K</div>
      </div>

      {/* Stat strip */}
      <div style={{ display: "flex", borderBottom: `1px solid ${t.border}`, background: t.bgPanel }}>
        {[
          ["processes", data.processes.length],
          ["units", totalUnits],
          ["cost.h/mo", totalCost],
          ["script", data.processes.reduce((s,p)=>s+p.units.filter(u=>u.executor==="script").length,0)],
          ["ai_agent", data.processes.reduce((s,p)=>s+p.units.filter(u=>u.executor==="ai_agent").length,0)],
          ["manual", data.processes.reduce((s,p)=>s+p.units.filter(u=>u.executor==="manual").length,0)],
        ].map(([k,v],i)=>(
          <div key={k} style={{padding:"10px 16px",borderRight: i<5?`1px solid ${t.border}`:"none",flex:1}}>
            <div style={{fontSize:"9.5px",color:t.textDim,letterSpacing:"0.06em",textTransform:"uppercase"}}>{k}</div>
            <div style={{fontSize:"18px",fontWeight:700,fontFamily:"'JetBrains Mono', monospace",letterSpacing:"-0.02em"}}>{v}</div>
          </div>
        ))}
      </div>

      {/* Filter bar */}
      <div style={{ display:"flex",alignItems:"center",gap:"6px",padding:"6px 12px",borderBottom:`1px solid ${t.border}`,background:t.bgInset }}>
        <span style={{fontSize:"10px",color:t.textDim,letterSpacing:"0.06em",textTransform:"uppercase"}}>{T("filter.label")}</span>
        <Pill bg={t.bgPanel} fg={t.text}>{T("filter.coreAny")}</Pill>
        <Pill bg={t.bgPanel} fg={t.text}>{T("filter.executorAll")}</Pill>
        <Pill bg={t.bgPanel} fg={t.text}>{T("filter.phaseAll")}</Pill>
        <Pill bg={t.bgPanel} fg={t.text}>{T("filter.statusAll")}</Pill>
        <div style={{flex:1}}></div>
        <span style={{fontSize:"10.5px",color:t.textDim}}>{data.processes.length} rows · sorted by cost ↓</span>
      </div>

      {/* Big table */}
      <div style={{ flex: 1, overflow: "auto" }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "24px 1.6fr 0.6fr 0.5fr 1.7fr 1.4fr 0.6fr 0.6fr",
          padding: "6px 12px", fontSize: "9.5px",
          color: t.textDim, fontWeight: 600,
          letterSpacing: "0.06em", textTransform: "uppercase",
          borderBottom: `1px solid ${t.border}`, background: t.bgPanel,
          position: "sticky", top: 0, zIndex: 1,
        }}>
          <div></div><div>{T("th.name")}</div><div>{T("th.phase")}</div><div>{T("th.units")}</div><div>{T("th.executors")}</div><div>{T("th.cost")}</div><div style={{textAlign:"right"}}>{T("th.hpermo")}</div><div style={{textAlign:"right"}}>{T("th.auto")}</div>
        </div>
        {[...data.processes].sort((a,b)=>H.totalCost(b)-H.totalCost(a)).map((p,i)=>{
          const cost = H.totalCost(p);
          const ec = H.executorCounts(p);
          const ratio = cost / allMax;
          const ph = PHASE_COLOR[p.phase] || PHASE_COLOR.spec;
          const autoPct = Math.round((ec.script + ec.ai_agent) / p.units.length * 100);
          return (
            <div key={p.id} style={{
              display: "grid",
              gridTemplateColumns: "24px 1.6fr 0.6fr 0.5fr 1.7fr 1.4fr 0.6fr 0.6fr",
              padding: "6px 12px", fontSize: "11.5px",
              borderBottom: `1px solid ${t.borderSoft}`,
              alignItems: "center",
              background: i % 2 === 0 ? t.bg : t.bgInset,
            }}>
              <div style={{fontFamily:"'JetBrains Mono', monospace",fontSize:"10px",color:t.textDim}}>{String(i+1).padStart(2,"0")}</div>
              <div style={{color:t.text,fontWeight:500}}>{p.name}</div>
              <div><Pill bg={ph.bg} fg={ph.fg} mono={false}>{p.phase}</Pill></div>
              <div style={{fontFamily:"'JetBrains Mono', monospace",color:t.textMid}}>{p.units.length}</div>
              <div style={{display:"flex",gap:"3px"}}>
                {ec.script > 0 && <Pill bg={exTone(mode,"script").bg} fg={exTone(mode,"script").fg}>s·{ec.script}</Pill>}
                {ec.ai_agent > 0 && <Pill bg={exTone(mode,"ai_agent").bg} fg={exTone(mode,"ai_agent").fg}>ai·{ec.ai_agent}</Pill>}
                {ec.manual > 0 && <Pill bg={exTone(mode,"manual").bg} fg={exTone(mode,"manual").fg}>m·{ec.manual}</Pill>}
              </div>
              <div style={{display:"flex",alignItems:"center",gap:"6px"}}>
                <div style={{flex:1,maxWidth:"120px",height:"4px",background:t.bgSubtle,borderRadius:"1px",overflow:"hidden"}}>
                  <div style={{width:(ratio*100)+"%",height:"100%",background:ratio>0.66?t.danger:ratio>0.33?t.warn:t.accent}}></div>
                </div>
              </div>
              <div style={{textAlign:"right",fontFamily:"'JetBrains Mono', monospace",fontWeight:600}}>{cost}</div>
              <div style={{textAlign:"right",fontFamily:"'JetBrains Mono', monospace",color:t.textMid}}>{autoPct}%</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function VCDetail({ mode = "light" }) {
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
      fontSize: "11.5px", display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      <div style={{ height: "38px", borderBottom: `1px solid ${t.border}`, background: t.bgPanel, display: "flex", alignItems: "center", padding: "0 12px", gap: "10px" }}>
        <div style={{ width: "18px", height: "18px", borderRadius: "4px", background: t.accent, color: "#FFF", fontWeight: 700, fontSize: "10px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace" }}>B</div>
        <span style={{fontWeight:600}}>{T("app.name")}</span>
        <span style={{color:t.textDim}}>/</span>
        <span style={{color:t.textMid}}>api-design</span>
        <span style={{color:t.textDim}}>/</span>
        <span style={{fontWeight:500}}>{T("sample.api.title")}</span>
        <div style={{flex:1}}></div>
        <button style={{fontSize:"10.5px",padding:"3px 8px",border:`1px solid ${t.border}`,background:t.bgPanel,borderRadius:"4px",color:t.textMid,cursor:"pointer",fontFamily:"inherit"}}>{T("unit.prev")}</button>
        <button style={{fontSize:"10.5px",padding:"3px 8px",border:`1px solid ${t.border}`,background:t.bgPanel,borderRadius:"4px",color:t.textMid,cursor:"pointer",fontFamily:"inherit"}}>{T("unit.next")}</button>
      </div>

      <div style={{flex:1,display:"flex",overflow:"hidden"}}>
        {/* compact left rail */}
        <div style={{width:"230px",borderRight:`1px solid ${t.border}`,background:t.bgPanel,padding:"8px 6px",overflow:"auto"}}>
          <div style={{padding:"4px 8px 6px",display:"flex",alignItems:"baseline",justifyContent:"space-between"}}>
            <span style={{fontSize:"11.5px",fontWeight:600}}>api-design</span>
            <span style={{fontSize:"9.5px",color:t.textDim,fontFamily:"'JetBrains Mono', monospace"}}>{H.totalCost(proc)}h</span>
          </div>
          {proc.units.map((u,i)=>{
            const sel = u.name === selected.name;
            const cost = H.cost(u);
            const ex = exTone(mode,u.executor);
            return (
              <div key={u.name} style={{
                padding:"5px 8px",fontSize:"11px",
                background:sel?t.accentBg:"transparent",
                borderLeft:`2px solid ${sel?t.accent:"transparent"}`,
                marginLeft:"-2px",
                display:"grid",gridTemplateColumns:"18px 1fr auto auto",gap:"6px",alignItems:"center",
                marginBottom:"1px",
              }}>
                <span style={{fontSize:"9.5px",color:t.textDim,fontFamily:"'JetBrains Mono', monospace"}}>{String(i+1).padStart(2,"0")}</span>
                <span style={{color:sel?t.accent:t.text,fontWeight:sel?600:400}}>{sel ? T("sample.api.title") : u.name}</span>
                <Pill bg={ex.bg} fg={ex.fg}>{u.executor==="ai_agent"?"ai":u.executor[0]}</Pill>
                <span style={{fontSize:"9.5px",color:t.textMid,fontFamily:"'JetBrains Mono', monospace"}}>{cost}h</span>
              </div>
            );
          })}
        </div>

        {/* Main */}
        <div style={{flex:1,overflow:"auto",padding:"16px 20px"}}>
          {/* Compact header */}
          <div style={{display:"flex",alignItems:"center",gap:"8px",marginBottom:"4px"}}>
            <span style={{fontSize:"10px",color:t.textDim,fontFamily:"'JetBrains Mono', monospace",letterSpacing:"0.04em"}}>UNIT 05 / 05</span>
            <Pill bg={exTone(mode,"script").bg} fg={exTone(mode,"script").fg}>script</Pill>
            <Pill bg={mode==="dark"?"rgba(245,158,11,0.12)":"#FEF3C7"} fg={t.warn}>review</Pill>
            <Pill bg={t.bgSubtle} fg={t.textMid} mono={false}>core·false</Pill>
          </div>
          <h1 style={{fontSize:"22px",fontWeight:700,letterSpacing:"-0.02em",margin:"0 0 4px"}}>{T("sample.api.title")}</h1>
          <div style={{fontSize:"12.5px",color:t.textMid,marginBottom:"14px",lineHeight:1.55,maxWidth:"640px"}}>
            {T("sample.api.desc")}
          </div>

          {/* tight metric strip */}
          <div style={{display:"grid",gridTemplateColumns:"repeat(6,1fr)",border:`1px solid ${t.border}`,borderRadius:"6px",overflow:"hidden",marginBottom:"14px",background:t.bgPanel}}>
            {[["effort","1h"],["freq","2/mo"],["cost","2h/mo"],["lev","1.0"],["diff","low"],["status","auto"]].map(([k,v],i)=>(
              <div key={k} style={{padding:"8px 10px",borderRight:i<5?`1px solid ${t.borderSoft}`:"none"}}>
                <div style={{fontSize:"9.5px",color:t.textDim,letterSpacing:"0.06em",textTransform:"uppercase",marginBottom:"2px"}}>{k}</div>
                <div style={{fontSize:"14px",fontWeight:700,fontFamily:"'JetBrains Mono', monospace"}}>{v}</div>
              </div>
            ))}
          </div>

          {/* IO compact table */}
          <div style={{background:t.bgPanel,border:`1px solid ${t.border}`,borderRadius:"6px",overflow:"hidden",marginBottom:"12px"}}>
            <div style={{padding:"6px 12px",fontSize:"9.5px",color:t.textDim,letterSpacing:"0.06em",textTransform:"uppercase",borderBottom:`1px solid ${t.border}`,background:t.bgInset,fontWeight:600}}>io · in / process / out</div>
            {[[T("unit.io.in"),[T("sample.api.in1")],t.accent],[T("unit.io.process"),[T("sample.api.proc1"),T("sample.api.proc2")],t.purple],[T("unit.io.out"),[T("sample.api.out1"),T("sample.api.out2")],t.ok]].map(([label,items,c],i)=>(
              <div key={label} style={{display:"grid",gridTemplateColumns:"80px 1fr",borderTop:i>0?`1px solid ${t.borderSoft}`:"none"}}>
                <div style={{padding:"8px 12px",fontSize:"10px",fontWeight:700,color:c,letterSpacing:"0.08em",borderRight:`1px solid ${t.borderSoft}`}}>{label}</div>
                <div style={{padding:"6px 12px"}}>
                  {items.map((it,j)=><div key={j} style={{fontSize:"12px",padding:"2px 0"}}>{it}</div>)}
                </div>
              </div>
            ))}
          </div>

          {/* Two-col compact */}
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"8px"}}>
            <div style={{background:t.bgPanel,border:`1px solid ${t.border}`,borderRadius:"6px",padding:"10px 12px"}}>
              <div style={{fontSize:"9.5px",fontWeight:700,color:t.textMid,letterSpacing:"0.08em",textTransform:"uppercase",marginBottom:"6px"}}>{T("unit.scopeRule")}</div>
              <ul style={{listStyle:"none",margin:0,padding:0,fontSize:"12px",lineHeight:1.6}}>
                <li style={{paddingLeft:"12px",position:"relative",marginBottom:"3px"}}><span style={{position:"absolute",left:0,color:t.accent}}>›</span>{T("sample.api.scope1")}</li>
                <li style={{paddingLeft:"12px",position:"relative",marginBottom:"3px"}}><span style={{position:"absolute",left:0,color:t.accent}}>›</span>{T("sample.api.scope2")}</li>
                <li style={{paddingLeft:"12px",position:"relative",marginBottom:"3px",color:t.text}}><span style={{position:"absolute",left:0,color:t.warn}}>!</span>{T("sample.api.rule1")}</li>
                <li style={{paddingLeft:"12px",position:"relative",color:t.text}}><span style={{position:"absolute",left:0,color:t.warn}}>!</span>{T("sample.api.rule2")}</li>
              </ul>
            </div>
            <div style={{background:t.bgPanel,border:`1px solid ${t.border}`,borderRadius:"6px",padding:"10px 12px"}}>
              <div style={{fontSize:"9.5px",fontWeight:700,color:t.textMid,letterSpacing:"0.08em",textTransform:"uppercase",marginBottom:"6px"}}>{T("unit.executorLinks")}</div>
              <div style={{fontSize:"12px",marginBottom:"8px"}}>
                <Pill bg={exTone(mode,"script").bg} fg={exTone(mode,"script").fg} padding="2px 7px">script</Pill>
                <span style={{color:t.textMid,marginLeft:"6px"}}>{T("exec.scriptAutomatable")}</span>
              </div>
              <div style={{display:"grid",gridTemplateColumns:"40px 1fr",gap:"4px 8px",fontSize:"11.5px",alignItems:"center"}}>
                <span style={{color:t.textDim,fontSize:"9.5px",letterSpacing:"0.06em"}}>{T("unit.up")}</span>
                <span style={{padding:"2px 7px",border:`1px solid ${t.border}`,borderRadius:"4px",background:t.bgInset,color:t.text,display:"inline-block",justifySelf:"start"}}>{T("sample.api.upstream")}</span>
                <span style={{color:t.textDim,fontSize:"9.5px",letterSpacing:"0.06em"}}>{T("unit.down")}</span>
                <span style={{color:t.textDim}}>—</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

window.VCIndex = VCIndex;
window.VCDetail = VCDetail;
