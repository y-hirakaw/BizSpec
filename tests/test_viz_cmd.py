from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.viz_cmd import (
    _topo_levels,
    _compute_layout,
    _build_edges,
    _generate_html,
    _generate_index_html,
    _load_units,
    _load_process_meta,
    _process_stats,
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


# ── _load_units / _load_process_meta ─────────────────────────────────────────

class TestLoadUnits:
    def test_skips_underscore_yaml(self, tmp_path):
        write_yaml(tmp_path, "UnitA", make_yaml("UnitA"))
        (tmp_path / "_process.yaml").write_text("name: テストプロセス", encoding="utf-8")
        units = _load_units(tmp_path)
        assert len(units) == 1
        assert units[0]["unit"] == "UnitA"

    def test_loads_normal_yaml(self, tmp_path):
        write_yaml(tmp_path, "A", make_yaml("A"))
        write_yaml(tmp_path, "B", make_yaml("B"))
        units = _load_units(tmp_path)
        names = {u["unit"] for u in units}
        assert names == {"A", "B"}


class TestLoadProcessMeta:
    def test_reads_name_field(self, tmp_path):
        (tmp_path / "_process.yaml").write_text("name: PRレビュー\n", encoding="utf-8")
        meta = _load_process_meta(tmp_path)
        assert meta.get("name") == "PRレビュー"

    def test_returns_empty_dict_when_missing(self, tmp_path):
        assert _load_process_meta(tmp_path) == {}

    def test_returns_empty_dict_on_invalid_yaml(self, tmp_path):
        (tmp_path / "_process.yaml").write_text(": invalid: yaml:\n", encoding="utf-8")
        meta = _load_process_meta(tmp_path)
        assert isinstance(meta, dict)


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

    def test_display_name_shown_when_given(self):
        units = [make_unit("A")]
        html = _generate_html("pr-review", units, display_name="PRレビュー")
        assert "PRレビュー" in html

    def test_display_name_slug_in_subtitle(self):
        units = [make_unit("A")]
        html = _generate_html("pr-review", units, display_name="PRレビュー")
        assert "pr-review" in html

    def test_no_display_name_uses_folder_name(self):
        units = [make_unit("A")]
        html = _generate_html("pr-review", units)
        assert "pr-review" in html


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


# ── _process_stats ────────────────────────────────────────────────────────────

class TestProcessStats:
    def test_counts_executors(self):
        units = [
            make_unit("A", executor_type="script"),
            make_unit("B", executor_type="ai_agent"),
            make_unit("C", executor_type="ai_agent"),
        ]
        s = _process_stats(units)
        assert s["executor"]["script"] == 1
        assert s["executor"]["ai_agent"] == 2
        assert s["executor"]["manual"] == 0

    def test_counts_core(self):
        units = [make_unit("A", core=True), make_unit("B", core=False)]
        s = _process_stats(units)
        assert s["core_count"] == 1
        assert s["unit_count"] == 2

    def test_collects_phases(self):
        u1 = {**make_unit("A"), "phase": "spec"}
        u2 = {**make_unit("B"), "phase": "dev"}
        s = _process_stats([u1, u2])
        assert set(s["phases"]) == {"spec", "dev"}


# ── _generate_index_html ──────────────────────────────────────────────────────

class TestGenerateIndexHtml:
    def _two_procs(self):
        proc_a = [make_unit("X", down=["Y"]), make_unit("Y", up=["X"])]
        proc_b = [make_unit("P")]
        return {"proc-a": proc_a, "proc-b": proc_b}

    def test_produces_html(self):
        html = _generate_index_html(self._two_procs())
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_contains_all_process_names(self):
        html = _generate_index_html(self._two_procs())
        assert "proc-a" in html
        assert "proc-b" in html

    def test_empty_processes_returns_empty(self):
        assert _generate_index_html({}) == ""

    def test_no_placeholder_tokens_remain(self):
        html = _generate_index_html(self._two_procs())
        assert "__ALL_DATA_JSON__" not in html

    def test_display_name_embedded_in_data(self):
        html = _generate_index_html(
            self._two_procs(),
            display_names={"proc-a": "プロセスA"},
        )
        assert "プロセスA" in html

    def test_display_name_none_when_same_as_key(self):
        import json, re
        m = re.search(r"const ALL_DATA = ({.*?});", _generate_index_html(
            self._two_procs(),
            display_names={"proc-a": "proc-a"},
        ), re.DOTALL)
        data = json.loads(m.group(1))
        assert data["proc-a"]["displayName"] is None


# ── run_viz index.html generation ────────────────────────────────────────────

class TestRunVizIndex:
    def test_generates_index_html_for_multiple_processes(self, tmp_path):
        for name in ("proc-a", "proc-b"):
            d = tmp_path / "bizspec" / name
            d.mkdir(parents=True)
            write_yaml(d, "UnitX", make_yaml("UnitX"))

        result = run_viz(FakeArgs(root=str(tmp_path)))
        assert result == 0
        index = tmp_path / "bizspec" / "_viz" / "index.html"
        assert index.exists()
        content = index.read_text(encoding="utf-8")
        assert "proc-a" in content
        assert "proc-b" in content

    def test_no_index_html_for_single_process_with_arg(self, tmp_path):
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitX", make_yaml("UnitX"))

        run_viz(FakeArgs(root=str(tmp_path), process="proc-a"))
        assert not (tmp_path / "bizspec" / "_viz" / "index.html").exists()

    def test_no_index_html_for_single_process_no_arg(self, tmp_path):
        proc = tmp_path / "bizspec" / "only-proc"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitX", make_yaml("UnitX"))

        run_viz(FakeArgs(root=str(tmp_path)))
        assert not (tmp_path / "bizspec" / "_viz" / "index.html").exists()

    def test_display_name_from_process_yaml(self, tmp_path):
        proc = tmp_path / "bizspec" / "pr-review"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitX", make_yaml("UnitX"))
        (proc / "_process.yaml").write_text("name: PRレビュー\n", encoding="utf-8")

        run_viz(FakeArgs(root=str(tmp_path), process="pr-review"))
        html = (tmp_path / "bizspec" / "_viz" / "pr-review.html").read_text(encoding="utf-8")
        assert "PRレビュー" in html
        assert "pr-review" in html

    def test_process_yaml_not_loaded_as_unit(self, tmp_path):
        proc = tmp_path / "bizspec" / "my-proc"
        proc.mkdir(parents=True)
        write_yaml(proc, "UnitA", make_yaml("UnitA"))
        (proc / "_process.yaml").write_text("name: テスト\n", encoding="utf-8")

        result = run_viz(FakeArgs(root=str(tmp_path), process="my-proc"))
        assert result == 0
        html = (tmp_path / "bizspec" / "_viz" / "my-proc.html").read_text(encoding="utf-8")
        assert "1 units" in html
