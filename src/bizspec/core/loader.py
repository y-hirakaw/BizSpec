"""YAML ローダー（共通）。

`bizspec/<process>/<unit>.yaml` を読み込む各コマンドが個別に持っていた
ロジックをここに集約する。

## 仕様

- `_` で始まるファイル名・ディレクトリ名はスキップ（メタデータ・出力先扱い）
- パース失敗・dict でない YAML は **黙ってスキップ**（既存挙動を維持）
  - `tests/test_loader_behavior.py` がこの契約を固定している
- 戻り値の用途別に 4 種類の API を提供：
  - `load_units`           — `list[dict]`（list/viz/search 系）
  - `load_units_with_paths`— `list[(Path, dict)]`（リネーム後参照など）
  - `load_units_by_name`   — `dict[unit名, (Path, dict)]`（rename/renumber）
  - `load_unit`            — 単一ファイル
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import yaml


def iter_unit_files(process_dir: Path) -> Iterator[Path]:
    """プロセスディレクトリ内の unit YAML ファイルを名前順で yield する。`_` 始まりはスキップ。"""
    for path in sorted(process_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        yield path


def iter_processes(bizspec_dir: Path) -> Iterator[Path]:
    """bizspec/ 直下のプロセスディレクトリを名前順で yield する。`_` 始まりはスキップ。"""
    if not bizspec_dir.is_dir():
        return
    for d in sorted(bizspec_dir.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            yield d


def load_unit(path: Path) -> dict | None:
    """単一の unit YAML を読む。パース失敗・dict でない場合は ``None``。"""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def load_units(process_dir: Path) -> list[dict]:
    """プロセス内の有効な unit dict をリストで返す。"""
    units: list[dict] = []
    for path in iter_unit_files(process_dir):
        data = load_unit(path)
        if data is not None:
            units.append(data)
    return units


def load_units_with_paths(process_dir: Path) -> list[tuple[Path, dict]]:
    """`(path, data)` のリストで返す（パスが必要なコマンド用）。"""
    items: list[tuple[Path, dict]] = []
    for path in iter_unit_files(process_dir):
        data = load_unit(path)
        if data is not None:
            items.append((path, data))
    return items


def load_units_by_name(process_dir: Path) -> dict[str, tuple[Path, dict]]:
    """unit 名（``data["unit"]``）→ ``(path, data)`` のマップ。

    ``unit`` が文字列でないファイルはスキップする（rename / renumber 用途）。
    """
    units: dict[str, tuple[Path, dict]] = {}
    for path, data in load_units_with_paths(process_dir):
        name = data.get("unit")
        if isinstance(name, str):
            units[name] = (path, data)
    return units


def load_process_meta(process_dir: Path) -> dict:
    """プロセス直下の ``_process.yaml`` を読む（無ければ空 dict）。"""
    meta_path = process_dir / "_process.yaml"
    if not meta_path.exists():
        return {}
    try:
        data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
