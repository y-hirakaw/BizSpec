from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _load_units(process_dir: Path) -> list[dict]:
    units = []
    for path in sorted(process_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
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

        has_duration   = any(isinstance(u.get("effort"), dict) and u["effort"].get("duration") for u in units)
        has_frequency  = any(isinstance(u.get("effort"), dict) and u["effort"].get("frequency") for u in units)
        has_difficulty = any(isinstance(u.get("automation"), dict) and u["automation"].get("difficulty") for u in units)
        has_deps       = any(isinstance(u.get("depends_on"), list) and u["depends_on"] for u in units)

        header = f"  {'unit':<{name_w}}  {'core':<6}  {'executor':<12}"
        sep    = f"  {'─' * name_w}  {'─' * 6}  {'─' * 12}"
        if has_duration:
            header += f"  {'duration':<10}"; sep += f"  {'─' * 10}"
        if has_frequency:
            header += f"  {'freq/月':<8}"; sep += f"  {'─' * 8}"
        if has_difficulty:
            header += f"  difficulty"; sep += f"  {'─' * 10}"
        if has_deps:
            header += f"  deps"; sep += f"  {'─' * 4}"
        print(header)
        print(sep)

        for u in units:
            name     = str(u.get("unit", ""))
            core     = u.get("core", "")
            core_str = str(core).lower() if isinstance(core, bool) else str(core)
            ex_type  = u.get("executor", {}).get("type", "") if isinstance(u.get("executor"), dict) else ""
            row = f"  {name:<{name_w}}  {core_str:<6}  {ex_type:<12}"
            eff = u.get("effort") or {}
            eff = eff if isinstance(eff, dict) else {}
            if has_duration:
                d = eff.get("duration")
                dur = f"{d}h" if isinstance(d, (int, float)) and not isinstance(d, bool) else ""
                row += f"  {dur:<10}"
            if has_frequency:
                f = eff.get("frequency")
                freq = str(f) if isinstance(f, int) and not isinstance(f, bool) else ""
                row += f"  {freq:<8}"
            if has_difficulty:
                aut = u.get("automation") or {}
                diff = str(aut.get("difficulty", "")) if isinstance(aut, dict) else ""
                row += f"  {diff}"
            if has_deps:
                dep_list = u.get("depends_on")
                dep_count = str(len(dep_list)) if isinstance(dep_list, list) and dep_list else ""
                row += f"  {dep_count}"
            print(row)

    print()
    return 0
