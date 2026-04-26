from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.validate import _check_file, _check_process


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
    job: list | None = None,
    rule: list | None = None,
    io_in: list | None = None,
    io_run: list | None = None,
    io_out: list | None = None,
) -> str:
    up    = up    if up    is not None else []
    down  = down  if down  is not None else []
    job   = job   if job   is not None else ["作業内容"]
    rule  = rule  if rule  is not None else ["制約"]
    io_in  = io_in  if io_in  is not None else ["入力"]
    io_run = io_run if io_run is not None else ["実行手順"]
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
        f"job:{_list_yaml(job)}\n"
        f"rule:{_list_yaml(rule)}\n"
        f"link:\n"
        f"  up:{_list_yaml(up)}\n"
        f"  down:{_list_yaml(down)}\n"
        f"core: {core_str}\n"
        f"io:\n"
        f"  in:{_list_yaml(io_in)}\n"
        f"  run:{_list_yaml(io_run)}\n"
        f"  out:{_list_yaml(io_out)}\n"
        f"executor:\n"
        f"  type: {executor_type}\n"
        f"  reason: {executor_reason}\n"
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

    def test_invalid_core_undetermined(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", core="undetermined"))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "core" for e in errors)

    def test_invalid_executor_type(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", executor_type="human"))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "executor.type" for e in errors)

    def test_missing_executor_reason(self, tmp_path):
        content = make_unit("TestUnit").replace("  reason: 定型処理のため\n", "")
        write_unit(tmp_path, "TestUnit", content)
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "executor.reason" for e in errors)

    def test_empty_job(self, tmp_path):
        write_unit(tmp_path, "TestUnit", make_unit("TestUnit", job=[]))
        errors, _ = _check_file(tmp_path / "TestUnit.yaml")
        assert any(e.field == "job" for e in errors)

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
