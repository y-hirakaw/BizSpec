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
        f"job:\n  - 作業\n"
        f"rule:\n  - 制約\n"
        f"link:\n"
        f"  up:{chr(10) + up_yaml if up_yaml else ' []'}\n"
        f"  down:{chr(10) + down_yaml if down_yaml else ' []'}\n"
        f"core: true\n"
        f"io:\n  in:\n    - 入力\n  run:\n    - 手順\n  out:\n    - 出力\n"
        f"executor:\n  type: script\n  reason: 定型処理\n"
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

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="A_new")
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

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="A_new")
        run_rename(args)

        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A_new" in b_data["link"]["up"]
        assert "A" not in b_data["link"]["up"]

    def test_preserves_numbering_prefix(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        (pd / "A.yaml").rename(pd / "01_A.yaml")

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="A_new")
        rc = run_rename(args)
        assert rc == 0
        assert (pd / "01_A_new.yaml").exists()
        assert not (pd / "01_A.yaml").exists()

    def test_dry_run_makes_no_changes(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="A_new", dry_run=True)
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

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="B")
        rc = run_rename(args)
        assert rc == 1

    def test_missing_unit_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="NoExist", new_name="X")
        assert run_rename(args) == 1

    def test_same_name_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], [])
        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="A", new_name="A")
        assert run_rename(args) == 1

    def test_three_unit_chain(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], ["C"])
        write_unit(pd, "C", ["B"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", old_name="B", new_name="B_new")
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

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="A")
        rc = run_rm(args)
        assert rc == 0
        assert not (pd / "A.yaml").exists()

    def test_removes_link_references(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="A", force=True)
        rc = run_rm(args)
        assert rc == 0

        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A" not in b_data["link"]["up"]

    def test_warns_and_aborts_on_disconnection(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="A")
        rc = run_rm(args)
        # B の link.up が空になる → warn + abort
        assert rc == 1
        assert (pd / "A.yaml").exists()

    def test_force_proceeds_despite_disconnection(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="A", force=True)
        rc = run_rm(args)
        assert rc == 0
        assert not (pd / "A.yaml").exists()

    def test_dry_run_makes_no_changes(self, tmp_path):
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="A", dry_run=True)
        rc = run_rm(args)
        assert rc == 0
        assert (pd / "A.yaml").exists()
        b_data = yaml.safe_load((pd / "B.yaml").read_text())
        assert "A" in b_data["link"]["up"]

    def test_missing_unit_returns_error(self, tmp_path):
        pd = make_process(tmp_path)
        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="NoExist")
        assert run_rm(args) == 1

    def test_middle_unit_removal_updates_both_neighbors(self, tmp_path):
        """A → B → C で B を削除 → A.down, C.up から B が消える。"""
        pd = make_process(tmp_path)
        write_unit(pd, "A", [], ["B"])
        write_unit(pd, "B", ["A"], ["C"])
        write_unit(pd, "C", ["B"], [])

        args = FakeArgs(root=str(tmp_path), process="test-proc", unit_name="B", force=True)
        rc = run_rm(args)
        assert rc == 0

        a_data = yaml.safe_load((pd / "A.yaml").read_text())
        c_data = yaml.safe_load((pd / "C.yaml").read_text())
        assert "B" not in a_data["link"]["down"]
        assert "B" not in c_data["link"]["up"]
