from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


NODE_W = 200
NODE_H = 54
H_GAP  = 20
V_GAP  = 56
MIN_CANVAS_W = 280


def _load_units(process_dir: Path) -> list[dict]:
    units = []
    for path in sorted(process_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                units.append(data)
        except Exception:
            pass
    return units


def _topo_levels(units: list[dict]) -> list[list[str]]:
    """Assign each unit to a DAG level via Kahn's algorithm."""
    names = {str(u["unit"]) for u in units if u.get("unit")}
    in_deg: dict[str, int] = {n: 0 for n in names}
    children: dict[str, list[str]] = {n: [] for n in names}

    for u in units:
        src = str(u.get("unit", ""))
        if src not in names:
            continue
        for down in (u.get("link") or {}).get("down") or []:
            if isinstance(down, str) and down in names:
                children[src].append(down)
                in_deg[down] += 1

    queue = sorted(n for n, d in in_deg.items() if d == 0)
    levels: list[list[str]] = []
    while queue:
        levels.append(queue)
        nxt: list[str] = []
        for n in queue:
            for c in children[n]:
                in_deg[c] -= 1
                if in_deg[c] == 0:
                    nxt.append(c)
        queue = sorted(nxt)

    remaining = sorted(n for n, d in in_deg.items() if d > 0)
    if remaining:
        levels.append(remaining)

    return levels


def _compute_layout(levels: list[list[str]]) -> tuple[dict[str, dict], int, int]:
    """Return (positions, canvas_w, canvas_h). Nodes are centered per level."""
    max_count = max(len(lvl) for lvl in levels) if levels else 1
    canvas_w = max(max_count * NODE_W + (max_count - 1) * H_GAP, MIN_CANVAS_W)

    positions: dict[str, dict] = {}
    y = 24
    for level in levels:
        count = len(level)
        total_w = count * NODE_W + (count - 1) * H_GAP
        start_x = (canvas_w - total_w) // 2
        for i, name in enumerate(level):
            positions[name] = {"left": start_x + i * (NODE_W + H_GAP), "top": y}
        y += NODE_H + V_GAP

    canvas_h = y - V_GAP + 24
    return positions, canvas_w, canvas_h


def _build_edges(units: list[dict], positions: dict[str, dict]) -> list[list[str]]:
    edges: list[list[str]] = []
    seen: set[tuple[str, str]] = set()
    for u in units:
        src = str(u.get("unit", ""))
        if src not in positions:
            continue
        for down in (u.get("link") or {}).get("down") or []:
            if isinstance(down, str) and down in positions and (src, down) not in seen:
                edges.append([src, down])
                seen.add((src, down))
    return edges


def _unit_to_js(u: dict) -> dict:
    def lst(v: object) -> list[str]:
        return [str(x) for x in v] if isinstance(v, list) else []

    io   = u.get("io")   or {}; io   = io   if isinstance(io,   dict) else {}
    link = u.get("link") or {}; link = link if isinstance(link, dict) else {}
    exe  = u.get("executor") or {}; exe = exe if isinstance(exe, dict) else {}

    return {
        "aim":      str(u.get("aim", "")),
        "phase":    str(u.get("phase", "")),
        "core":     u.get("core"),
        "job":      lst(u.get("job")),
        "rule":     lst(u.get("rule")),
        "io":       {"in": lst(io.get("in")), "run": lst(io.get("run")), "out": lst(io.get("out"))},
        "executor": {"type": str(exe.get("type", "")), "reason": str(exe.get("reason", ""))},
        "link":     {"up": lst(link.get("up")), "down": lst(link.get("down"))},
    }


def _generate_html(process_name: str, units: list[dict]) -> str:
    if not units:
        return ""

    levels = _topo_levels(units)
    positions, canvas_w, canvas_h = _compute_layout(levels)
    edges = _build_edges(units, positions)

    units_js = {str(u["unit"]): _unit_to_js(u) for u in units if u.get("unit")}
    phases = sorted({str(u.get("phase", "")) for u in units if u.get("phase")})
    phase_str = " &nbsp;·&nbsp; phase: " + " · ".join(phases) if phases else ""
    subtitle = f"{len(units)} units{phase_str}"

    units_json     = json.dumps(units_js,   ensure_ascii=False, indent=2)
    positions_json = json.dumps(positions,  ensure_ascii=False)
    edges_json     = json.dumps(edges,      ensure_ascii=False)

    html = _HTML_TEMPLATE
    html = html.replace("__PROCESS_NAME__", process_name)
    html = html.replace("__SUBTITLE__",     subtitle)
    html = html.replace("__CANVAS_W__",     str(canvas_w))
    html = html.replace("__CANVAS_H__",     str(canvas_h))
    html = html.replace("__UNITS_JSON__",   units_json)
    html = html.replace("__POSITIONS_JSON__", positions_json)
    html = html.replace("__EDGES_JSON__",   edges_json)
    return html


def run_viz(args) -> int:
    root = Path(args.root).resolve()
    bizspec_dir = root / "bizspec"

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    if getattr(args, "process", None):
        process_dirs = [bizspec_dir / args.process]
        if not process_dirs[0].is_dir():
            print(f"ERROR: プロセス '{args.process}' が見つかりません", file=sys.stderr)
            return 1
    else:
        process_dirs = sorted(
            d for d in bizspec_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        )

    out_dir = bizspec_dir / "_viz"
    out_dir.mkdir(exist_ok=True)

    generated = 0
    for process_dir in process_dirs:
        units = _load_units(process_dir)
        if not units:
            continue
        html = _generate_html(process_dir.name, units)
        if not html:
            continue
        out_path = out_dir / f"{process_dir.name}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"  {out_path.relative_to(root)}")
        generated += 1

    if generated == 0:
        print("WARNING: 出力された HTML はありません", file=sys.stderr)
        return 1

    return 0


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__PROCESS_NAME__ フロー | BizSpec</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic UI", sans-serif;
  font-size: 14px;
  background: #F9FAFB;
  color: #111827;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  height: 50px;
  background: #fff;
  border-bottom: 1px solid #E5E7EB;
  z-index: 10;
}
header h1 { font-size: 16px; font-weight: 700; }
header .subtitle { font-size: 12px; color: #6B7280; }

.legend-bar {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 6px 20px;
  background: #fff;
  border-bottom: 1px solid #F3F4F6;
  font-size: 11px;
  color: #6B7280;
}
.legend-item { display: flex; align-items: center; gap: 5px; }
.lswatch { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
.lpill {
  height: 14px; padding: 0 6px; border-radius: 999px;
  font-size: 10px; font-weight: 500; display: flex; align-items: center;
}

.layout { flex: 1 1 0; display: flex; min-height: 0; }

.flow-area {
  flex: 0 0 auto;
  min-width: 320px;
  max-width: 60vw;
  overflow-y: auto;
  overflow-x: auto;
  background: #F8FAFC;
  border-right: 1px solid #E5E7EB;
  padding: 24px 20px 40px;
}
.flow-canvas {
  position: relative;
  width: __CANVAS_W__px;
  height: __CANVAS_H__px;
}
svg.arrows-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
}

.node {
  position: absolute;
  width: 200px;
  height: 54px;
  border-radius: 8px;
  padding: 7px 11px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  transition: box-shadow 0.15s ease, transform 0.1s ease;
  user-select: none;
}
.node:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.13); transform: translateY(-1px); }
.node.selected { box-shadow: 0 0 0 3px #2563EB, 0 4px 14px rgba(37,99,235,0.18); }
.node.core-true  { background: #EFF6FF; border: 2px solid #93C5FD; }
.node.core-false { background: #F9FAFB; border: 2px solid #D1D5DB; }

.node-name { font-size: 11px; font-weight: 600; color: #111827; line-height: 1.35; white-space: normal; }
.node-badges { display: flex; gap: 4px; align-items: center; }
.badge { font-size: 9px; font-weight: 600; padding: 1px 5px; border-radius: 999px; white-space: nowrap; line-height: 1.5; }
.badge-script   { background: #D1FAE5; color: #065F46; }
.badge-ai_agent { background: #EDE9FE; color: #5B21B6; }
.badge-manual   { background: #FEF3C7; color: #92400E; }
.badge-core     { background: #DBEAFE; color: #1D4ED8; }

.detail-panel {
  flex: 1 1 0;
  overflow-y: auto;
  padding: 24px 28px;
  background: #fff;
  min-width: 0;
}
.detail-empty {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9CA3AF;
  font-size: 14px;
}

.detail-header { padding-bottom: 16px; margin-bottom: 18px; border-bottom: 1px solid #F3F4F6; }
.detail-unit-name { font-size: 20px; font-weight: 700; line-height: 1.3; margin-bottom: 6px; word-break: break-all; }
.detail-aim { font-size: 13px; color: #4B5563; line-height: 1.75; margin-bottom: 10px; }
.detail-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.tag { font-size: 11px; font-weight: 500; padding: 2px 9px; border-radius: 999px; }
.tag-phase      { background: #ECFDF5; color: #065F46; }
.tag-core-true  { background: #DBEAFE; color: #1D4ED8; }
.tag-core-false { background: #F3F4F6; color: #6B7280; }
.tag-script     { background: #D1FAE5; color: #065F46; }
.tag-ai_agent   { background: #EDE9FE; color: #5B21B6; }
.tag-manual     { background: #FEF3C7; color: #92400E; }

.section { margin-bottom: 18px; }
.section-label {
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.07em;
  color: #9CA3AF; margin-bottom: 7px;
}
.item-list { list-style: none; padding: 0; font-size: 13px; color: #374151; line-height: 1.75; }
.item-list li { padding-left: 14px; position: relative; }
.item-list li::before { content: "·"; position: absolute; left: 0; color: #9CA3AF; font-size: 18px; line-height: 1.35; }

.io-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.io-box { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; padding: 10px; }
.io-box-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px; }
.io-box-in  .io-box-label { color: #0284C7; }
.io-box-run .io-box-label { color: #7C3AED; }
.io-box-out .io-box-label { color: #059669; }
.io-box ul { list-style: none; padding: 0; font-size: 11px; color: #4B5563; line-height: 1.65; }
.io-box ul li { padding-left: 8px; position: relative; }
.io-box ul li::before { content: "·"; position: absolute; left: 0; color: #9CA3AF; }

.executor-box { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; padding: 10px 12px; }
.executor-reason { font-size: 12px; color: #6B7280; margin-top: 5px; line-height: 1.65; }

.link-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.link-chip {
  font-size: 11px; padding: 3px 10px; border-radius: 999px;
  background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;
  cursor: pointer; transition: background 0.1s;
}
.link-chip:hover { background: #DBEAFE; }
.link-empty { font-size: 12px; color: #D1D5DB; font-style: italic; }
</style>
</head>
<body>

<header>
  <h1>__PROCESS_NAME__</h1>
  <span class="subtitle">__SUBTITLE__</span>
</header>

<div class="legend-bar">
  <div class="legend-item">
    <div class="lswatch" style="background:#EFF6FF;border:2px solid #93C5FD;"></div>
    core: true
  </div>
  <div class="legend-item">
    <div class="lswatch" style="background:#F9FAFB;border:2px solid #D1D5DB;"></div>
    core: false
  </div>
  <div class="legend-item">
    <div class="lpill" style="background:#D1FAE5;color:#065F46;">script</div>
  </div>
  <div class="legend-item">
    <div class="lpill" style="background:#EDE9FE;color:#5B21B6;">ai_agent</div>
  </div>
  <div class="legend-item">
    <div class="lpill" style="background:#FEF3C7;color:#92400E;">manual</div>
  </div>
</div>

<div class="layout">
  <div class="flow-area">
    <div class="flow-canvas" id="canvas"></div>
  </div>
  <div class="detail-panel" id="detail-panel">
    <div class="detail-empty">ノードをクリックして詳細を表示</div>
  </div>
</div>

<script>
const units     = __UNITS_JSON__;
const positions = __POSITIONS_JSON__;
const edges     = __EDGES_JSON__;

const W = 200, H = 54;
const canvas     = document.getElementById("canvas");
const detailPane = document.getElementById("detail-panel");

// ── SVG arrows ──────────────────────────────────────────
const NS  = "http://www.w3.org/2000/svg";
const svg = document.createElementNS(NS, "svg");
svg.classList.add("arrows-layer");
svg.setAttribute("viewBox", "0 0 __CANVAS_W__ __CANVAS_H__");

const defs   = document.createElementNS(NS, "defs");
const marker = document.createElementNS(NS, "marker");
Object.entries({
  id: "arrowhead", markerWidth: "9", markerHeight: "7",
  refX: "8", refY: "3.5", orient: "auto"
}).forEach(([k,v]) => marker.setAttribute(k, v));
const poly = document.createElementNS(NS, "polygon");
poly.setAttribute("points", "0 0, 9 3.5, 0 7");
poly.setAttribute("fill", "#94A3B8");
marker.appendChild(poly);
defs.appendChild(marker);
const markerSkip = document.createElementNS(NS, "marker");
Object.entries({
  id: "arrowhead-skip", markerWidth: "9", markerHeight: "7",
  refX: "8", refY: "3.5", orient: "auto"
}).forEach(([k,v]) => markerSkip.setAttribute(k, v));
const polySkip = document.createElementNS(NS, "polygon");
polySkip.setAttribute("points", "0 0, 9 3.5, 0 7");
polySkip.setAttribute("fill", "#F59E0B");
markerSkip.appendChild(polySkip);
defs.appendChild(markerSkip);
svg.appendChild(defs);

edges.forEach(([from, to]) => {
  const fp = positions[from], tp = positions[to];
  const fx = fp.left + W / 2, fy = fp.top + H;
  const tx = tp.left + W / 2, ty = tp.top;
  const path = document.createElementNS(NS, "path");
  let d;
  const sameCol = Math.abs(fx - tx) < 2;
  const isSkip  = sameCol && (ty - fy) > 100;
  if (sameCol && !isSkip) {
    d = `M ${fx} ${fy} L ${tx} ${ty - 1}`;
  } else if (isSkip) {
    const ox = fp.left - 40;
    d = `M ${fx} ${fy} C ${ox} ${fy + 20} ${ox} ${ty - 20} ${tx} ${ty - 1}`;
  } else {
    const my = (fy + ty) / 2;
    d = `M ${fx} ${fy} C ${fx} ${my} ${tx} ${my} ${tx} ${ty - 1}`;
  }
  path.setAttribute("d", d);
  path.setAttribute("stroke", isSkip ? "#F59E0B" : "#94A3B8");
  path.setAttribute("stroke-width", isSkip ? "1.5" : "1.5");
  path.setAttribute("stroke-dasharray", isSkip ? "5 3" : "none");
  path.setAttribute("fill", "none");
  path.setAttribute("marker-end", isSkip ? "url(#arrowhead-skip)" : "url(#arrowhead)");
  svg.appendChild(path);
});

canvas.appendChild(svg);

// ── Nodes ────────────────────────────────────────────────
Object.entries(positions).forEach(([name, pos]) => {
  const u   = units[name];
  if (!u) return;
  const div = document.createElement("div");
  div.className    = `node core-${u.core}`;
  div.style.left   = pos.left + "px";
  div.style.top    = pos.top  + "px";
  div.dataset.name = name;

  div.innerHTML = `
    <div class="node-name">${name}</div>
    <div class="node-badges">
      <span class="badge badge-${u.executor.type}">${u.executor.type}</span>
      ${u.core ? '<span class="badge badge-core">core</span>' : ''}
    </div>`;

  div.addEventListener("click", () => {
    document.querySelectorAll(".node.selected").forEach(n => n.classList.remove("selected"));
    div.classList.add("selected");
    renderDetail(name);
  });

  canvas.appendChild(div);
});

// ── Detail panel ─────────────────────────────────────────
function renderDetail(name) {
  const u = units[name];
  const chips = (arr) =>
    arr.length
      ? arr.map(n => `<span class="link-chip" onclick="jumpTo('${n.replace(/'/g, "\\'")}')">${n}</span>`).join("")
      : `<span class="link-empty">なし</span>`;

  detailPane.innerHTML = `
    <div class="detail-header">
      <div class="detail-unit-name">${name}</div>
      <div class="detail-aim">${u.aim}</div>
      <div class="detail-tags">
        <span class="tag tag-phase">phase: ${u.phase}</span>
        <span class="tag tag-core-${u.core}">core: ${u.core}</span>
        <span class="tag tag-${u.executor.type}">${u.executor.type}</span>
      </div>
    </div>

    <div class="section">
      <div class="section-label">Job</div>
      <ul class="item-list">${u.job.map(j => `<li>${j}</li>`).join("")}</ul>
    </div>

    <div class="section">
      <div class="section-label">Rule</div>
      <ul class="item-list">${u.rule.map(r => `<li>${r}</li>`).join("")}</ul>
    </div>

    <div class="section">
      <div class="section-label">IO</div>
      <div class="io-grid">
        <div class="io-box io-box-in">
          <div class="io-box-label">In</div>
          <ul>${u.io.in.map(i => `<li>${i}</li>`).join("")}</ul>
        </div>
        <div class="io-box io-box-run">
          <div class="io-box-label">Run</div>
          <ul>${u.io.run.map(r => `<li>${r}</li>`).join("")}</ul>
        </div>
        <div class="io-box io-box-out">
          <div class="io-box-label">Out</div>
          <ul>${u.io.out.map(o => `<li>${o}</li>`).join("")}</ul>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-label">Executor</div>
      <div class="executor-box">
        <span class="badge badge-${u.executor.type}" style="font-size:11px;padding:2px 8px;">${u.executor.type}</span>
        <div class="executor-reason">${u.executor.reason}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-label">Link · Up</div>
      <div class="link-chips">${chips(u.link.up)}</div>
    </div>
    <div class="section">
      <div class="section-label">Link · Down</div>
      <div class="link-chips">${chips(u.link.down)}</div>
    </div>`;
}

function jumpTo(name) {
  const el = document.querySelector(`.node[data-name="${CSS.escape(name)}"]`);
  if (!el) return;
  document.querySelectorAll(".node.selected").forEach(n => n.classList.remove("selected"));
  el.classList.add("selected");
  renderDetail(name);
  el.scrollIntoView({ behavior: "smooth", block: "center" });
}
</script>
</body>
</html>
"""
