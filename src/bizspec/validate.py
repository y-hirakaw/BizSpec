from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REQUIRED_FIELDS = ["unit", "aim", "phase", "job", "rule", "link", "core", "io", "executor"]
VALID_EXECUTOR_TYPES = {"script", "ai_agent", "manual"}


@dataclass
class VError:
    file: Path
    field: str
    message: str


def _check_file(path: Path) -> list[VError]:
    errors: list[VError] = []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [VError(path, "parse", f"YAML パースエラー: {e}")]

    if not isinstance(data, dict):
        return [VError(path, "format", "トップレベルはマッピングである必要があります")]

    # 必須フィールド
    for f in REQUIRED_FIELDS:
        if f not in data:
            errors.append(VError(path, f, f"必須フィールド '{f}' がありません"))

    # unit 名とファイル名の一致
    if "unit" in data:
        expected = f"{data['unit']}.yaml"
        if path.name != expected:
            errors.append(VError(path, "unit",
                f"unit 名 '{data['unit']}' とファイル名 '{path.name}' が一致しません（期待: {expected}）"))

    # core は真偽値のみ
    if "core" in data and not isinstance(data["core"], bool):
        errors.append(VError(path, "core",
            f"true / false でなければなりません（現在: {data['core']!r}）"))

    # executor
    if "executor" in data:
        ex = data["executor"]
        if not isinstance(ex, dict):
            errors.append(VError(path, "executor", "マッピングである必要があります"))
        else:
            if "type" not in ex:
                errors.append(VError(path, "executor.type", "フィールドがありません"))
            elif ex["type"] not in VALID_EXECUTOR_TYPES:
                errors.append(VError(path, "executor.type",
                    f"{sorted(VALID_EXECUTOR_TYPES)} のいずれかでなければなりません（現在: {ex['type']!r}）"))
            if "reason" not in ex:
                errors.append(VError(path, "executor.reason", "フィールドがありません"))

    # link
    if "link" in data:
        lnk = data["link"]
        if not isinstance(lnk, dict):
            errors.append(VError(path, "link", "マッピングである必要があります"))
        else:
            for direction in ("up", "down"):
                if direction not in lnk:
                    errors.append(VError(path, f"link.{direction}", "フィールドがありません"))
                elif not isinstance(lnk[direction], list):
                    errors.append(VError(path, f"link.{direction}", "リストである必要があります"))

    # io
    if "io" in data:
        io = data["io"]
        if not isinstance(io, dict):
            errors.append(VError(path, "io", "マッピングである必要があります"))
        else:
            for key in ("in", "run", "out"):
                if key not in io:
                    errors.append(VError(path, f"io.{key}", "フィールドがありません"))
                elif not isinstance(io[key], list):
                    errors.append(VError(path, f"io.{key}", "リストである必要があります"))

    return errors


def _check_process(process_dir: Path) -> list[VError]:
    yaml_files = sorted(f for f in process_dir.glob("*.yaml"))
    if not yaml_files:
        return []

    errors: list[VError] = []

    # ファイル単体チェック＋全 unit ロード
    units: dict[str, dict] = {}
    for path in yaml_files:
        errors.extend(_check_file(path))
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("unit"), str):
                units[data["unit"]] = data
        except Exception:
            pass

    unit_names = set(units)

    # クロスファイルチェック
    for unit_name, data in units.items():
        path = process_dir / f"{unit_name}.yaml"
        lnk = data.get("link", {})
        if not isinstance(lnk, dict):
            continue

        for direction, opposite in (("down", "up"), ("up", "down")):
            targets = lnk.get(direction)
            if not isinstance(targets, list):
                continue
            for target in targets:
                if target not in unit_names:
                    errors.append(VError(path, f"link.{direction}",
                        f"'{target}' が存在しません（{target}.yaml が見つかりません）"))
                else:
                    back = units[target].get("link", {}).get(opposite, [])
                    if isinstance(back, list) and unit_name not in back:
                        errors.append(VError(path, f"link.{direction}",
                            f"'{target}' の link.{opposite} に '{unit_name}' がありません（双方向リンク不整合）"))

    return errors


def run_validate(args) -> int:
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

    total_errors = 0
    print()

    for process_dir in process_dirs:
        errors = _check_process(process_dir)
        label = process_dir.relative_to(root)

        if errors:
            print(f"FAIL  {label}")
            for e in errors:
                print(f"      {e.file.name:<40}  [{e.field}]  {e.message}")
            total_errors += len(errors)
        else:
            unit_count = len(list(process_dir.glob("*.yaml")))
            print(f"PASS  {label}  ({unit_count} units)")

    print()
    if total_errors == 0:
        print("✓ すべての検証が通過しました")
        return 0

    print(f"✗ {total_errors} 件のエラーが見つかりました")
    return 1
