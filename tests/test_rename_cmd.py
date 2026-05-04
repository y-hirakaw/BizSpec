from __future__ import annotations

from pathlib import Path
import pytest
import yaml
from bizspec.rename_cmd import run_rename, run_rm


# ── ヘルパー ──────────────────────────────────────────────────────────────────

def write_unit(directory: Path, name: str, up: list[str], down: list[str]) -> None:
    up_yaml = "\n".join(f"    - {u}" for u in up) if up else ""
    down_yaml = "\n".join(f"    - {d}" for d in down) if down else ""
    content = (
        f"unit: {name}\n"
        f"aim: test\n"
        f"phase: spec\n"
        f"rule:\n  - 制約\n"
        f"link:\n"
        f"  up:{chr(10) + up_yaml if up_yaml else ' []'}\n"
        f"  down:{chr(10) + down_yaml if down_yaml else ' []'}\n"
        f"core: true\n"
        f"io:\n  in:\n    - 入力\n  process:\n    - 手順\n  out:\n    - 出力\n"
        f"executor:\n  type: script\n  reason: 定型処理\n"
        f"status: stable\n"
    )
    (directory / f"{name}.yaml").write_text(content, encoding="utf-8")


def make_process(tmp_path: Path, name: str = "test-proc") -> Path:
    pd = tmp_path / "bizspec" / name
    pd.mkdir(parents=True)
    return pd


class FakeArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.root = getattr(self, "root", str(getattr(self, "_tmp", ".")))
        self.dry_run = getattr(self, "dry_run", False)
        self.force = getattr(self, "force", False)


# ── bizspec rename ────────────────────────────────────────────────────────────

class TestRename:
    def test_renames_file_and_unit_field(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A_new")
        rc = run_rename(args)
        assert rc == 0

        assert not (pd / "A.yaml").exists()
        assert (pd / "A_new.yaml").exists()
        data = yaml.safe_load((pd / "A_new.yaml").read_text())
        assert data["unit"] == "A_new"

    def test_updates_link_references(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A_new")
        run_rename(args)

        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A_new" in b_data["link"]["up"]
        assert "A" not in b_data["link"]["up"]

    def test_preserves_numbering_prefix(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        (pd / "A.yaml").rename(pd / "01_A.yaml")

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A_new")
        rc = run_rename(args)
        assert rc == 0
        assert (pd / "01_A_new.yaml").exists()
        assert not (pd / "01_A.yaml").exists()

    def test_dry_run_makes_no_changes(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A_new", dry_run=True)
        rc = run_rename(args)
        assert rc == 0
        assert (pd / "A.yaml").exists()
        assert not (pd / "A_new.yaml").exists()
        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A" in b_data["link"]["up"]

    def test_conflict_with_existing_unit(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        write_unit(pd, "B", [], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="B")
        rc = run_rename(args)
        assert rc == 1

    def test_missing_unit_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        args = FakeArgs(root=str(tmp_path), process="test-proc", old="NoExist", new="X")
        assert run_rename(args) == 1

    def test_same_name_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A")
        assert run_rename(args) == 1

    def test_three_unit_chain(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], ["C"])
        write_unit(pd, "C", ["B"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old="B", new="B_new")
        rc = run_rename(args)
        assert rc == 0

        a_data = yaml.safe_load((pd / "A.yaml").read_text())
        c_data = yaml.safe_load((pd / "C.yaml").read_text())
        assert "B_new" in a_data["link"]["down"]
        assert "B_new" in c_data["link"]["up"]


# ── bizspec rm ───────────────────────────────────────────────────────────────

class TestRm:
    def test_deletes_file(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="A")
        rc = run_rm(args)
        assert rc == 0
        assert not (pd / "A.yaml").exists()

    def test_removes_link_references(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="A", force=True)
        rc = run_rm(args)
        assert rc == 0

        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A" not in b_data["link"]["up"]

    def test_warns_and_aborts_on_disconnection(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="A")
        rc = run_rm(args)
        # B の link.up が空になる → warn + abort
        assert rc == 1
        assert (pd / "A.yaml").exists()

    def test_force_proceeds_despite_disconnection(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="A", force=True)
        rc = run_rm(args)
        assert rc == 0
        assert not (pd / "A.yaml").exists()

    def test_dry_run_makes_no_changes(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="A", dry_run=True)
        rc = run_rm(args)
        assert rc == 0
        assert (pd / "A.yaml").exists()
        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A" in b_data["link"]["up"]

    def test_missing_unit_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="NoExist")
        assert run_rm(args) == 1

    def test_middle_unit_removal_updates_both_neighbors(self, tmp_path):
        """A → B → C で B を削除 → A.down, C.up から B が消える。"""
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], ["C"])
        write_unit(pd, "C", ["B"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="B", force=True)
        rc = run_rm(args)
        assert rc == 0

        a_data = yaml.safe_load((pd / "A.yaml").read_text())
        c_data = yaml.safe_load((pd / "C.yaml").read_text())
        assert "B" not in a_data["link"]["down"]
        assert "B" not in c_data["link"]["up"]


# ── 失敗パス（rename / rm の error / warn 系） ─────────────────────────────────

class TestRenameFailures:
    def test_no_bizspec_dir(self, tmp_path, capsys):
        args = FakeArgs(root=str(tmp_path), process="x", old="A", new="B")
        rc = run_rename(args)
        assert rc == 1
        assert "が見つかりません" in capsys.readouterr().err

    def test_process_dir_not_found(self, tmp_path, capsys):
        (tmp_path / "bizspec").mkdir()
        args = FakeArgs(root=str(tmp_path), process="missing", old="A", new="B")
        rc = run_rename(args)
        assert rc == 1
        assert "プロセス" in capsys.readouterr().err

    def test_same_name_rejected(self, tmp_path, capsys):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="A")
        rc = run_rename(args)
        assert rc == 1
        assert "同じ" in capsys.readouterr().err

    def test_old_unit_not_found(self, tmp_path, capsys):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", old="Missing", new="X")
        rc = run_rename(args)
        assert rc == 1
        assert "見つかりません" in capsys.readouterr().err

    def test_new_name_already_exists(self, tmp_path, capsys):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        write_unit(pd, "B", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", old="A", new="B")
        rc = run_rename(args)
        assert rc == 1
        assert "すでに存在" in capsys.readouterr().err

    def test_dry_run_warns_about_external_depends_on(self, tmp_path, capsys):
        pd = make_process(tmp_path, name="proc-a")
        write_unit(pd, "X", [], [])
        # proc-b 側に depends_on で proc-a:X を参照
        pd_b = tmp_path / "bizspec" / "proc-b"
        pd_b.mkdir()
        (pd_b / "P.yaml").write_text(
            "unit: P\naim: t\nphase: spec\n"
            "rule:\n  - r\n"
            "link:\n  up: []\n  down: []\n"
            "core: true\n"
            "io:\n  in:\n    - i\n  process:\n    - r\n  out:\n    - o\n"
            "executor:\n  type: script\n  reason: r\n"
            "status: stable\n"
            "depends_on:\n  - proc-a:X\n",
            encoding="utf-8",
        )
        args = FakeArgs(root=str(tmp_path), process="proc-a",
                        old="X", new="X_new", dry_run=True)
        rc = run_rename(args)
        out = capsys.readouterr().out
        assert rc == 0
        assert "depends_on" in out
        assert "P.yaml" in out


class TestRmFailures:
    def test_no_bizspec_dir(self, tmp_path, capsys):
        args = FakeArgs(root=str(tmp_path), process="x", unit="A")
        rc = run_rm(args)
        assert rc == 1
        assert "が見つかりません" in capsys.readouterr().err

    def test_process_dir_not_found(self, tmp_path, capsys):
        (tmp_path / "bizspec").mkdir()
        args = FakeArgs(root=str(tmp_path), process="missing", unit="A")
        rc = run_rm(args)
        assert rc == 1
        assert "プロセス" in capsys.readouterr().err

    def test_unit_not_found(self, tmp_path, capsys):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="Missing")
        rc = run_rm(args)
        assert rc == 1
        assert "見つかりません" in capsys.readouterr().err

    def test_disconnect_blocks_without_force(self, tmp_path, capsys):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", unit="B")
        rc = run_rm(args)
        out = capsys.readouterr().out
        assert rc == 1
        assert "分断" in out
        assert "--force" in out
        # B should still exist (not deleted)
        assert (pd / "B.yaml").exists()

    def test_external_deps_warning_after_rm(self, tmp_path, capsys):
        pd = make_process(tmp_path, name="proc-a")
        write_unit(pd, "X", [], [])
        pd_b = tmp_path / "bizspec" / "proc-b"
        pd_b.mkdir()
        (pd_b / "P.yaml").write_text(
            "unit: P\naim: t\nphase: spec\n"
            "rule:\n  - r\n"
            "link:\n  up: []\n  down: []\n"
            "core: true\n"
            "io:\n  in:\n    - i\n  process:\n    - r\n  out:\n    - o\n"
            "executor:\n  type: script\n  reason: r\n"
            "status: stable\n"
            "depends_on:\n  - proc-a:X\n",
            encoding="utf-8",
        )
        args = FakeArgs(root=str(tmp_path), process="proc-a", unit="X")
        rc = run_rm(args)
        out = capsys.readouterr().out
        # rm proceeds (no link disconnect since X is isolated in proc-a)
        assert "depends_on" in out
        assert "手動で更新" in out
