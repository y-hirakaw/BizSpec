"""Backward-compat shim. 新規コードは ``bizspec.viz`` から import すること。

旧 ``bizspec.viz_cmd`` の公開シンボルをそのまま再エクスポートする。
- 内部詳細（``_topo_levels`` 等）も引き続き import 可能（テストが利用中）
- ``_load_units`` / ``_load_process_meta`` は ``bizspec.core.loader`` のエイリアス
"""

from __future__ import annotations

from .core.loader import (
    load_process_meta as _load_process_meta,
    load_units as _load_units,
)
from .viz.builder import (
    _generate_html,
    _generate_index_html,
    _process_stats,
    _unit_to_js,
)
from .viz.cmd import run_viz
from .viz.layout import (
    H_GAP,
    MIN_CANVAS_W,
    NODE_H,
    NODE_W,
    V_GAP,
    _build_edges,
    _compute_layout,
    _topo_levels,
)

__all__ = [
    "H_GAP",
    "MIN_CANVAS_W",
    "NODE_H",
    "NODE_W",
    "V_GAP",
    "_build_edges",
    "_compute_layout",
    "_generate_html",
    "_generate_index_html",
    "_load_process_meta",
    "_load_units",
    "_process_stats",
    "_topo_levels",
    "_unit_to_js",
    "run_viz",
]
