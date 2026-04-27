from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

REQUIRED_FIELDS = ["unit", "aim", "phase", "job", "rule", "link", "core", "io", "executor"]
VALID_EXECUTOR_TYPES = {"script", "ai_agent", "manual"}
VALID_DIFFICULTY     = {"low", "medium", "high"}
VALID_AUTO_STATUS    = {"manual", "partially-automated", "automated"}
NON_EMPTY_LIST_FIELDS = ["job", "rule"]


@dataclass
class VError:
    file: Path
    field: str
    message: str


def _detect_yaml_hint(line: str) -> str:
    """よくある YAML ミスパターンを検出してヒントを返す。なければ空文字。"""
    stripped = line.strip()
    if not stripped.startswith("- "):
        return ""
    item = stripped[2:].lstrip()
    # すでにシングルクォートで正しく囲まれている → ヒント不要
    if item.startswith("'") and item.endswith("'") and len(item) >= 2:
        return ""
    if ": " in item or item.endswith(":"):
        return (
            f"リスト要素に `: ` が含まれています。"
            f"シングルクォートで全体を囲んでください → - '{item}'"
        )
    if item.startswith('"'):
        close = item.find('"', 1)
        if close != -1 and close < len(item) - 1:
            return (
                f"ダブルクォートで囲んだ値の後ろに文字列が続いています。"
                f"シングルクォートで全体を囲んでください → - '{item}'"
            )
    return ""


def _yaml_parse_message(path: Path, exc: yaml.YAMLError) -> str:
    """YAMLError に行情報とヒントを付加したメッセージを組み立てる。"""
    mark = getattr(exc, "problem_mark", None)
    if mark is None:
        return f"YAML パースエラー: {exc}"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return f"YAML パースエラー: {exc}"

    lineno = mark.line  # 0-indexed
    line_text = lines[lineno].rstrip() if lineno < len(lines) else ""
    base = f"YAML パースエラー（{lineno + 1}行目）: {line_text}"
    hint = _detect_yaml_hint(line_text)
    return f"{base}  ヒント: {hint}" if hint else base


def _check_file(path: Path) -> tuple[list[VError], Optional[dict]]:
    """単一ファイルを検証する。(errors, data) を返す。"""
    errors: list[VError] = []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [VError(path, "parse", _yaml_parse_message(path, e))], None

    if not isinstance(data, dict):
        return [VError(path, "format", "トップレベルはマッピングである必要があります")], None

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
                elif len(io[key]) == 0:
                    errors.append(VError(path, f"io.{key}", "空リストは許可されていません"))

    # effort (optional)
    if "effort" in data:
        eff = data["effort"]
        if not isinstance(eff, dict):
            errors.append(VError(path, "effort", "マッピングである必要があります"))
        elif "duration" in eff:
            dur = eff["duration"]
            if isinstance(dur, bool) or not isinstance(dur, (int, float)):
                errors.append(VError(path, "effort.duration",
                    "数値（時間単位）でなければなりません（例: 0.5 / 1 / 2.5）"))
            elif dur <= 0:
                errors.append(VError(path, "effort.duration",
                    "0より大きい値でなければなりません"))

    # automation (optional)
    if "automation" in data:
        aut = data["automation"]
        if not isinstance(aut, dict):
            errors.append(VError(path, "automation", "マッピングである必要があります"))
        else:
            if "difficulty" in aut and aut["difficulty"] not in VALID_DIFFICULTY:
                errors.append(VError(path, "automation.difficulty",
                    f"{sorted(VALID_DIFFICULTY)} のいずれかでなければなりません（現在: {aut['difficulty']!r}）"))
            if "status" in aut and aut["status"] not in VALID_AUTO_STATUS:
                errors.append(VError(path, "automation.status",
                    f"{sorted(VALID_AUTO_STATUS)} のいずれかでなければなりません（現在: {aut['status']!r}）"))

    # job / rule の空リスト
    for key in NON_EMPTY_LIST_FIELDS:
        if key in data and isinstance(data[key], list) and len(data[key]) == 0:
            errors.append(VError(path, key, "空リストは許可されていません"))

    return errors, data


def _check_process(process_dir: Path) -> list[VError]:
    yaml_files = sorted(p for p in process_dir.glob("*.yaml") if not p.name.startswith("_"))
    if not yaml_files:
        return []

    errors: list[VError] = []
    units: dict[str, dict] = {}

    for path in yaml_files:
        file_errors, data = _check_file(path)
        errors.extend(file_errors)
        if data is not None and isinstance(data.get("unit"), str):
            units[data["unit"]] = data

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
