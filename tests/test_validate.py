from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.validate import _check_file, _check_process, _detect_yaml_hint, run_validate


# ── ヘルパー ──────────────────────────────────────────────────────────────────

def _list_yaml(items: list, indent: int = 4) -> str:
    if not items:
        return " []"
    lines = "\n".join(" " * indent + f"- {item}" for item in items)
    return f"\n{lines}"


def make_unit(
    name: str,
    up: list | None = None,
    down: list | None = None,
    core=True,
    executor_type: str = "script",
    executor_reason: str = "定型処理のため",
    rule: list | None = None,
    io_in: list | None = None,
    io_process: list | None = None,
    io_out: list | None = None,
    status: str = "stable",
) -> str:
    up    = up    if up    is not None else []
    down  = down  if down  is not None else []
    rule   = rule  if rule  is not None else ["制約"]
    io_in  = io_in  if io_in  is not None else ["入力"]
    io_process = io_process if io_process is not None else ["実行手順"]
    io_out = io_out if io_out is not None else ["出力"]

    if core is True:
        core_str = "true"
    elif core is False:
        core_str = "false"
    else:
        core_str = str(core)

    return (
        f"unit: {name}\n"
        f"aim: テスト用 unit\n"
        f"phase: spec\n"
        f"rule:{_list_yaml(rule)}\n"
        f"link:\n"
        f"  up:{_list_yaml(up)}\n"
        f"  down:{_list_yaml(down)}\n"
        f"core: {core_str}\n"
        f"io:\n"
        f"  in:{_list_yaml(io_in)}\n"
        f"  process:{_list_yaml(io_process)}\n"
        f"  out:{_list_yaml(io_out)}\n"
        f"executor:\n"
        f"  type: {executor_type}\n"
        f"  reason: {executor_reason}\n"
        f"status: {status}\n"
    )


def write_unit(dir: Path, name: str, content: str) -> Path:
    path = dir / f"{name}.yaml"
    path.write_text(content, encoding="utf-8")
    return path


# ── _check_file ───────────────────────────────────────────────────────────────

class TestCheckFile:
    def test_valid_unit(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit"))
        errors, data = _check_file(tmp_path / "TestUnit.yaml")
        assert errors == []
        assert data is not None

    def test_missing_required_field(self, tmp_path):
        content = make_unit("TestUnit").replace("aim: テスト用 unit\n", "")
        write_unit(tmp_path, "TestUnit", content)
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "aim" for e in errors)

    def test_core_undetermined_allowed(self, tmp_path):
        """'undetermined' は AI がユーザー確認待ちで使う仮置き値として許容される。"""
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", core="undetermined"))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert not any(e.field == "core" for e in errors)

    def test_invalid_core_value(self, tmp_path):
        """true / false / 'undetermined' 以外はエラー。"""
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", core="maybe"))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "core" for e in errors)

    def test_phase_recommended_no_warn(self, tmp_path):
        """推奨語彙の phase は warn にもならない。"""
        # make_unit のデフォルト phase は "spec"
        write_unit(tmp_path, "U", make_unit("U"))
        diags, _ = _check_file(tmp_path / "U.yaml")
        assert not any(d.field == "phase" for d in diags)

    def test_phase_unknown_emits_warn(self, tmp_path):
        """推奨外の phase は severity='warn' で報告される（エラーではない）。"""
        content = make_unit("U").replace("phase: spec", "phase: 知らない値")
        write_unit(tmp_path, "U", content)
        diags, _ = _check_file(tmp_path / "U.yaml")
        phase_diags = [d for d in diags if d.field == "phase"]
        assert len(phase_diags) == 1
        assert phase_diags[0].severity == "warn"

    def test_invalid_executor_type(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", executor_type="human"))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "executor.type" for e in errors)

    def test_missing_executor_reason(self, tmp_path):
        content = make_unit("TestUnit").replace("  reason: 定型処理のため\n", "")
        write_unit(tmp_path, "TestUnit", content)
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "executor.reason" for e in errors)

    def test_empty_rule(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", rule=[]))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "rule" for e in errors)

    def test_empty_io_in(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", io_in=[]))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "io.in" for e in errors)

    def test_empty_io_out(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", io_out=[]))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "io.out" for e in errors)

    def test_unit_filename_mismatch(self, tmp_path):
        write_unit(tmp_path, "WrongName", make_unit("TestUnit"))
        errors, _ = _check_file(tmp_path / "WrongName.yaml")
        assert any(e.field == "unit" for e in errors)

    def test_yaml_parse_error(self, tmp_path):
        path = tmp_path / "TestUnit.yaml"
        path.write_text("key: [unclosed bracket", encoding="utf-8")
        errors, data = _check_file(path)
        assert any(e.field == "parse" for e in errors)
        assert data is None

    def test_parse_error_shows_line_number(self, tmp_path):
        # ダブルクォート後に文字が続くと YAML パースエラー → 行番号が表示される
        path = tmp_path / "TestUnit.yaml"
        path.write_text('rule:\n  - "02.概要設計" フォルダ\n', encoding="utf-8")
        errors, _ = _check_file(path)
        assert any("行" in e.message for e in errors if e.field == "parse")

    def test_parse_error_colon_hint(self, tmp_path):
        # ダブルクォート後に文字が続く行で `: ` も含む場合 → コロンのヒントが出る
        path = tmp_path / "TestUnit.yaml"
        path.write_text('rule:\n  - 対象シート: "考慮漏れ"（Backend用）\n', encoding="utf-8")
        errors, _ = _check_file(path)
        parse_errors = [e for e in errors if e.field == "parse"]
        assert parse_errors
        assert "ヒント" in parse_errors[0].message

    def test_parse_error_doublequote_hint(self, tmp_path):
        path = tmp_path / "TestUnit.yaml"
        path.write_text('rule:\n  - "02.概要設計" フォルダ\n', encoding="utf-8")
        errors, _ = _check_file(path)
        parse_errors = [e for e in errors if e.field == "parse"]
        assert parse_errors
        assert "ヒント" in parse_errors[0].message


# ── _detect_yaml_hint ─────────────────────────────────────────────────────────

class TestDetectYamlHint:
    def test_colon_space_in_list_item(self):
        hint = _detect_yaml_hint("  - 対象シート: Backend用")
        assert hint != ""
        assert "シングルクォート" in hint

    def test_doublequote_followed_by_text(self):
        hint = _detect_yaml_hint('  - "02.概要設計" フォルダ')
        assert hint != ""
        assert "シングルクォート" in hint

    def test_normal_list_item_no_hint(self):
        assert _detect_yaml_hint("  - 普通のテキスト") == ""

    def test_non_list_line_no_hint(self):
        assert _detect_yaml_hint("unit: TestUnit") == ""

    def test_properly_quoted_no_hint(self):
        assert _detect_yaml_hint("  - '対象: 値'") == ""


# ── _check_process ────────────────────────────────────────────────────────────

class TestCheckProcess:
    def test_valid_two_unit_process(self, tmp_path):
        write_unit(tmp_path, "UnitA", make_unit("UnitA", down=["UnitB"]))
        write_unit(tmp_path, "UnitB", make_unit("UnitB", up=["UnitA"]))
        assert _check_process(tmp_path) == []

    def test_valid_single_unit(self, tmp_path):
        write_unit(tmp_path, "UnitA", make_unit("UnitA"))
        assert _check_process(tmp_path) == []

    def test_empty_process_dir(self, tmp_path):
        assert _check_process(tmp_path) == []

    def test_link_target_not_found(self, tmp_path):
        write_unit(tmp_path, "UnitA", make_unit("UnitA", down=["NonExistent"]))
        errors = _check_process(tmp_path)
        assert any(e.field == "link.down" for e in errors)

    def test_link_bidirectional_inconsistency(self, tmp_path):
        # A.down に B があるが B.up に A がない
        write_unit(tmp_path, "UnitA", make_unit("UnitA", down=["UnitB"]))
        write_unit(tmp_path, "UnitB", make_unit("UnitB", up=[]))
        errors = _check_process(tmp_path)
        assert any("双方向" in e.message for e in errors)

    def test_three_unit_chain(self, tmp_path):
        write_unit(tmp_path, "UnitA", make_unit("UnitA", down=["UnitB"]))
        write_unit(tmp_path, "UnitB", make_unit("UnitB", up=["UnitA"], down=["UnitC"]))
        write_unit(tmp_path, "UnitC", make_unit("UnitC", up=["UnitB"]))
        assert _check_process(tmp_path) == []

    def test_branch_pattern(self, tmp_path):
        # A → B, A → C（分岐）
        write_unit(tmp_path, "UnitA", make_unit("UnitA", down=["UnitB", "UnitC"]))
        write_unit(tmp_path, "UnitB", make_unit("UnitB", up=["UnitA"]))
        write_unit(tmp_path, "UnitC", make_unit("UnitC", up=["UnitA"]))
        assert _check_process(tmp_path) == []

    def test_skips_underscore_yaml(self, tmp_path):
        write_unit(tmp_path, "UnitA", make_unit("UnitA"))
        (tmp_path / "_process.yaml").write_text("name: テスト\n", encoding="utf-8")
        assert _check_process(tmp_path) == []


# ── automation optional fields ────────────────────────────────────────────────

class TestAutomationOptionalFields:
    def test_valid_automation_passes(self, tmp_path):
        content = make_unit("UnitA") + "automation:\n  difficulty: medium\n  status: manual\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_invalid_difficulty_fails(self, tmp_path):
        content = make_unit("UnitA") + "automation:\n  difficulty: extreme\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "automation.difficulty" for e in errors)

    def test_invalid_status_fails(self, tmp_path):
        content = make_unit("UnitA") + "automation:\n  status: unknown\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "automation.status" for e in errors)

    def test_automation_not_dict_fails(self, tmp_path):
        content = make_unit("UnitA") + "automation: invalid\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "automation" for e in errors)

    def test_effort_duration_numeric_passes(self, tmp_path):
        content = make_unit("UnitA") + "effort:\n  duration: 0.5\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_effort_duration_string_fails(self, tmp_path):
        content = make_unit("UnitA") + "effort:\n  duration: '30m'\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "effort.duration" for e in errors)

    def test_effort_duration_zero_passes(self, tmp_path):
        content = make_unit("UnitA") + "effort:\n  duration: 0\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert not any(e.field == "effort.duration" for e in errors)

    def test_effort_not_dict_fails(self, tmp_path):
        content = make_unit("UnitA") + "effort: invalid\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "effort" for e in errors)

    def test_all_difficulty_values_valid(self, tmp_path):
        for diff in ("low", "medium", "high"):
            content = make_unit("UnitA") + f"automation:\n  difficulty: {diff}\n"
            write_unit(tmp_path, "UnitA", content)
            errors, _ = _check_file(tmp_path / "UnitA.yaml")
            assert errors == [], f"difficulty={diff} should be valid"

    def test_all_status_values_valid(self, tmp_path):
        for status in ("manual", "partially-automated", "automated"):
            content = make_unit("UnitA") + f"automation:\n  status: {status}\n"
            write_unit(tmp_path, "UnitA", content)
            errors, _ = _check_file(tmp_path / "UnitA.yaml")
            assert errors == [], f"status={status} should be valid"


class TestDependsOn:
    def test_valid_depends_on_passes(self, tmp_path):
        content = make_unit("UnitA") + "depends_on:\n  - other-proc:UnitB\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_multiple_deps_pass(self, tmp_path):
        content = make_unit("UnitA") + "depends_on:\n  - proc-a:X\n  - proc-b:Y\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_not_list_fails(self, tmp_path):
        content = make_unit("UnitA") + "depends_on: other-proc:UnitB\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "depends_on" for e in errors)

    def test_missing_colon_fails(self, tmp_path):
        content = make_unit("UnitA") + "depends_on:\n  - other-proc-UnitB\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "depends_on" for e in errors)

    def test_cross_process_exists_passes(self, tmp_path):
        bizspec = tmp_path / "bizspec"
        proc_a = bizspec / "proc-a"
        proc_b = bizspec / "proc-b"
        proc_a.mkdir(parents=True)
        proc_b.mkdir(parents=True)
        write_unit(proc_b, "UnitB", make_unit("UnitB"))
        content = make_unit("UnitA") + "depends_on:\n  - proc-b:UnitB\n"
        write_unit(proc_a, "UnitA", content)
        errors = _check_process(proc_a, bizspec)
        assert errors == []

    def test_cross_process_missing_fails(self, tmp_path):
        bizspec = tmp_path / "bizspec"
        proc_a = bizspec / "proc-a"
        proc_a.mkdir(parents=True)
        content = make_unit("UnitA") + "depends_on:\n  - proc-b:UnitB\n"
        write_unit(proc_a, "UnitA", content)
        errors = _check_process(proc_a, bizspec)
        assert any(e.field == "depends_on" for e in errors)


class TestLifecycleStatus:
    def test_valid_status_stable(self, tmp_path):
        content = make_unit("UnitA") + "status: stable\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_valid_status_deprecated_with_reason(self, tmp_path):
        content = make_unit("UnitA") + "status: deprecated\ndeprecated_reason: 新プロセスに統合\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert errors == []

    def test_invalid_status_value(self, tmp_path):
        content = make_unit("UnitA") + "status: active\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "status" for e in errors)

    def test_deprecated_reason_without_deprecated_status_fails(self, tmp_path):
        content = make_unit("UnitA") + "status: stable\ndeprecated_reason: 理由\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "deprecated_reason" for e in errors)

    def test_deprecated_reason_without_status_fails(self, tmp_path):
        content = make_unit("UnitA") + "deprecated_reason: 理由\n"
        write_unit(tmp_path, "UnitA", content)
        errors, _ = _check_file(tmp_path / "UnitA.yaml")
        assert any(e.field == "deprecated_reason" for e in errors)

    def test_all_valid_statuses(self, tmp_path):
        for st in ("draft", "review", "stable", "deprecated"):
            content = make_unit(f"Unit{st}") + f"status: {st}\n"
            write_unit(tmp_path, f"Unit{st}", content)
            errors, _ = _check_file(tmp_path / f"Unit{st}.yaml")
            assert errors == [], f"status: {st} should be valid"


# ── run_validate (CLI entry point) ────────────────────────────────────────────

class _ValidateArgs:
    def __init__(self, root, process=None, format="text"):
        self.root = str(root)
        self.process = process
        self.format = format


_INVALID_UNIT = (  # missing required field 'aim'
    "unit: BadUnit\n"
    "phase: spec\n"
    "rule:\n  - y\n"
    "link:\n  up: []\n  down: []\n"
    "core: true\n"
    "io:\n  in:\n    - i\n  process:\n    - r\n  out:\n    - o\n"
    "executor:\n  type: script\n  reason: r\n"
    "status: stable\n"
)


class TestRunValidate:
    def test_no_bizspec_dir(self, tmp_path, capsys):
        result = run_validate(_ValidateArgs(tmp_path))
        assert result == 1
        assert "が見つかりません" in capsys.readouterr().err

    def test_specified_process_not_found(self, tmp_path, capsys):
        (tmp_path / "bizspec").mkdir()
        result = run_validate(_ValidateArgs(tmp_path, process="missing"))
        assert result == 1
        assert "が見つかりません" in capsys.readouterr().err

    def test_all_pass_returns_zero(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "UnitA", make_unit("UnitA"))
        result = run_validate(_ValidateArgs(tmp_path))
        out = capsys.readouterr().out
        assert result == 0
        assert "PASS" in out
        assert "✓" in out

    def test_some_errors_returns_one(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "BadUnit", _INVALID_UNIT)
        result = run_validate(_ValidateArgs(tmp_path))
        out = capsys.readouterr().out
        assert result == 1
        assert "FAIL" in out
        assert "✗" in out

    def test_specific_process_filter(self, tmp_path, capsys):
        for name in ("proc-a", "proc-b"):
            proc = tmp_path / "bizspec" / name
            proc.mkdir(parents=True)
            write_unit(proc, "U", make_unit("U"))
        result = run_validate(_ValidateArgs(tmp_path, process="proc-a"))
        out = capsys.readouterr().out
        assert result == 0
        assert "proc-a" in out
        assert "proc-b" not in out

    def test_underscore_dirs_skipped(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "U", make_unit("U"))
        viz = tmp_path / "bizspec" / "_viz"
        viz.mkdir()
        (viz / "junk.yaml").write_text("not: valid: yaml: at: all", encoding="utf-8")
        result = run_validate(_ValidateArgs(tmp_path))
        out = capsys.readouterr().out
        assert result == 0
        assert "_viz" not in out

    def test_underscore_files_not_counted(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "Real", make_unit("Real"))
        write_unit(proc, "_template", make_unit("Tpl"))
        result = run_validate(_ValidateArgs(tmp_path))
        out = capsys.readouterr().out
        assert result == 0
        assert "(1 units)" in out

    def test_aggregate_error_count(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "Bad1", _INVALID_UNIT)
        write_unit(proc, "Bad2", _INVALID_UNIT)
        result = run_validate(_ValidateArgs(tmp_path))
        out = capsys.readouterr().out
        assert result == 1
        import re
        m = re.search(r"(\d+) 件のエラー", out)
        assert m and int(m.group(1)) >= 2


# ── run_validate --format json ────────────────────────────────────────────────

class TestRunValidateJson:
    def test_json_all_pass(self, tmp_path, capsys):
        import json
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "U", make_unit("U"))
        result = run_validate(_ValidateArgs(tmp_path, format="json"))
        out = capsys.readouterr().out
        assert result == 0
        data = json.loads(out)
        assert data["ok"] is True
        assert data["total_errors"] == 0
        assert len(data["processes"]) == 1
        assert data["processes"][0]["process"] == "proc-a"
        assert data["processes"][0]["passed"] is True
        assert data["processes"][0]["errors"] == []
        assert data["processes"][0]["unit_count"] == 1

    def test_json_with_errors(self, tmp_path, capsys):
        import json
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_unit(proc, "Bad", _INVALID_UNIT)
        result = run_validate(_ValidateArgs(tmp_path, format="json"))
        out = capsys.readouterr().out
        assert result == 1
        data = json.loads(out)
        assert data["ok"] is False
        assert data["total_errors"] >= 1
        proc_a = data["processes"][0]
        assert proc_a["passed"] is False
        assert any(e["field"] == "aim" for e in proc_a["errors"])
        # file path is relative to root, contains process and filename
        assert proc_a["errors"][0]["file"].endswith("Bad.yaml")

    def test_json_no_bizspec_dir(self, tmp_path, capsys):
        import json
        result = run_validate(_ValidateArgs(tmp_path, format="json"))
        out = capsys.readouterr().out
        assert result == 1
        data = json.loads(out)
        assert data["ok"] is False
        assert "error" in data

    def test_json_process_not_found(self, tmp_path, capsys):
        import json
        (tmp_path / "bizspec").mkdir()
        result = run_validate(_ValidateArgs(tmp_path, process="missing", format="json"))
        out = capsys.readouterr().out
        assert result == 1
        data = json.loads(out)
        assert data["ok"] is False
        assert "missing" in data["error"]


# ── _defaults.yaml 由来のフィールドが必須チェックを満たすこと ──────────────
# unit YAML に書かれていなくても _defaults.yaml で補完されていれば
# 「必須フィールド欠落」エラーが出ないこと。

class TestValidateWithDefaults:
    def _setup(self, tmp_path, defaults_yaml: str, unit_yaml: str):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        (proc / "_defaults.yaml").write_text(defaults_yaml, encoding="utf-8")
        (proc / "U1.yaml").write_text(unit_yaml, encoding="utf-8")
        return tmp_path

    def test_phase_inherited_from_defaults(self, tmp_path, capsys):
        """unit に phase が無くても _defaults.yaml にあれば検証パス。"""
        defaults = "phase: spec\n"
        unit = (
            "unit: U1\n"
            "aim: aim\n"
            "rule:\n  - r\n"
            "link:\n  up: []\n  down: []\n"
            "core: true\n"
            "io:\n  in:\n    - i\n  process:\n    - p\n  out:\n    - o\n"
            "executor:\n  type: script\n  reason: r\n"
            "status: stable\n"
        )
        result = run_validate(_ValidateArgs(self._setup(tmp_path, defaults, unit)))
        assert result == 0

    def test_executor_inherited_from_defaults(self, tmp_path, capsys):
        """unit に executor が無くても _defaults.yaml にあれば検証パス。"""
        defaults = "executor:\n  type: script\n  reason: 共通\n"
        unit = (
            "unit: U1\n"
            "aim: aim\n"
            "phase: spec\n"
            "rule:\n  - r\n"
            "link:\n  up: []\n  down: []\n"
            "core: true\n"
            "io:\n  in:\n    - i\n  process:\n    - p\n  out:\n    - o\n"
            "status: stable\n"
        )
        result = run_validate(_ValidateArgs(self._setup(tmp_path, defaults, unit)))
        assert result == 0

    def test_required_field_still_missing_after_merge(self, tmp_path, capsys):
        """defaults でも補えていない必須フィールドはエラーになる。"""
        defaults = "phase: spec\n"
        # aim が unit にも defaults にもない
        unit = (
            "unit: U1\n"
            "rule:\n  - r\n"
            "link:\n  up: []\n  down: []\n"
            "core: true\n"
            "io:\n  in:\n    - i\n  process:\n    - p\n  out:\n    - o\n"
            "executor:\n  type: script\n  reason: r\n"
            "status: stable\n"
        )
        result = run_validate(_ValidateArgs(self._setup(tmp_path, defaults, unit)))
        err = capsys.readouterr().out + capsys.readouterr().err
        assert result == 1
        # aim が未設定なので必須フィールド欠落エラーが残る
        assert "aim" in err or "aim" in capsys.readouterr().out
