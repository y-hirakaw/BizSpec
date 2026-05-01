from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import yaml

from .core.loader import load_units_by_name as _load_all_units

_PREFIX_RE = re.compile(r"^\d+_")


def _find_unit_file(process_dir: Path, unit_name: str) -> Optional[Path]:
    """unit名からファイルパスを解決する（採番プレフィックス対応）。"""
    exact = process_dir / f"{unit_name}.yaml"
    if exact.exists():
        return exact
    for p in process_dir.glob("*.yaml"):
        if not p.name.startswith("_") and _PREFIX_RE.sub("", p.stem) == unit_name:
            return p
    return None


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _find_link_refs(units: dict[str, tuple[Path, dict]], target: str) -> list[tuple[Path, str, str]]:
    """target を link.up/down で参照しているファイルのリストを返す。"""
    refs = []
    for uname, (upath, udata) in units.items():
        if uname == target:
            continue
        lnk = udata.get("link") or {}
        if not isinstance(lnk, dict):
            continue
        for direction in ("up", "down"):
            if target in (lnk.get(direction) or []):
                refs.append((upath, uname, direction))
    return refs


def _find_depends_on_refs(bizspec_dir: Path, process: str, unit_name: str) -> list[tuple[Path, str]]:
    """他プロセスの depends_on で process:unit_name を参照しているファイルを返す。"""
    from .core.loader import iter_processes, load_units_with_paths
    refs = []
    entry = f"{process}:{unit_name}"
    for proc_dir in iter_processes(bizspec_dir):
        if proc_dir.name == process:
            continue
        for path, data in load_units_with_paths(proc_dir):
            deps = data.get("depends_on") or []
            if isinstance(deps, list) and entry in deps:
                refs.append((path, str(path.relative_to(bizspec_dir.parent))))
    return refs


def run_rename(args) -> int:
    from .core.prompt import confirm
    root = Path(args.root).resolve()
    bizspec_dir = root / "bizspec"
    process_dir = bizspec_dir / args.process
    old_name: str = args.old
    new_name: str = args.new
    dry_run: bool = getattr(args, "dry_run", False)
    yes: bool     = getattr(args, "yes", False)

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    if not process_dir.is_dir():
        print(f"ERROR: プロセス '{args.process}' が見つかりません", file=sys.stderr)
        return 1

    if old_name == new_name:
        print("ERROR: 変更前後の名前が同じです", file=sys.stderr)
        return 1

    old_path = _find_unit_file(process_dir, old_name)
    if old_path is None:
        print(f"ERROR: unit '{old_name}' が見つかりません", file=sys.stderr)
        return 1

    # 新ファイル名（採番プレフィックスがあれば保持）
    prefix_m = _PREFIX_RE.match(old_path.stem)
    prefix = prefix_m.group(0) if prefix_m else ""
    new_path = process_dir / f"{prefix}{new_name}.yaml"

    if new_path.exists() and new_path.resolve() != old_path.resolve():
        print(f"ERROR: '{new_path.name}' はすでに存在します", file=sys.stderr)
        return 1

    units = _load_all_units(process_dir)
    link_refs = _find_link_refs(units, old_name)
    ext_refs = _find_depends_on_refs(bizspec_dir, args.process, old_name)

    if dry_run:
        print(f"\n{args.process} rename '{old_name}' → '{new_name}'  (dry-run)\n")
        print(f"  {old_path.name}  →  {new_path.name}")
        for upath, _, direction in link_refs:
            print(f"  {upath.name}  link.{direction} を更新")
        if ext_refs:
            print()
            for _, rel in ext_refs:
                print(f"  WARN  {rel}  depends_on の手動更新が必要です")
        print()
        return 0

    # 確認プロンプト（TTY 環境でのみ）
    extra = f"、{len(link_refs)} ファイルの link 参照も更新" if link_refs else ""
    if not confirm(f"\n'{old_name}' を '{new_name}' にリネームします{extra}", yes=yes):
        print("中止しました")
        return 1

    # ファイル書き換え・リネーム
    data = yaml.safe_load(old_path.read_text(encoding="utf-8"))
    data["unit"] = new_name
    _write_yaml(new_path, data)
    if old_path.resolve() != new_path.resolve():
        old_path.unlink()
    print(f"  renamed: {old_path.name}  →  {new_path.name}")

    # 同プロセス内の link 参照を更新
    for upath, _, direction in link_refs:
        udata = yaml.safe_load(upath.read_text(encoding="utf-8"))
        lnk = udata.setdefault("link", {})
        refs = lnk.get(direction) or []
        lnk[direction] = [new_name if r == old_name else r for r in refs]
        _write_yaml(upath, udata)
        print(f"  updated: {upath.name}  (link.{direction})")

    # 他プロセスの depends_on 警告
    if ext_refs:
        print()
        for _, rel in ext_refs:
            print(f"  WARN  {rel}  depends_on を手動で更新してください（{args.process}:{new_name}）")

    # validate
    print()
    from bizspec.validate import _check_process
    errors = _check_process(process_dir, bizspec_dir)
    if errors:
        print("WARN  リネーム後の validate:")
        for e in errors:
            print(f"      {e.file.name:<40}  [{e.field}]  {e.message}")
        return 1

    print("✓ validate 通過")
    return 0


def run_rm(args) -> int:
    from .core.prompt import confirm
    root = Path(args.root).resolve()
    bizspec_dir = root / "bizspec"
    process_dir = bizspec_dir / args.process
    unit_name: str = args.unit
    dry_run: bool = getattr(args, "dry_run", False)
    force: bool = getattr(args, "force", False)
    yes: bool   = getattr(args, "yes", False)

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    if not process_dir.is_dir():
        print(f"ERROR: プロセス '{args.process}' が見つかりません", file=sys.stderr)
        return 1

    target_path = _find_unit_file(process_dir, unit_name)
    if target_path is None:
        print(f"ERROR: unit '{unit_name}' が見つかりません", file=sys.stderr)
        return 1

    units = _load_all_units(process_dir)
    link_refs = _find_link_refs(units, unit_name)
    ext_refs = _find_depends_on_refs(bizspec_dir, args.process, unit_name)

    # フロー分断の警告: 削除後に link.up/down が空になる unit を検出
    disconnects: list[str] = []
    for upath, uname, direction in link_refs:
        _, udata = units[uname]
        lnk = udata.get("link") or {}
        remaining = [r for r in (lnk.get(direction) or []) if r != unit_name]
        if not remaining:
            disconnects.append(f"  '{uname}' の link.{direction} が空になります")

    if dry_run:
        print(f"\n{args.process} rm '{unit_name}'  (dry-run)\n")
        print(f"  {target_path.name}  を削除")
        for upath, _, direction in link_refs:
            print(f"  {upath.name}  link.{direction} から '{unit_name}' を削除")
        if disconnects or ext_refs:
            print()
        for msg in disconnects:
            print(f"  WARN  {msg.strip()}")
        for _, rel in ext_refs:
            print(f"  WARN  {rel}  depends_on の手動更新が必要です")
        print()
        return 0

    if disconnects and not force:
        print(f"WARN  '{unit_name}' を削除するとフローが分断される可能性があります:")
        for msg in disconnects:
            print(msg)
        print("\n続けるには --force を指定してください")
        return 1

    # 確認プロンプト（TTY 環境でのみ）
    extra = f"、{len(link_refs)} ファイルの link 参照も削除" if link_refs else ""
    if not confirm(f"\n'{unit_name}' を削除します{extra}", yes=yes):
        print("中止しました")
        return 1

    target_path.unlink()
    print(f"  deleted: {target_path.name}")

    for upath, _, direction in link_refs:
        udata = yaml.safe_load(upath.read_text(encoding="utf-8"))
        lnk = udata.setdefault("link", {})
        refs = lnk.get(direction) or []
        lnk[direction] = [r for r in refs if r != unit_name]
        _write_yaml(upath, udata)
        print(f"  updated: {upath.name}  (link.{direction})")

    if ext_refs:
        print()
        for _, rel in ext_refs:
            print(f"  WARN  {rel}  depends_on を手動で更新してください")

    # validate
    print()
    from bizspec.validate import _check_process
    errors = _check_process(process_dir, bizspec_dir)
    if errors:
        print("WARN  削除後の validate:")
        for e in errors:
            print(f"      {e.file.name:<40}  [{e.field}]  {e.message}")
        return 1

    print("✓ validate 通過")
    return 0
