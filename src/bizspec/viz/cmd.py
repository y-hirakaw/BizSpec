"""``bizspec viz`` の CLI エントリ。"""

from __future__ import annotations

import sys
from pathlib import Path

from ..core.loader import load_units, load_process_meta
from .builder import _generate_html, _generate_index_html


def run_viz(args) -> int:
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

    out_dir = bizspec_dir / "_viz"
    out_dir.mkdir(exist_ok=True)

    generated = 0
    all_units: dict[str, list[dict]] = {}
    all_display_names: dict[str, str] = {}
    for process_dir in process_dirs:
        units = load_units(process_dir)
        if not units:
            continue
        meta = load_process_meta(process_dir)
        display_name = meta.get("name") or None
        html = _generate_html(process_dir.name, units, display_name=display_name)
        if not html:
            continue
        out_path = out_dir / f"{process_dir.name}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"  {out_path.relative_to(root)}")
        all_units[process_dir.name] = units
        if display_name:
            all_display_names[process_dir.name] = display_name
        generated += 1

    if generated == 0:
        print("WARNING: 出力された HTML はありません", file=sys.stderr)
        return 1

    # 引数なし（全プロセス対象）のときだけ index.html も生成する
    if not getattr(args, "process", None) and len(all_units) > 1:
        index_html = _generate_index_html(all_units, display_names=all_display_names)
        if index_html:
            index_path = out_dir / "index.html"
            index_path.write_text(index_html, encoding="utf-8")
            print(f"  {index_path.relative_to(root)}")

    return 0
