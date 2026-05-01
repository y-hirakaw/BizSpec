from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ALL_FIELDS = ("unit", "aim", "scope", "rule", "io", "executor", "depends_on")
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
    """マッチした unit の情報を返す。"""
    hits: list[dict] = []
    kw_lower = keyword.lower()
    for path in sorted(process_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        unit_name = str(data.get("unit", path.stem))
        matched: list[tuple[str, str]] = []
        for field_path, text in _extract_texts(data, fields):
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
    bizspec_dir = root / "bizspec"
    keyword     = args.keyword

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    fields = tuple(args.field) if args.field else _ALL_FIELDS

    process_dirs = sorted(
        d for d in bizspec_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    total = 0
    for process_dir in process_dirs:
        hits = _search_process(process_dir, keyword, fields)
        for hit in hits:
            print(f"\n[{hit['process']}]  {hit['unit']}")
            for field_path, text in hit["matches"]:
                marker = text.replace(keyword, f"\033[1m{keyword}\033[0m")
                print(f"  {field_path:<12}  {marker}")
        total += len(hits)

    print()
    if total == 0:
        print(f'"{keyword}" にマッチする unit は見つかりませんでした')
        return 1

    print(f"{total} 件の unit が見つかりました")
    return 0
