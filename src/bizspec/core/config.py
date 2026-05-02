"""BizSpec プロジェクト設定 (`bizspec/config.yaml`) のローダ。

ユーザは config.yaml に書いた値だけを上書きできる（deep-merge）。
未指定キーは ``DEFAULT_CONFIG`` から補完される。
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml


DEFAULT_CONFIG: dict = {
    "viz": {
        "heatmap": {
            # heatmap の cost X 軸を fixed モードに切り替えたときに使う 3 個の境界
            # (h/月、昇順)。relative/fixed のモード切替は HTML 上のトグルで行う。
            # 例: [1, 4, 20] → ≤1h / 1<x≤4 / 4<x≤20 / >20 の 4 列
            "cost_thresholds": [1, 4, 20],
        },
    },
}


def load_config(bizspec_dir: Path) -> dict:
    """``bizspec/config.yaml`` を読んで DEFAULT_CONFIG に deep-merge して返す。

    存在しない / 空 / パース不能の場合は DEFAULT_CONFIG をそのまま返す。
    """
    cfg_path = bizspec_dir / "config.yaml"
    if not cfg_path.exists():
        return _clone(DEFAULT_CONFIG)
    try:
        loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return _clone(DEFAULT_CONFIG)
    if not isinstance(loaded, dict):
        return _clone(DEFAULT_CONFIG)
    return _deep_merge(DEFAULT_CONFIG, loaded)


def _clone(d: dict) -> dict:
    """設定が呼び出し側で破壊変更されないよう常に独立した dict を返す。"""
    return copy.deepcopy(d)


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out
