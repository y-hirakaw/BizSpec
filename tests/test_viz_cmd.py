from __future__ import annotations

import re
import shutil
import subprocess
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
    _unit_to_js,
    run_viz,
    NODE_W, NODE_H, H_GAP, V_GAP,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def make_unit(name: str, up=None, down=None, core=True, executor_type="script", extra=None) -> dict:
    d = {
        "unit": name, "aim": f"{name}のaim", "phase": "spec", "core": core,
        "scope": ["作業"], "rule": ["制約"],
        "io": {"in": ["入力"], "run": ["実行"], "out": ["出力"]},
        "executor": {"type": executor_type, "reason": "理由"},
        "link": {"up": up or [], "down": down or []},
    }
    if extra:
        d.update(extra)
    return d


def make_yaml(name: str, up=None, down=None, core: bool = True, executor_type: str = "script") -> str:
    core_str = "true" if core else "false"
    up_items  = "\n".join(f"    - {u}" for u in (up  or []))
    down_items = "\n".join(f"    - {d}" for d in (down or []))
    return (
        f"unit: {name}\naim: テスト\nphase: spec\n"
        f"scope:\n  - 作業\nrule:\n  - 制約\n"
        f"link:\n  up:\n{up_items or '    []'}\n  down:\n{down_items or '    []'}\n"
        f"core: {core_str}\n"
        f"io:\n  in:\n    - 入力\n  process:\n    - 実行\n  out:\n    - 出力\n"
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
        assert ["A", "B", "seq"] in edges

    def test_no_duplicate_edges(self):
        units = [make_unit("A", down=["B"]), make_unit("B", up=["A"])]
        positions = {"A": {"left": 0, "top": 0}, "B": {"left": 0, "top": 110}}
        edges = _build_edges(units, positions)
        assert edges.count(["A", "B", "seq"]) == 1

    def test_unknown_target_skipped(self):
        units = [make_unit("A", down=["Ghost"])]
        positions = {"A": {"left": 0, "top": 0}}
        edges = _build_edges(units, positions)
        assert edges == []

    def test_parallel_edge(self):
        units = [
            make_unit("A"),
            make_unit("B", extra={"execution": {"parallel_with": ["C"]}}),
            make_unit("C"),
        ]
        positions = {"A": {"left": 0, "top": 0}, "B": {"left": 0, "top": 110}, "C": {"left": 200, "top": 110}}
        edges = _build_edges(units, positions)
        parallel_edges = [e for e in edges if e[2] == "parallel"]
        assert len(parallel_edges) == 1
        assert set(parallel_edges[0][:2]) == {"B", "C"}

    def test_parallel_edge_no_duplicate(self):
        units = [
            make_unit("A", extra={"execution": {"parallel_with": ["B"]}}),
            make_unit("B", extra={"execution": {"parallel_with": ["A"]}}),
        ]
        positions = {"A": {"left": 0, "top": 0}, "B": {"left": 200, "top": 0}}
        edges = _build_edges(units, positions)
        parallel_edges = [e for e in edges if e[2] == "parallel"]
        assert len(parallel_edges) == 1


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
        m = re.search(r"const ALL_DATA\s*=\s*({.*?});", _generate_index_html(
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


# ── _unit_to_js effort / automation ──────────────────────────────────────────

class TestUnitToJs:
    def test_effort_duration_included(self):
        u = {**make_unit("A"), "effort": {"duration": 0.5}}
        js = _unit_to_js(u)
        assert js["effort"]["duration"] == 0.5

    def test_effort_duration_none_when_absent(self):
        js = _unit_to_js(make_unit("A"))
        assert js["effort"]["duration"] is None

    def test_automation_fields_included(self):
        u = {**make_unit("A"), "automation": {"difficulty": "high", "status": "manual"}}
        js = _unit_to_js(u)
        assert js["automation"]["difficulty"] == "high"
        assert js["automation"]["status"] == "manual"

    def test_automation_fields_none_when_absent(self):
        js = _unit_to_js(make_unit("A"))
        assert js["automation"]["difficulty"] is None
        assert js["automation"]["status"] is None


class TestGenerateHtmlEffortAutomation:
    def test_effort_section_shown_when_present(self):
        u = {**make_unit("A"), "effort": {"duration": 0.5}}
        html = _generate_html("proc", [u])
        assert "0.5" in html
        assert "所要時間" in html

    def test_automation_section_shown_when_present(self):
        u = {**make_unit("A"), "automation": {"difficulty": "low", "status": "automated"}}
        html = _generate_html("proc", [u])
        assert "low" in html
        assert "自動化難易度" in html

    def test_effort_null_when_not_set(self):
        import json, re
        html = _generate_html("proc", [make_unit("A")])
        m = re.search(r"const units\s*=\s*({.*?});", html, re.DOTALL)
        data = json.loads(m.group(1))
        assert data["A"]["effort"]["duration"] is None
        assert data["A"]["automation"]["difficulty"] is None

    def test_effort_string_becomes_null(self):
        u = {**make_unit("A"), "effort": {"duration": "30m"}}
        js = _unit_to_js(u)
        assert js["effort"]["duration"] is None


# ── JS 構文チェック ───────────────────────────────────────────────────────────

def _extract_scripts(html: str) -> list[str]:
    return re.findall(r"<script>(.*?)</script>", html, re.DOTALL)


def _check_js(script: str, tmp_path: Path, name: str) -> subprocess.CompletedProcess:
    js_file = tmp_path / name
    js_file.write_text(script, encoding="utf-8")
    return subprocess.run(
        ["node", "--check", str(js_file)],
        capture_output=True,
    )


def _full_unit(name: str) -> dict:
    """effort + automation をすべて持つユニット（最多コードパス）。"""
    return {
        **make_unit(name),
        "effort": {"duration": 1, "frequency": 4},
        "automation": {"difficulty": "medium", "status": "manual"},
    }


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
class TestGeneratedJsSyntax:
    def test_process_html_no_effort(self, tmp_path):
        html = _generate_html("proc", [make_unit("A"), make_unit("B")])
        for i, script in enumerate(_extract_scripts(html)):
            r = _check_js(script, tmp_path, f"no_effort_{i}.js")
            assert r.returncode == 0, r.stderr.decode()

    def test_process_html_with_effort_and_automation(self, tmp_path):
        units = [_full_unit("A"), _full_unit("B")]
        html = _generate_html("proc", units)
        for i, script in enumerate(_extract_scripts(html)):
            r = _check_js(script, tmp_path, f"effort_auto_{i}.js")
            assert r.returncode == 0, r.stderr.decode()

    def test_process_html_partial_effort(self, tmp_path):
        """duration のみ（frequency なし）のケース。"""
        u = {**make_unit("A"), "effort": {"duration": 2}}
        html = _generate_html("proc", [u])
        for i, script in enumerate(_extract_scripts(html)):
            r = _check_js(script, tmp_path, f"partial_effort_{i}.js")
            assert r.returncode == 0, r.stderr.decode()

    def test_index_html_no_effort(self, tmp_path):
        procs = {"proc-a": [make_unit("X")], "proc-b": [make_unit("Y")]}
        html = _generate_index_html(procs)
        for i, script in enumerate(_extract_scripts(html)):
            r = _check_js(script, tmp_path, f"index_no_effort_{i}.js")
            assert r.returncode == 0, r.stderr.decode()

    def test_index_html_with_effort_and_automation(self, tmp_path):
        procs = {
            "proc-a": [_full_unit("X"), _full_unit("Y")],
            "proc-b": [_full_unit("Z")],
        }
        html = _generate_index_html(procs)
        for i, script in enumerate(_extract_scripts(html)):
            r = _check_js(script, tmp_path, f"index_effort_{i}.js")
            assert r.returncode == 0, r.stderr.decode()


# ── index.html 構造契約 ───────────────────────────────────────────────────────
# viz_cmd.py 分割／テンプレート外部化前に、生成 HTML の DOM/JS 契約を固定する。

class TestIndexHtmlStructure:
    def _procs(self, with_cross_dep: bool = False):
        proc_a = [make_unit("X", down=["Y"]), make_unit("Y", up=["X"])]
        if with_cross_dep:
            proc_b = [{**make_unit("P"), "depends_on": ["proc-a:X"]}]
        else:
            proc_b = [make_unit("P")]
        return {"proc-a": proc_a, "proc-b": proc_b}

    def test_critical_dom_elements_present(self):
        html = _generate_index_html(self._procs())
        for el in (
            'id="overview-view"', 'id="overview-grid"', 'id="overview-edges"',
            'id="sidebar"', 'id="topbar"', 'id="back-btn"',
            'id="flow-view"', 'id="flow-canvas"', 'id="detail-panel"',
        ):
            assert el in html, f"missing critical element: {el}"

    def test_mode_toggle_buttons_present(self):
        """モード切替の構造（ID + data-mode 属性）が残ること。

        ボタンラベル（"Info" / "Flow" / "情報" / "フロー" など）はデザイン
        テーマで変わるため、構造のみをチェックする。
        """
        html = _generate_index_html(self._procs())
        assert 'id="ov-mode-toggle"' in html
        assert 'data-mode="info"' in html
        assert 'data-mode="flow"' in html
        # モード切替を駆動する関数がスクリプト中に存在する
        assert "setOvMode" in html
        # 切替対象クラスが CSS に存在する
        assert ".mode-info" in html
        assert ".mode-flow" in html

    def test_all_data_is_valid_json(self):
        import json
        html = _generate_index_html(self._procs())
        m = re.search(r"const ALL_DATA\s*=\s*({.*?});", html, re.DOTALL)
        assert m, "ALL_DATA assignment missing"
        data = json.loads(m.group(1))
        for proc_name in ("proc-a", "proc-b"):
            assert proc_name in data
            entry = data[proc_name]
            for key in ("units", "positions", "edges", "canvasW", "canvasH", "stats"):
                assert key in entry, f"{proc_name} missing key: {key}"

    def test_cross_edges_is_valid_json_with_dep(self):
        import json
        html = _generate_index_html(self._procs(with_cross_dep=True))
        m = re.search(r"const CROSS_EDGES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        assert m, "CROSS_EDGES assignment missing"
        edges = json.loads(m.group(1))
        assert {"from": "proc-a", "to": "proc-b"} in edges

    def test_cross_edges_empty_when_no_deps(self):
        import json
        html = _generate_index_html(self._procs(with_cross_dep=False))
        m = re.search(r"const CROSS_EDGES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        edges = json.loads(m.group(1))
        assert edges == []

    def test_node_color_logic_present(self):
        """ノード色分岐が SVG ミニフローと CSS の両方に残ること。

        具体的な色 hex はテーマで変わるので assert しない。代わりに
        色を選ぶ関数（nodeColors）と、CSS で参照される色クラスの
        定義が両方残っていることを確認する。
        """
        html = _generate_index_html(self._procs())
        # 色選択ロジック本体
        assert "function nodeColors" in html
        # 各色クラスが CSS で定義されている
        for cls in (
            ".node.heat-low", ".node.heat-medium", ".node.heat-high",
            ".node.status-draft", ".node.status-review",
            ".node.status-stable", ".node.status-deprecated",
            ".node.core-true", ".node.core-false",
        ):
            assert cls in html, f"missing CSS class: {cls}"
