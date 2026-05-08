from __future__ import annotations

import sys
from pathlib import Path

from .core.loader import apply_defaults, load_process_defaults, load_units_with_paths

_ALL_FIELDS = ("unit", "aim", "rule", "io", "executor", "depends_on")
FIELD_CHOICES = list(_ALL_FIELDS)


def _extract_texts(data: dict, fields: tuple[str, ...]) -> list[tuple[str, str]]:
    """(field_path, text) のリストを返す。"""
    results: list[tuple[str, str]] = []
    for field in fields:
        val = data.get(field)
        if val is None:
            continue
        if field == "io":
            io = val if isinstance(val, dict) else {}
            for sub in ("in", "process", "out"):
                sub_val = io.get(sub)
                if isinstance(sub_val, list):
                    for item in sub_val:
                        results.append((f"io.{sub}", str(item)))
                elif sub_val is not None:
                    results.append((f"io.{sub}", str(sub_val)))
        elif field == "executor":
            ex = val if isinstance(val, dict) else {}
            for sub in ("type", "reason"):
                sub_val = ex.get(sub)
                if sub_val is not None:
                    results.append((f"executor.{sub}", str(sub_val)))
        elif field == "depends_on":
            if isinstance(val, list):
                for item in val:
                    results.append(("depends_on", str(item)))
        elif isinstance(val, list):
            for item in val:
                results.append((field, str(item)))
        else:
            results.append((field, str(val)))
    return results


def _search_process(process_dir: Path, keyword: str, fields: tuple[str, ...]) -> list[dict]:
    """マッチした unit の情報を返す。_defaults.yaml の値も検索対象に含む。"""
    hits: list[dict] = []
    kw_lower = keyword.lower()
    defaults = load_process_defaults(process_dir)
    for path, data in load_units_with_paths(process_dir):
        merged = apply_defaults(data, defaults) if defaults else data
        unit_name = str(merged.get("unit", path.stem))
        matched: list[tuple[str, str]] = []
        for field_path, text in _extract_texts(merged, fields):
            if kw_lower in text.lower():
                matched.append((field_path, text))
        if matched:
            hits.append({
                "process": process_dir.name,
                "unit": unit_name,
                "file": path.name,
                "matches": matched,
            })
    return hits


def run_search(args) -> int:
    root        = Path(args.root).resolve()
    import json as _json
    bizspec_dir = root / "bizspec"
    keyword     = args.keyword
    fmt: str    = getattr(args, "format", "text")

    if not bizspec_dir.exists():
        msg = f"{bizspec_dir} が見つかりません"
        if fmt == "json":
            print(_json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    fields = tuple(args.field) if args.field else _ALL_FIELDS

    process_dirs = sorted(
        d for d in bizspec_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    all_hits: list[dict] = []
    for process_dir in process_dirs:
        all_hits.extend(_search_process(process_dir, keyword, fields))

    if fmt == "json":
        print(_json.dumps({
            "keyword": keyword,
            "fields": list(fields),
            "total": len(all_hits),
            "hits": [
                {
                    "process": h["process"],
                    "unit":    h["unit"],
                    "file":    h["file"],
                    "matches": [{"field": f, "text": t} for f, t in h["matches"]],
                }
                for h in all_hits
            ],
        }, ensure_ascii=False, indent=2))
        return 0 if all_hits else 1

    # text 形式
    for hit in all_hits:
        print(f"\n[{hit['process']}]  {hit['unit']}")
        for field_path, text in hit["matches"]:
            marker = text.replace(keyword, f"\033[1m{keyword}\033[0m")
            print(f"  {field_path:<12}  {marker}")

    print()
    if not all_hits:
        print(f'"{keyword}" にマッチする unit は見つかりませんでした')
        return 1

    print(f"{len(all_hits)} 件の unit が見つかりました")
    return 0
