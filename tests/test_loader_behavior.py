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
        f"rule:\n  - r\n"
        f"link:\n  up: []\n  down: []\n"
        f"core: true\n"
        f"io:\n  in:\n    - i\n  process:\n    - r\n  out:\n    - o\n"
        f"executor:\n  type: script\n  reason: r\n"
        f"status: stable\n"
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


# ── _defaults.yaml 継承 ───────────────────────────────────────────────────────
# プロセス直下の _defaults.yaml に書いた共通フィールドが、unit YAML に書かれて
# いない場合だけ補完される。unit 側に同名フィールドがあれば unit が勝つ。
# unit ファイル自体は書き換わらない（読み出し時にのみマージされる）。

from bizspec.core import apply_defaults, load_process_defaults


def _minimal_unit(name: str, **overrides: str) -> str:
    """defaults からの継承を観察するため、最低限必要なフィールドだけ書いた YAML。"""
    body = (
        f"unit: {name}\n"
        f"aim: aim\n"
        f"rule:\n  - r\n"
        f"link:\n  up: []\n  down: []\n"
        f"core: true\n"
        f"io:\n  in:\n    - i\n  process:\n    - r\n  out:\n    - o\n"
    )
    # 上書きしたい項目があれば末尾に足す
    for k, v in overrides.items():
        body += f"{k}: {v}\n"
    return body


class TestProcessDefaults:
    def test_apply_defaults_unit_wins(self):
        """unit 側に同名フィールドがあれば unit が勝つ。"""
        merged = apply_defaults(
            {"phase": "dev", "executor": {"type": "ai_agent"}},
            {"phase": "spec", "executor": {"type": "script", "reason": "default"}},
        )
        assert merged["phase"] == "dev"
        # nested dict は再帰マージされ、unit が持たないキー（reason）は default が補完
        assert merged["executor"] == {"type": "ai_agent", "reason": "default"}

    def test_apply_defaults_returns_unit_when_no_defaults(self):
        u = {"phase": "spec"}
        assert apply_defaults(u, {}) is u

    def test_load_process_defaults_missing(self, tmp_path):
        """_defaults.yaml が無ければ空 dict。"""
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        assert load_process_defaults(proc) == {}

    def test_load_process_defaults_invalid(self, tmp_path):
        """壊れた _defaults.yaml は黙殺して空 dict（loader の既存契約に揃える）。"""
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        (proc / "_defaults.yaml").write_text(": : :\n  bad", encoding="utf-8")
        assert load_process_defaults(proc) == {}

    def test_list_inherits_executor_from_defaults(self, tmp_path, capsys):
        """unit に executor を書かなくても _defaults.yaml の値で list が動くこと。"""
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        (proc / "_defaults.yaml").write_text(
            "phase: spec\n"
            "executor:\n  type: ai_agent\n  reason: 共通\n"
            "status: stable\n",
            encoding="utf-8",
        )
        _write(proc, "U1", _minimal_unit("U1"))
        result = run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert result is None or result == 0
        assert "U1" in out
        # list は unit 名と executor.type を表示する
        assert "ai_agent" in out

    def test_unit_field_overrides_defaults(self, tmp_path, capsys):
        """unit 側に書かれたフィールドは defaults より優先。"""
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        (proc / "_defaults.yaml").write_text(
            "phase: spec\n"
            "executor:\n  type: ai_agent\n  reason: default\n"
            "status: stable\n",
            encoding="utf-8",
        )
        # U1 は executor.type を script で上書き
        body = _minimal_unit("U1") + "executor:\n  type: script\n  reason: 個別\n" + "status: stable\n"
        _write(proc, "U1", body)
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        assert "script" in out
        assert "ai_agent" not in out

    def test_defaults_file_not_loaded_as_unit(self, tmp_path, capsys):
        """_defaults.yaml は unit ファイルとして読まれない（_ プレフィックスの既存契約）。"""
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        (proc / "_defaults.yaml").write_text("phase: spec\n", encoding="utf-8")
        _write(proc, "U1", _minimal_unit("U1") + "phase: dev\nexecutor:\n  type: script\n  reason: r\nstatus: stable\n")
        run_list(_ListArgs(tmp_path))
        out = capsys.readouterr().out
        # unit U1 のみが出力に現れる
        assert "U1" in out
        # _defaults.yaml は unit として表示されない
        assert "_defaults" not in out
