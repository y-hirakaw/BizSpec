from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.search_cmd import run_search, _search_process, _extract_texts, _ALL_FIELDS


# ── helpers ───────────────────────────────────────────────────────────────────

def make_unit_data(name="UnitA", aim="テスト", rule=None, io_process=None) -> dict:
    return {
        "unit": name,
        "aim": aim,
        "rule": rule or ["制約"],
        "io": {
            "in": ["入力"],
            "process": io_process or ["実行手順"],
            "out": ["出力"],
        },
        "executor": {"type": "manual", "reason": "理由"},
    }


def write_yaml(path: Path, data: dict) -> None:
    import yaml
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")


class FakeArgs:
    def __init__(self, root, keyword, field=None, format="text"):
        self.root    = root
        self.keyword = keyword
        self.field   = field
        self.format  = format


# ── _extract_texts ────────────────────────────────────────────────────────────

class TestExtractTexts:
    def test_extracts_aim(self):
        data = make_unit_data(aim="テスト用 aim")
        texts = dict(_extract_texts(data, ("aim",)))
        assert texts.get("aim") == "テスト用 aim"

    def test_extracts_rule_list(self):
        data = make_unit_data(rule=["制約A", "制約B"])
        pairs = _extract_texts(data, ("rule",))
        values = [t for _, t in pairs]
        assert "制約A" in values
        assert "制約B" in values

    def test_extracts_io_subfields(self):
        data = make_unit_data(io_process=["Google Drive にアップロード"])
        pairs = _extract_texts(data, ("io",))
        fields = {f for f, _ in pairs}
        assert "io.process" in fields

    def test_extracts_executor_type(self):
        data = make_unit_data()
        data["executor"] = {"type": "script", "reason": "定型処理"}
        pairs = _extract_texts(data, ("executor",))
        fields_vals = {f: t for f, t in pairs}
        assert fields_vals.get("executor.type") == "script"

    def test_extracts_executor_reason(self):
        data = make_unit_data()
        data["executor"] = {"type": "ai_agent", "reason": "推論が必要"}
        pairs = _extract_texts(data, ("executor",))
        fields_vals = {f: t for f, t in pairs}
        assert fields_vals.get("executor.reason") == "推論が必要"


# ── _search_process ────────────────────────────────────────────────────────────

class TestSearchProcess:
    def test_finds_keyword_in_aim(self, tmp_path):
        write_yaml(tmp_path / "UnitA.yaml", make_unit_data(aim="Google Drive を確認"))
        hits = _search_process(tmp_path, "Google Drive", ("aim",))
        assert len(hits) == 1
        assert hits[0]["unit"] == "UnitA"

    def test_case_insensitive(self, tmp_path):
        write_yaml(tmp_path / "UnitA.yaml", make_unit_data(aim="google drive"))
        hits = _search_process(tmp_path, "Google", ("aim",))
        assert len(hits) == 1

    def test_no_match_returns_empty(self, tmp_path):
        write_yaml(tmp_path / "UnitA.yaml", make_unit_data(aim="関係ない内容"))
        hits = _search_process(tmp_path, "Google Drive", ("aim",))
        assert hits == []

    def test_skips_underscore_yaml(self, tmp_path):
        (tmp_path / "_process.yaml").write_text("name: テスト\n", encoding="utf-8")
        write_yaml(tmp_path / "UnitA.yaml", make_unit_data(aim="Google Drive"))
        hits = _search_process(tmp_path, "Google Drive", ("aim",))
        assert len(hits) == 1

    def test_field_filter(self, tmp_path):
        write_yaml(tmp_path / "UnitA.yaml", make_unit_data(aim="Google Drive", rule=["制約"]))
        hits_aim  = _search_process(tmp_path, "Google Drive", ("aim",))
        hits_rule = _search_process(tmp_path, "Google Drive", ("rule",))
        assert len(hits_aim) == 1
        assert len(hits_rule) == 0

    def test_finds_keyword_in_executor_type(self, tmp_path):
        data = make_unit_data()
        data["executor"] = {"type": "script", "reason": "定型処理"}
        write_yaml(tmp_path / "UnitA.yaml", data)
        hits = _search_process(tmp_path, "script", ("executor",))
        assert len(hits) == 1
        assert any(f == "executor.type" for f, _ in hits[0]["matches"])

    def test_finds_keyword_in_executor_reason(self, tmp_path):
        data = make_unit_data()
        data["executor"] = {"type": "ai_agent", "reason": "API呼び出しで完結"}
        write_yaml(tmp_path / "UnitA.yaml", data)
        hits = _search_process(tmp_path, "API", ("executor",))
        assert len(hits) == 1
        assert any(f == "executor.reason" for f, _ in hits[0]["matches"])

    def test_executor_not_in_default_field_restriction(self, tmp_path):
        data = make_unit_data(aim="無関係")
        data["executor"] = {"type": "script", "reason": "定型"}
        write_yaml(tmp_path / "UnitA.yaml", data)
        hits_all = _search_process(tmp_path, "script", _ALL_FIELDS)
        assert len(hits_all) == 1


# ── run_search ────────────────────────────────────────────────────────────────

class TestRunSearch:
    def test_finds_across_processes(self, tmp_path):
        for proc in ("proc-a", "proc-b"):
            d = tmp_path / "bizspec" / proc
            d.mkdir(parents=True)
            write_yaml(d / "UnitX.yaml", make_unit_data(aim=f"Google Drive {proc}"))

        result = run_search(FakeArgs(root=str(tmp_path), keyword="Google Drive"))
        assert result == 0

    def test_returns_1_when_no_match(self, tmp_path):
        (tmp_path / "bizspec" / "proc-a").mkdir(parents=True)
        write_yaml(
            tmp_path / "bizspec" / "proc-a" / "UnitX.yaml",
            make_unit_data(aim="関係ない内容"),
        )
        result = run_search(FakeArgs(root=str(tmp_path), keyword="存在しないキーワード"))
        assert result == 1

    def test_missing_bizspec_dir_returns_1(self, tmp_path):
        result = run_search(FakeArgs(root=str(tmp_path), keyword="test"))
        assert result == 1


# ── run_search --format json ──────────────────────────────────────────────────

class TestRunSearchJson:
    def test_json_with_hits(self, tmp_path, capsys):
        import json
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_yaml(proc / "UnitX.yaml", make_unit_data("UnitX", aim="OpenAPI 設計"))
        result = run_search(FakeArgs(root=str(tmp_path), keyword="OpenAPI", format="json"))
        out = capsys.readouterr().out
        assert result == 0
        data = json.loads(out)
        assert data["keyword"] == "OpenAPI"
        assert data["total"] == 1
        assert data["hits"][0]["unit"] == "UnitX"
        assert data["hits"][0]["process"] == "proc-a"
        assert any(m["field"] == "aim" for m in data["hits"][0]["matches"])

    def test_json_no_hits(self, tmp_path, capsys):
        import json
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_yaml(proc / "UnitX.yaml", make_unit_data("UnitX"))
        result = run_search(FakeArgs(root=str(tmp_path), keyword="存在しない", format="json"))
        out = capsys.readouterr().out
        assert result == 1
        data = json.loads(out)
        assert data["total"] == 0
        assert data["hits"] == []

    def test_json_no_bizspec_dir(self, tmp_path, capsys):
        import json
        result = run_search(FakeArgs(root=str(tmp_path), keyword="x", format="json"))
        out = capsys.readouterr().out
        assert result == 1
        data = json.loads(out)
        assert data["ok"] is False
        assert "error" in data

    def test_json_field_filter_in_output(self, tmp_path, capsys):
        import json
        proc = tmp_path / "bizspec" / "proc-a"
        proc.mkdir(parents=True)
        write_yaml(proc / "UnitX.yaml", make_unit_data("UnitX"))
        result = run_search(FakeArgs(root=str(tmp_path), keyword="UnitX",
                                     field=["unit"], format="json"))
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["fields"] == ["unit"]
