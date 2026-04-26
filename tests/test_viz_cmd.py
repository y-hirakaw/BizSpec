from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.viz_cmd import (
    _topo_levels,
    _compute_layout,
    _build_edges,
    _generate_html,
    run_viz,
    NODE_W, NODE_H, H_GAP, V_GAP,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def make_unit(name: str, up=None, down=None, core=True, executor_type="script") -> dict:
    return {
        "unit": name, "aim": f"{name}のaim", "phase": "spec", "core": core,
        "job": ["作業"], "rule": ["制約"],
        "io": {"in": ["入力"], "run": ["実行"], "out": ["出力"]},
        "executor": {"type": executor_type, "reason": "理由"},
        "link": {"up": up or [], "down": down or []},
    }


def make_yaml(name: str, up=None, down=None, core: bool = True, executor_type: str = "script") -> str:
    core_str = "true" if core else "false"
    up_items  = "\n".join(f"    - {u}" for u in (up  or []))
    down_items = "\n".join(f"    - {d}" for d in (down or []))
    return (
        f"unit: {name}\naim: テスト\nphase: spec\n"
        f"job:\n  - 作業\nrule:\n  - 制約\n"
        f"link:\n  up:\n{up_items or '    []'}\n  down:\n{down_items or '    []'}\n"
        f"core: {core_str}\n"
        f"io:\n  in:\n    - 入力\n  run:\n    - 実行\n  out:\n    - 出力\n"
        f"executor:\n  type: {executor_type}\n  reason: 理由\n"
    )


def write_yaml(dir: Path, name: str, content: str) -> Path:
    path = dir / f"{name}.yaml"
    path.write_text(content, encoding="utf-8")
    return path


class FakeArgs:
    def __init__(self, root: str, process: str | None = None):
        self.root = root
        self.process = process


# ── _topo_levels ──────────────────────────────────────────────────────────────

class TestTopoLevels:
    def test_linear_chain(self):
        units = [
            make_unit("A", down=["B"]),
            make_unit("B", up=["A"], down=["C"]),
            make_unit("C", up=["B"]),
        ]
        levels = _topo_levels(units)
        assert levels == [["A"], ["B"], ["C"]]

    def test_branch(self):
        units = [
            make_unit("A", down=["B", "C"]),
            make_unit("B", up=["A"]),
            make_unit("C", up=["A"]),
        ]
        levels = _topo_levels(units)
        assert levels[0] == ["A"]
        assert sorted(levels[1]) == ["B", "C"]

    def test_single_unit(self):
        units = [make_unit("A")]
        assert _topo_levels(units) == [["A"]]

    def test_disconnected_units(self):
        units = [make_unit("A"), make_unit("B")]
        levels = _topo_levels(units)
        assert len(levels) == 1
        assert sorted(levels[0]) == ["A", "B"]

    def test_unknown_link_ignored(self):
        units = [make_unit("A", down=["NonExistent"])]
        levels = _topo_levels(units)
        assert levels == [["A"]]


# ── _compute_layout ───────────────────────────────────────────────────────────

class TestComputeLayout:
    def test_single_node(self):
        positions, w, h = _compute_layout([["A"]])
        assert "A" in positions
        assert positions["A"]["top"] == 24
        assert h == 24 + NODE_H + 24

    def test_linear_chain_top_ordering(self):
        levels = [["A"], ["B"], ["C"]]
        positions, w, h = _compute_layout(levels)
        assert positions["A"]["top"] < positions["B"]["top"] < positions["C"]["top"]

    def test_branch_same_top(self):
        levels = [["A"], ["B", "C"]]
        positions, w, h = _compute_layout(levels)
        assert positions["B"]["top"] == positions["C"]["top"]
        assert positions["B"]["left"] < positions["C"]["left"]

    def test_canvas_height_grows_with_levels(self):
        _, _, h1 = _compute_layout([["A"]])
        _, _, h2 = _compute_layout([["A"], ["B"]])
        assert h2 > h1

    def test_canvas_width_grows_with_siblings(self):
        _, w1, _ = _compute_layout([["A"]])
        _, w2, _ = _compute_layout([["A", "B", "C"]])
        assert w2 >= w1

    def test_vertical_gap_between_levels(self):
        levels = [["A"], ["B"]]
        positions, _, _ = _compute_layout(levels)
        diff = positions["B"]["top"] - positions["A"]["top"]
        assert diff == NODE_H + V_GAP


# ── _build_edges ──────────────────────────────────────────────────────────────

class TestBuildEdges:
    def test_simple_edge(self):
        units = [make_unit("A", down=["B"]), make_unit("B")]
        positions = {"A": {"left": 0, "top": 0}, "B": {"left": 0, "top": 110}}
        edges = _build_edges(units, positions)
        assert ["A", "B"] in edges

    def test_no_duplicate_edges(self):
        units = [make_unit("A", down=["B"]), make_unit("B", up=["A"])]
        positions = {"A": {"left": 0, "top": 0}, "B": {"left": 0, "top": 110}}
        edges = _build_edges(units, positions)
        assert edges.count(["A", "B"]) == 1

    def test_unknown_target_skipped(self):
        units = [make_unit("A", down=["Ghost"])]
        positions = {"A": {"left": 0, "top": 0}}
        edges = _build_edges(units, positions)
        assert edges == []


# ── _generate_html ────────────────────────────────────────────────────────────

class TestGenerateHtml:
    def test_produces_html(self):
        units = [make_unit("UnitA")]
        html = _generate_html("my-proc", units)
        assert "<!DOCTYPE html>" in html

    def test_process_name_in_title(self):
        units = [make_unit("UnitA")]
        html = _generate_html("my-proc", units)
        assert "my-proc" in html

    def test_unit_data_embedded(self):
        units = [make_unit("SpecialUnit")]
        html = _generate_html("my-proc", units)
        assert "SpecialUnit" in html

    def test_unit_count_in_header(self):
        units = [make_unit("A"), make_unit("B")]
        html = _generate_html("my-proc", units)
        assert "2 units" in html

    def test_empty_units_returns_empty(self):
        assert _generate_html("my-proc", []) == ""

    def test_no_placeholder_tokens_remain(self):
        units = [make_unit("A", down=["B"]), make_unit("B", up=["A"])]
        html = _generate_html("my-proc", units)
        assert "__" not in html


# ── run_viz ───────────────────────────────────────────────────────────────────

class TestRunViz:
    def test_generates_html_file(self, tmp_path):
        proc = tmp_path / "bizspec" / "my-proc"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitA", make_yaml("UnitA"))

        result = run_viz(FakeArgs(root=str(tmp_path)))
        assert result == 0
        out = tmp_path / "bizspec" / "_viz" / "my-proc.html"
        assert out.exists()
        assert "UnitA" in out.read_text(encoding="utf-8")

    def test_filter_by_process(self, tmp_path):
        for name in ("proc-a", "proc-b"):
            d = tmp_path / "bizspec" / name
            d.mkdir(parents=True)
            write_yaml(d, "UnitX", make_yaml("UnitX"))

        result = run_viz(FakeArgs(root=str(tmp_path), process="proc-a"))
        assert result == 0
        assert (tmp_path / "bizspec" / "_viz" / "proc-a.html").exists()
        assert not (tmp_path / "bizspec" / "_viz" / "proc-b.html").exists()

    def test_missing_bizspec_dir(self, tmp_path):
        result = run_viz(FakeArgs(root=str(tmp_path)))
        assert result == 1

    def test_missing_process(self, tmp_path):
        (tmp_path / "bizspec").mkdir()
        result = run_viz(FakeArgs(root=str(tmp_path), process="nonexistent"))
        assert result == 1

    def test_creates_viz_dir(self, tmp_path):
        proc = tmp_path / "bizspec" / "proc"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitA", make_yaml("UnitA"))

        run_viz(FakeArgs(root=str(tmp_path)))
        assert (tmp_path / "bizspec" / "_viz").is_dir()

    def test_skips_underscore_dirs(self, tmp_path):
        (tmp_path / "bizspec" / "_internal").mkdir(parents=True)
        write_yaml(tmp_path / "bizspec" / "_internal", "UnitX", make_yaml("UnitX"))

        result = run_viz(FakeArgs(root=str(tmp_path)))
        assert result == 1  # no processable dirs → WARNING + return 1
