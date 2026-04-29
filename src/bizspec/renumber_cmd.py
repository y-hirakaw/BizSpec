from __future__ import annotations

import re
import sys
from collections import defaultdict, deque
from pathlib import Path

import yaml

_PREFIX_RE = re.compile(r"^\d+_")


def _load_units(process_dir: Path) -> dict[str, tuple[Path, dict]]:
    """unit名 → (ファイルパス, data) のマップを返す。"""
    units: dict[str, tuple[Path, dict]] = {}
    for path in sorted(process_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        unit_name = data.get("unit")
        if isinstance(unit_name, str):
            units[unit_name] = (path, data)
    return units


def _topological_sort(units: dict[str, tuple[Path, dict]]) -> list[str]:
    """Kahn's algorithm でトポロジカルソートした unit 名リストを返す。"""
    in_degree: dict[str, int] = {name: 0 for name in units}
    graph: dict[str, list[str]] = defaultdict(list)

    for name, (_, data) in units.items():
        lnk = data.get("link") or {}
        if not isinstance(lnk, dict):
            continue
        downs = lnk.get("down") or []
        if not isinstance(downs, list):
            continue
        for target in downs:
            if target in units:
                graph[name].append(target)
                in_degree[target] += 1

    queue: deque[str] = deque(sorted(n for n, d in in_degree.items() if d == 0))
    result: list[str] = []
    visited: set[str] = set()

    while queue:
        node = queue.popleft()
        result.append(node)
        visited.add(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # サイクル等で残ったノードはアルファベット順で末尾に追加
    for n in sorted(units):
        if n not in visited:
            result.append(n)

    return result


def run_renumber(args) -> int:
    root = Path(args.root).resolve()
    bizspec_dir = root / "bizspec"
    process_dir = bizspec_dir / args.process
    dry_run: bool = getattr(args, "dry_run", False)

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    if not process_dir.is_dir():
        print(f"ERROR: プロセス '{args.process}' が見つかりません", file=sys.stderr)
        return 1

    units = _load_units(process_dir)
    if not units:
        print("unit ファイルが見つかりません")
        return 0

    ordered = _topological_sort(units)
    width = max(2, len(str(len(ordered))))

    renames: list[tuple[Path, Path]] = []
    for i, unit_name in enumerate(ordered, 1):
        old_path, _ = units[unit_name]
        new_name = f"{str(i).zfill(width)}_{unit_name}.yaml"
        new_path = process_dir / new_name
        if old_path.name != new_name:
            renames.append((old_path, new_path))

    if not renames:
        print(f"  {args.process}: 変更なし（すでに採番済み）")
        return 0

    if dry_run:
        print(f"\n{args.process}  (dry-run)\n")
        for old, new in renames:
            print(f"  {old.name}  →  {new.name}")
        print()
        return 0

    for old, new in renames:
        old.rename(new)
        print(f"  renamed: {old.name}  →  {new.name}")

    print(f"\n{args.process}: {len(renames)} ファイルをリネームしました")
    return 0
