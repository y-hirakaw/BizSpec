from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.renumber_cmd import _topological_sort, run_renumber


# ── ヘルパー ──────────────────────────────────────────────────────────────────

def write_unit(directory: Path, name: str, up: list[str], down: list[str]) -> None:
    up_yaml = "\n".join(f"    - {u}" for u in up) if up else ""
    down_yaml = "\n".join(f"    - {d}" for d in down) if down else ""
    up_block = f"\n{up_yaml}" if up_yaml else " []"
    down_block = f"\n{down_yaml}" if down_yaml else " []"
    content = (
        f"unit: {name}\n"
        f"aim: test\n"
        f"phase: spec\n"
        f"scope:\n  - 作業\n"
        f"rule:\n  - 制約\n"
        f"link:\n"
        f"  up:{up_block}\n"
        f"  down:{down_block}\n"
        f"core: true\n"
        f"io:\n  in:\n    - 入力\n  process:\n    - 手順\n  out:\n    - 出力\n"
        f"executor:\n  type: script\n  reason: 定型処理\n"
    )
    (directory / f"{name}.yaml").write_text(content, encoding="utf-8")


def make_process(tmp_path: Path, links: list[tuple[str, str]]) -> Path:
    """links: [(from, to), ...] の辺リストからプロセスを作る。"""
    process_dir = tmp_path / "bizspec" / "test-proc"
    process_dir.mkdir(parents=True)

    # ノード収集
    all_nodes: set[str] = set()
    downs: dict[str, list[str]] = {}
    ups: dict[str, list[str]] = {}
    for src, dst in links:
        all_nodes.add(src)
        all_nodes.add(dst)
        downs.setdefault(src, []).append(dst)
        ups.setdefault(dst, []).append(src)

    for node in all_nodes:
        write_unit(process_dir, node, ups.get(node, []), downs.get(node, []))
    return process_dir


class FakeArgs:
    def __init__(self, process: str, root: str, dry_run: bool = False):
        self.process = process
        self.root = root
        self.dry_run = dry_run


# ── _topological_sort ────────────────────────────────────────────────────────

class TestTopologicalSort:
    def _units(self, process_dir: Path) -> dict:
        from bizspec.renumber_cmd import _load_units
        return _load_units(process_dir)

    def test_linear_chain(self, tmp_path):
        """A → B → C の直列"""
        pd = make_process(tmp_path, [("A", "B"), ("B", "C")])
        units = self._units(pd)
        result = _topological_sort(units)
        assert result == ["A", "B", "C"]

    def test_fork_and_merge(self, tmp_path):
        """A → B, A → C, B → D, C → D の分岐合流"""
        pd = make_process(tmp_path, [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
        units = self._units(pd)
        result = _topological_sort(units)
        assert result[0] == "A"
        assert result[-1] == "D"
        assert set(result[1:3]) == {"B", "C"}

    def test_no_links(self, tmp_path):
        """link なし（孤立ノード）はアルファベット順"""
        pd = tmp_path / "bizspec" / "test-proc"
        pd.mkdir(parents=True)
        for name in ["C", "A", "B"]:
            write_unit(pd, name, [], [])
        from bizspec.renumber_cmd import _load_units
        units = _load_units(pd)
        result = _topological_sort(units)
        assert result == ["A", "B", "C"]


# ── run_renumber ─────────────────────────────────────────────────────────────

class TestRunRenumber:
    def test_basic_rename(self, tmp_path):
        """直列フローをリネームして採番される"""
        make_process(tmp_path, [("A", "B"), ("B", "C")])
        args = FakeArgs("test-proc", str(tmp_path))
        rc = run_renumber(args)
        assert rc == 0
        process_dir = tmp_path / "bizspec" / "test-proc"
        names = sorted(p.name for p in process_dir.glob("*.yaml"))
        assert names == ["01_A.yaml", "02_B.yaml", "03_C.yaml"]

    def test_dry_run_no_rename(self, tmp_path):
        """--dry-run ではファイルが変わらない"""
        make_process(tmp_path, [("A", "B")])
        args = FakeArgs("test-proc", str(tmp_path), dry_run=True)
        rc = run_renumber(args)
        assert rc == 0
        process_dir = tmp_path / "bizspec" / "test-proc"
        names = {p.name for p in process_dir.glob("*.yaml")}
        assert names == {"A.yaml", "B.yaml"}

    def test_already_numbered_no_change(self, tmp_path):
        """正しく採番済みなら変更なし"""
        make_process(tmp_path, [("A", "B")])
        args = FakeArgs("test-proc", str(tmp_path))
        run_renumber(args)  # first run
        rc = run_renumber(args)  # second run
        assert rc == 0
        process_dir = tmp_path / "bizspec" / "test-proc"
        names = sorted(p.name for p in process_dir.glob("*.yaml"))
        assert names == ["01_A.yaml", "02_B.yaml"]

    def test_reorder_updates_filenames(self, tmp_path):
        """既存のプレフィックスが間違っていても正しく上書きされる"""
        process_dir = tmp_path / "bizspec" / "test-proc"
        process_dir.mkdir(parents=True)
        # 逆順に手動採番してから renumber
        write_unit(process_dir, "A", [], ["B"])
        write_unit(process_dir, "B", ["A"], [])
        # 先に B を 01_ にしておく（意図的に誤順）
        (process_dir / "B.yaml").rename(process_dir / "01_B.yaml")
        (process_dir / "A.yaml").rename(process_dir / "02_A.yaml")

        args = FakeArgs("test-proc", str(tmp_path))
        rc = run_renumber(args)
        assert rc == 0
        names = sorted(p.name for p in process_dir.glob("*.yaml"))
        assert names == ["01_A.yaml", "02_B.yaml"]

    def test_missing_process_returns_error(self, tmp_path):
        (tmp_path / "bizspec").mkdir()
        args = FakeArgs("no-such", str(tmp_path))
        assert run_renumber(args) == 1


# ── validate との統合: プレフィックス付きファイルを検証できる ─────────────────

class TestValidateWithPrefixedFiles:
    def test_prefixed_files_pass_filename_check(self, tmp_path):
        from bizspec.validate import _check_file
        path = tmp_path / "01_MyUnit.yaml"
        path.write_text(
            "unit: MyUnit\naim: test\nphase: spec\n"
            "scope:\n  - 作業\nrule:\n  - 制約\n"
            "link:\n  up: []\n  down: []\ncore: true\n"
            "io:\n  in:\n    - 入力\n  process:\n    - 手順\n  out:\n    - 出力\n"
            "executor:\n  type: script\n  reason: 定型処理\n",
            encoding="utf-8",
        )
        errors, _ = _check_file(path)
        filename_errors = [e for e in errors if e.field == "unit"]
        assert filename_errors == []

    def test_wrong_prefix_unit_fails(self, tmp_path):
        from bizspec.validate import _check_file
        path = tmp_path / "01_WrongName.yaml"
        path.write_text(
            "unit: CorrectName\naim: test\nphase: spec\n"
            "scope:\n  - 作業\nrule:\n  - 制約\n"
            "link:\n  up: []\n  down: []\ncore: true\n"
            "io:\n  in:\n    - 入力\n  process:\n    - 手順\n  out:\n    - 出力\n"
            "executor:\n  type: script\n  reason: 定型処理\n",
            encoding="utf-8",
        )
        errors, _ = _check_file(path)
        filename_errors = [e for e in errors if e.field == "unit"]
        assert len(filename_errors) == 1
