from __future__ import annotations

import sys
from pathlib import Path

import yaml


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


def run_list(args) -> int:
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

    for process_dir in process_dirs:
        units = _load_units(process_dir)
        if not units:
            continue

        print(f"\n{process_dir.name}  ({len(units)} units)")

        name_w = max(len(str(u.get("unit", ""))) for u in units)
        name_w = max(name_w, 4)

        print(f"  {'unit':<{name_w}}  {'core':<6}  executor")
        print(f"  {'─' * name_w}  {'─' * 6}  {'─' * 10}")

        for u in units:
            name     = str(u.get("unit", ""))
            core     = u.get("core", "")
            core_str = str(core).lower() if isinstance(core, bool) else str(core)
            ex_type  = u.get("executor", {}).get("type", "") if isinstance(u.get("executor"), dict) else ""
            print(f"  {name:<{name_w}}  {core_str:<6}  {ex_type}")

    print()
    return 0
