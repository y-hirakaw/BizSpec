"""
YAML 読み込み層の挙動テスト。

list / viz / search の各コマンドは現状それぞれが独自に YAML 読み込み
ロジック (`_load_units` 等) を持つ。これを `bizspec.core` 配下の共有
loader へ抽出する際、外部から見た挙動が変わらないことを保証するため
の網。コマンド経由で観察できる契約のみを検証する。
"""

from __future__ import annotations

from pathlib import Path

from bizspec.list_cmd import run_list
from bizspec.search_cmd import run_search
from bizspec.viz_cmd import run_viz


def _write(dir: Path, name: str, body: str) -> Path:
    dir.mkdir(parents=True, exist_ok=True)
    f = dir / f"{name}.yaml"
    f.write_text(body, encoding="utf-8")
    return f


def _valid_unit(name: str) -> str:
    return (
        f"unit: {name}\n"
        f"aim: aim\n"
        f"phase: spec\n"
        f"job:\n  - 作業\n"
        f"rule:\n  - r\n"
        f"link:\n  up: []\n  down: []\n"
        f"core: true\n"
        f"io:\n  in:\n    - i\n  run:\n    - r\n  out:\n    - o\n"
        f"executor:\n  type: script\n  reason: r\n"
    )


class _ListArgs:
    def __init__(self, root, process=None, refactor=False, format="text"):
        self.root = str(root)
        self.process = process
        self.refactor = refactor
        self.format = format


class _SearchArgs:
    def __init__(self, root, keyword, field=None):
        self.root = str(root)
        self.keyword = keyword
        self.field = field


class _VizArgs:
    def __init__(self, root, process=None):
        self.root = str(root)
        self.process = process


# ── 壊れた YAML の扱い ─────────────────────────────────────────────────────────
# 現挙動: parse 失敗は黙殺され、有効ファイルだけが処理される。これを契約として固定。

class TestMalformedYamlSilentlySkipped:
    def _setup(self, tmp_path):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "valid", _valid_unit("ValidUnit"))
        _write(proc, "broken", "this: is: : not: valid: : :\n  - bad")
        return tmp_path

    def test_list_does_not_crash(self, tmp_path, capsys):
        result = run_list(_ListArgs(self._setup(tmp_path)))
        out = capsys.readouterr().out
        assert result is None or result == 0
        assert "ValidUnit" in out

    def test_viz_does_not_crash(self, tmp_path, capsys):
        result = run_viz(_VizArgs(self._setup(tmp_path)))
        capsys.readouterr()  # discard
        assert result == 0

    def test_search_does_not_crash(self, tmp_path, capsys):
        result = run_search(_SearchArgs(self._setup(tmp_path), keyword="ValidUnit"))
        out = capsys.readouterr().out
        assert result is None or result == 0
        assert "ValidUnit" in out


# ── dict でない YAML / unit キー欠落 ──────────────────────────────────────────

class TestNonUnitYamlSkipped:
    def test_list_yaml_top_level(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "valid", _valid_unit("Real"))
        _write(proc, "list_yaml", "- item1\n- item2\n")
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert "Real" in out

    def test_dict_without_unit_key(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "valid", _valid_unit("Real"))
        _write(proc, "no_unit", "aim: only aim\nphase: spec\n")
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert "Real" in out
        # The non-unit file should not appear as a unit name
        assert "no_unit" not in out

    def test_empty_yaml_file(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "valid", _valid_unit("Real"))
        _write(proc, "empty", "")
        result = run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert result is None or result == 0
        assert "Real" in out


# ── _ prefix ファイル ──────────────────────────────────────────────────────────

class TestUnderscorePrefix:
    def test_underscore_files_skipped(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "Real", _valid_unit("Real"))
        _write(proc, "_template", _valid_unit("Template"))
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert "Real" in out
        assert "Template" not in out

    def test_underscore_files_skipped_in_search(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "proc-a"
        _write(proc, "Real", _valid_unit("Real"))
        _write(proc, "_skipped", _valid_unit("ShouldNotMatch"))
        run_search(_SearchArgs(tmp_path, keyword="ShouldNotMatch"))
        out = capsys.readouterr().out
        # Should report "not found" rather than match the unit in the underscore file
        assert "見つかりませんでした" in out


# ── Unicode / 日本語 ──────────────────────────────────────────────────────────

class TestUnicodeNames:
    def test_japanese_unit_name(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "プロセスA"
        _write(proc, "ユニット壱", _valid_unit("ユニット壱"))
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert "ユニット壱" in out
        assert "プロセスA" in out

    def test_japanese_search_keyword(self, tmp_path, capsys):
        proc = tmp_path / "bizspec" / "プロセスA"
        _write(proc, "ユニット壱", _valid_unit("ユニット壱"))
        run_search(_SearchArgs(tmp_path, keyword="ユニット壱"))
        out = capsys.readouterr().out
        assert "ユニット壱" in out


# ── 空 / 異常ディレクトリ ──────────────────────────────────────────────────────

class TestEmptyAndMissing:
    def test_empty_process_directory(self, tmp_path, capsys):
        (tmp_path / "bizspec" / "empty").mkdir(parents=True)
        result = run_list(_ListArgs(tmp_path))
        # should not crash
        assert result is None or result == 0

    def test_no_bizspec_dir_list(self, tmp_path, capsys):
        result = run_list(_ListArgs(tmp_path))
        # behavior: returns error code or prints warning, but does not raise
        assert result is None or isinstance(result, int)
