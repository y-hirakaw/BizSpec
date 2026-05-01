"""``bizspec.viz`` のテンプレが ``importlib.resources`` で読めることを検証する。

``pyproject.toml`` の ``[tool.setuptools.package-data]`` 設定漏れがあると、
本番 install 後に ``bizspec viz`` が壊れる。CI でその事故を早期検知する。
"""

from __future__ import annotations

from importlib.resources import files

import pytest


class TestVizTemplatesAreShipped:
    """テンプレ HTML が package-data として配布される。"""

    def test_process_template_readable(self):
        path = files("bizspec.viz") / "templates" / "process.html"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("<!DOCTYPE html>")
        # placeholder が含まれていることを確認（中身が空ではない）
        assert "__PROCESS_NAME__" in text
        assert "__UNITS_JSON__" in text

    def test_index_template_readable(self):
        path = files("bizspec.viz") / "templates" / "index.html"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("<!DOCTYPE html>")
        assert "__ALL_DATA_JSON__" in text
        assert "__CROSS_EDGES_JSON__" in text

    def test_builder_caches_templates_at_import(self):
        """builder モジュール初回 import 時にテンプレが読まれている。"""
        from bizspec.viz import builder
        assert builder._TEMPLATE_PROCESS.startswith("<!DOCTYPE html>")
        assert builder._TEMPLATE_INDEX.startswith("<!DOCTYPE html>")


class TestEndToEndHtmlGeneration:
    """テンプレを使った HTML 生成が完走する（package-data の実利用パス）。"""

    def test_generate_html_does_not_leak_placeholders(self):
        from bizspec.viz.builder import _generate_html
        units = [
            {"unit": "A", "aim": "a", "phase": "spec", "core": True,
             "scope": [], "rule": [], "io": {}, "executor": {"type": "script", "reason": ""},
             "link": {"up": [], "down": ["B"]}},
            {"unit": "B", "aim": "b", "phase": "spec", "core": True,
             "scope": [], "rule": [], "io": {}, "executor": {"type": "script", "reason": ""},
             "link": {"up": ["A"], "down": []}},
        ]
        html = _generate_html("proc", units)
        for ph in (
            "__PROCESS_NAME__", "__SUBTITLE__", "__CANVAS_W__", "__CANVAS_H__",
            "__UNITS_JSON__", "__POSITIONS_JSON__", "__EDGES_JSON__",
        ):
            assert ph not in html, f"placeholder leaked: {ph}"

    def test_generate_index_html_does_not_leak_placeholders(self):
        from bizspec.viz.builder import _generate_index_html
        units_a = [{"unit": "X", "aim": "x", "phase": "spec", "core": True,
                    "scope": [], "rule": [], "io": {},
                    "executor": {"type": "script", "reason": ""},
                    "link": {"up": [], "down": []}}]
        html = _generate_index_html({"proc-a": units_a})
        assert "__ALL_DATA_JSON__" not in html
        assert "__CROSS_EDGES_JSON__" not in html
