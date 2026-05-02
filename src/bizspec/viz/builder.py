"""HTML 組み立て。

unit 辞書を JS 用 JSON に整形し、外部 HTML テンプレ（``templates/*.html``）を
``importlib.resources`` 経由で読み込んでプレースホルダ置換する。
"""

from __future__ import annotations

import json
from importlib.resources import files

from ..core.config import DEFAULT_CONFIG
from .layout import _topo_levels, _compute_layout, _build_edges


# テンプレはモジュール初回 import 時に一度だけ読む（プロセス内キャッシュ）
_TEMPLATE_PROCESS = (files(__package__) / "templates" / "process.html").read_text(encoding="utf-8")
_TEMPLATE_INDEX = (files(__package__) / "templates" / "index.html").read_text(encoding="utf-8")


def _unit_to_js(u: dict) -> dict:
    def lst(v: object) -> list[str]:
        return [str(x) for x in v] if isinstance(v, list) else []

    def opt_str(v: object) -> str | None:
        return str(v) if v is not None else None

    io   = u.get("io")   or {}; io   = io   if isinstance(io,   dict) else {}
    link = u.get("link") or {}; link = link if isinstance(link, dict) else {}
    exe  = u.get("executor")   or {}; exe = exe if isinstance(exe,  dict) else {}
    eff  = u.get("effort")     or {}; eff = eff if isinstance(eff,  dict) else {}
    aut  = u.get("automation") or {}; aut = aut if isinstance(aut,  dict) else {}

    def opt_num(v: object) -> int | float | None:
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    dur  = opt_num(eff.get("duration"))
    freq = opt_num(eff.get("frequency"))
    return {
        "aim":      str(u.get("aim", "")),
        "phase":    str(u.get("phase", "")),
        "core":     u.get("core"),
        "scope":    lst(u.get("scope")),
        "rule":     lst(u.get("rule")),
        "io":       {"in": lst(io.get("in")), "process": lst(io.get("process")), "out": lst(io.get("out"))},
        "executor": {"type": str(exe.get("type", "")), "reason": str(exe.get("reason", ""))},
        "link":       {"up": lst(link.get("up")), "down": lst(link.get("down"))},
        "depends_on": lst(u.get("depends_on")),
        "effort":   {"duration": dur, "frequency": freq},
        "automation": {
            "difficulty": opt_str(aut.get("difficulty")),
            "status":     opt_str(aut.get("status")),
        },
        "lifecycle_status":     opt_str(u.get("status")),
        "deprecated_reason":    opt_str(u.get("deprecated_reason")),
        "parallel_with":        lst((u.get("execution") or {}).get("parallel_with")),
    }


def _process_stats(units: list[dict]) -> dict:
    phases = sorted({str(u.get("phase", "")) for u in units if u.get("phase")})
    exe: dict[str, int] = {"script": 0, "ai_agent": 0, "manual": 0}
    core_count = 0
    for u in units:
        t = (u.get("executor") or {}).get("type", "")
        if t in exe:
            exe[t] += 1
        if u.get("core") is True:
            core_count += 1
    return {"unit_count": len(units), "phases": phases, "executor": exe, "core_count": core_count}


def _generate_html(
    process_name: str,
    units: list[dict],
    display_name: str | None = None,
    config: dict | None = None,
) -> str:
    if not units:
        return ""

    levels = _topo_levels(units)
    positions, canvas_w, canvas_h = _compute_layout(levels)
    edges = _build_edges(units, positions)

    units_js = {str(u["unit"]): _unit_to_js(u) for u in units if u.get("unit")}
    phases = sorted({str(u.get("phase", "")) for u in units if u.get("phase")})
    phase_str = " &nbsp;·&nbsp; phase: " + " · ".join(phases) if phases else ""

    title = display_name or process_name
    if display_name and display_name != process_name:
        subtitle = f"{process_name} &nbsp;·&nbsp; {len(units)} units{phase_str}"
    else:
        subtitle = f"{len(units)} units{phase_str}"

    cfg = config if config is not None else DEFAULT_CONFIG
    units_json     = json.dumps(units_js,   ensure_ascii=False, indent=2)
    positions_json = json.dumps(positions,  ensure_ascii=False)
    edges_json     = json.dumps(edges,      ensure_ascii=False)
    config_json    = json.dumps(cfg,        ensure_ascii=False)

    html = _TEMPLATE_PROCESS
    html = html.replace("__PROCESS_NAME__", title)
    html = html.replace("__SUBTITLE__",     subtitle)
    html = html.replace("__CANVAS_W__",     str(canvas_w))
    html = html.replace("__CANVAS_H__",     str(canvas_h))
    html = html.replace("__UNITS_JSON__",   units_json)
    html = html.replace("__POSITIONS_JSON__", positions_json)
    html = html.replace("__EDGES_JSON__",   edges_json)
    html = html.replace("__VIZ_CONFIG_JSON__", config_json)
    return html


def _generate_index_html(
    processes: dict[str, list[dict]],
    display_names: dict[str, str] | None = None,
    config: dict | None = None,
) -> str:
    all_data: dict[str, dict] = {}
    for name, units in processes.items():
        if not units:
            continue
        levels = _topo_levels(units)
        positions, canvas_w, canvas_h = _compute_layout(levels)
        edges = _build_edges(units, positions)
        units_js = {str(u["unit"]): _unit_to_js(u) for u in units if u.get("unit")}
        dn = (display_names or {}).get(name)
        all_data[name] = {
            "displayName": dn if dn and dn != name else None,
            "units":     units_js,
            "positions": positions,
            "edges":     edges,
            "canvasW":   canvas_w,
            "canvasH":   canvas_h,
            "stats":     _process_stats(units),
        }

    if not all_data:
        return ""

    cross_edges: list[dict] = []
    seen_cross: set[tuple[str, str]] = set()
    for to_proc, units in processes.items():
        for u in units:
            for dep in (u.get("depends_on") or []):
                dep_str = str(dep)
                if ":" not in dep_str:
                    continue
                from_proc = dep_str.split(":")[0]
                if from_proc == to_proc or from_proc not in all_data:
                    continue
                key = (from_proc, to_proc)
                if key not in seen_cross:
                    seen_cross.add(key)
                    cross_edges.append({"from": from_proc, "to": to_proc})

    cfg = config if config is not None else DEFAULT_CONFIG
    all_data_json = json.dumps(all_data, ensure_ascii=False, indent=2)
    cross_edges_json = json.dumps(cross_edges, ensure_ascii=False)
    config_json = json.dumps(cfg, ensure_ascii=False)
    return (_TEMPLATE_INDEX
        .replace("__ALL_DATA_JSON__", all_data_json)
        .replace("__CROSS_EDGES_JSON__", cross_edges_json)
        .replace("__VIZ_CONFIG_JSON__", config_json))
