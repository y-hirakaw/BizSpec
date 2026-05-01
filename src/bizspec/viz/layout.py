"""フロー図のレイアウト計算（純関数）。

DAG をレベル分けし、各ノードの座標とエッジを返す。HTML 生成からは独立しており、
依存はゼロ（Python 標準ライブラリのみ）。
"""

from __future__ import annotations


NODE_W = 200
NODE_H = 54
H_GAP = 20
V_GAP = 56
MIN_CANVAS_W = 280


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
    """Return edges as [from, to, type]. type: 'seq' | 'parallel'."""
    edges: list[list[str]] = []
    seen: set[tuple[str, str]] = set()
    for u in units:
        src = str(u.get("unit", ""))
        if src not in positions:
            continue
        for down in (u.get("link") or {}).get("down") or []:
            if isinstance(down, str) and down in positions and (src, down) not in seen:
                edges.append([src, down, "seq"])
                seen.add((src, down))
        exe = u.get("execution") or {}
        for par in (exe.get("parallel_with") or []):
            if isinstance(par, str) and par in positions:
                key = (min(src, par), max(src, par))
                if key not in seen:
                    edges.append([src, par, "parallel"])
                    seen.add(key)
    return edges
