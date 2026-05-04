from __future__ import annotations

from pathlib import Path
import yaml
import pytest
from bizspec.new_cmd import run_new


class FakeArgs:
    def __init__(self, root, process, unit, executor=None, phase=None,
                 core=None, up=None, down=None, force=False):
        self.root     = root
        self.process  = process
        self.unit     = unit
        self.executor = executor
        self.phase    = phase
        self.core     = core
        self.up       = up
        self.down     = down
        self.force    = force


def make_args(tmp_path, process="my-proc", unit="MyUnit", **kwargs):
    (tmp_path / "bizspec").mkdir(exist_ok=True)
    return FakeArgs(root=str(tmp_path), process=process, unit=unit, **kwargs)


# ── 正常系 ────────────────────────────────────────────────────────────────────

class TestRunNew:
    def test_creates_yaml_file(self, tmp_path):
        args = make_args(tmp_path)
        assert run_new(args) == 0
        assert (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").exists()

    def test_yaml_has_required_fields(self, tmp_path):
        args = make_args(tmp_path)
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        for field in ("unit", "aim", "phase", "rule", "link", "core", "io", "executor", "status"):
            assert field in data, f"フィールド {field!r} がない"

    def test_unit_name_matches(self, tmp_path):
        args = make_args(tmp_path, unit="テストUnit")
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "テストUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["unit"] == "テストUnit"

    def test_executor_written(self, tmp_path):
        args = make_args(tmp_path, executor="ai_agent")
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["executor"]["type"] == "ai_agent"

    def test_phase_written(self, tmp_path):
        args = make_args(tmp_path, phase="dev")
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["phase"] == "dev"

    def test_core_written(self, tmp_path):
        args = make_args(tmp_path, core="true")
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["core"] is True

    def test_link_up_down_written(self, tmp_path):
        args = make_args(tmp_path, up=["UnitA"], down=["UnitB"])
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["link"]["up"] == ["UnitA"]
        assert data["link"]["down"] == ["UnitB"]

    def test_creates_process_dir_if_absent(self, tmp_path):
        args = make_args(tmp_path, process="new-proc")
        run_new(args)
        assert (tmp_path / "bizspec" / "new-proc").is_dir()

    def test_default_link_is_empty_list(self, tmp_path):
        args = make_args(tmp_path)
        run_new(args)
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["link"]["up"] == []
        assert data["link"]["down"] == []


# ── エラー系 ──────────────────────────────────────────────────────────────────

class TestRunNewErrors:
    def test_missing_bizspec_dir(self, tmp_path):
        args = FakeArgs(root=str(tmp_path), process="p", unit="U")
        assert run_new(args) == 1

    def test_existing_file_without_force(self, tmp_path):
        args = make_args(tmp_path)
        run_new(args)
        assert run_new(args) == 1

    def test_force_overwrites(self, tmp_path):
        args = make_args(tmp_path)
        run_new(args)
        args2 = make_args(tmp_path, executor="script", force=True)
        assert run_new(args2) == 0
        data = yaml.safe_load(
            (tmp_path / "bizspec" / "my-proc" / "MyUnit.yaml").read_text(encoding="utf-8")
        )
        assert data["executor"]["type"] == "script"
