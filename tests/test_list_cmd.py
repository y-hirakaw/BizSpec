from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.list_cmd import _load_units, run_list


# ── ヘルパー ──────────────────────────────────────────────────────────────────

def write_yaml(dir: Path, name: str, content: str) -> Path:
    path = dir / f"{name}.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def make_yaml(name: str, core: bool = True, executor_type: str = "script") -> str:
    core_str = "true" if core else "false"
    return (
        f"unit: {name}\naim: テスト\nphase: spec\n"
        f"job:\n  - 作業\nrule:\n  - 制約\n"
        f"link:\n  up: []\n  down: []\n"
        f"core: {core_str}\n"
        f"io:\n  in:\n    - 入力\n  run:\n    - 実行\n  out:\n    - 出力\n"
        f"executor:\n  type: {executor_type}\n  reason: 理由\n"
    )


# ── _load_units ───────────────────────────────────────────────────────────────

class TestLoadUnits:
    def test_loads_all_yaml_files(self, tmp_path):
        write_yaml(tmp_path, "UnitA", make_yaml("UnitA"))
        write_yaml(tmp_path, "UnitB", make_yaml("UnitB"))
        units = _load_units(tmp_path)
        assert len(units) == 2

    def test_empty_dir(self, tmp_path):
        assert _load_units(tmp_path) == []

    def test_skips_broken_yaml(self, tmp_path):
        write_yaml(tmp_path, "UnitA", make_yaml("UnitA"))
        (tmp_path / "broken.yaml").write_text("key: [", encoding="utf-8")
        units = _load_units(tmp_path)
        assert len(units) == 1

    def test_skips_underscore_yaml(self, tmp_path):
        write_yaml(tmp_path, "UnitA", make_yaml("UnitA"))
        (tmp_path / "_process.yaml").write_text("name: テスト\n", encoding="utf-8")
        units = _load_units(tmp_path)
        assert len(units) == 1
        assert units[0]["unit"] == "UnitA"


# ── run_list ──────────────────────────────────────────────────────────────────

class FakeArgs:
    def __init__(self, root: str, process: str | None = None):
        self.root = root
        self.process = process


class TestRunList:
    def test_lists_all_processes(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "my-process"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitA", make_yaml("UnitA", core=True, executor_type="script"))
        write_yaml(proc, "UnitB", make_yaml("UnitB", core=False, executor_type="ai_agent"))

        result = run_list(FakeArgs(root=str(tmp_path)))
        captured = capsys.readouterr().out

        assert result == 0
        assert "my-process" in captured
        assert "UnitA" in captured
        assert "UnitB" in captured
        assert "true" in captured
        assert "false" in captured
        assert "script" in captured
        assert "ai_agent" in captured

    def test_filter_by_process(self, tmp_path, capsys):
        for name in ("proc-a", "proc-b"):
            d = tmp_path / "bizspec" / name
            d.mkdir(parents=True)
            write_yaml(d, "UnitX", make_yaml("UnitX"))

        run_list(FakeArgs(root=str(tmp_path), process="proc-a"))
        captured = capsys.readouterr().out

        assert "proc-a" in captured
        assert "proc-b" not in captured

    def test_missing_bizspec_dir(self, tmp_path):
        result = run_list(FakeArgs(root=str(tmp_path)))
        assert result == 1

    def test_missing_process(self, tmp_path):
        (tmp_path / "bizspec").mkdir()
        result = run_list(FakeArgs(root=str(tmp_path), process="nonexistent"))
        assert result == 1

    def test_shows_duration_column_when_present(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "my-proc"
        proc.mkdir(parents=True)
        content = make_yaml("UnitA") + "effort:\n  duration: 0.5\n"
        write_yaml(proc, "UnitA", content)

        run_list(FakeArgs(root=str(tmp_path)))
        captured = capsys.readouterr().out
        assert "duration" in captured
        assert "0.5h" in captured

    def test_shows_difficulty_column_when_present(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "my-proc"
        proc.mkdir(parents=True)
        content = make_yaml("UnitA") + "automation:\n  difficulty: high\n  status: manual\n"
        write_yaml(proc, "UnitA", content)

        run_list(FakeArgs(root=str(tmp_path)))
        captured = capsys.readouterr().out
        assert "difficulty" in captured
        assert "high" in captured

    def test_no_meta_columns_when_absent(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "my-proc"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitA", make_yaml("UnitA"))

        run_list(FakeArgs(root=str(tmp_path)))
        captured = capsys.readouterr().out
        assert "duration" not in captured
        assert "difficulty" not in captured
