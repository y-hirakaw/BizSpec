from __future__ import annotations

import json
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


def _unit_to_refactor_entry(u: dict) -> dict:
    link = u.get("link") or {}
    link = link if isinstance(link, dict) else {}
    up = link.get("up") or []
    down = link.get("down") or []

    eff = u.get("effort") or {}
    eff = eff if isinstance(eff, dict) else {}
    duration = eff.get("duration")
    frequency = eff.get("frequency")

    entry: dict = {
        "unit": u.get("unit", ""),
        "aim": u.get("aim", ""),
        "core": u.get("core", ""),
        "executor": (u.get("executor") or {}).get("type", "") if isinstance(u.get("executor"), dict) else "",
        "link_up": [str(x) for x in up] if isinstance(up, list) else [],
        "link_down": [str(x) for x in down] if isinstance(down, list) else [],
    }
    if isinstance(duration, (int, float)) and not isinstance(duration, bool):
        entry["effort_duration"] = duration
    if isinstance(frequency, int) and not isinstance(frequency, bool):
        entry["effort_frequency"] = frequency
    return entry


def _print_refactor_text(all_data: list[dict]) -> None:
    for proc in all_data:
        print(f"\n=== {proc['process']} ({len(proc['units'])} units) ===")
        for u in proc["units"]:
            core_val = u["core"]
            core_str = str(core_val).lower() if isinstance(core_val, bool) else str(core_val)
            print(f"\n[{u['unit']}]  core:{core_str}  executor:{u['executor']}")
            if u["aim"]:
                print(f"  aim: {u['aim']}")
            if u["link_up"]:
                print(f"  ↑ {', '.join(u['link_up'])}")
            if u["link_down"]:
                print(f"  ↓ {', '.join(u['link_down'])}")
            dur = u.get("effort_duration")
            freq = u.get("effort_frequency")
            if dur is not None or freq is not None:
                parts = []
                if dur is not None:
                    parts.append(f"{dur}h")
                if freq is not None:
                    parts.append(f"{freq}/月")
                print(f"  effort: {' × '.join(parts)}")
    print()


def _run_list_refactor(process_dirs: list[Path], fmt: str) -> int:
    all_data = []
    for process_dir in process_dirs:
        units = _load_units(process_dir)
        if not units:
            continue
        all_data.append({
            "process": process_dir.name,
            "units": [_unit_to_refactor_entry(u) for u in units],
        })

    if fmt == "json":
        print(json.dumps(all_data, ensure_ascii=False, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(all_data, allow_unicode=True, default_flow_style=False, sort_keys=False), end="")
    else:
        _print_refactor_text(all_data)

    return 0


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

    refactor = getattr(args, "refactor", False)
    fmt = getattr(args, "format", "text") or "text"

    if refactor or fmt in ("yaml", "json"):
        return _run_list_refactor(process_dirs, fmt)

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
        has_status     = any(u.get("status") for u in units)

        header = f"  {'unit':<{name_w}}  {'core':<6}  {'executor':<12}"
        sep    = f"  {'─' * name_w}  {'─' * 6}  {'─' * 12}"
        if has_status:
            header += f"  {'status':<12}"; sep += f"  {'─' * 12}"
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
            if has_status:
                st = str(u.get("status", "")) if u.get("status") else ""
                row += f"  {st:<12}"
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
