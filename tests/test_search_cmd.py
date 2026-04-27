from __future__ import annotations

from pathlib import Path
import pytest
from bizspec.search_cmd import run_search, _search_process, _extract_texts


# ── helpers ───────────────────────────────────────────────────────────────────

def make_unit_data(name="UnitA", aim="テスト", job=None, rule=None, io_run=None) -> dict:
    return {
        "unit": name,
        "aim": aim,
        "job": job or ["作業内容"],
        "rule": rule or ["制約"],
        "io": {
            "in": ["入力"],
            "run": io_run or ["実行手順"],
            "out": ["出力"],
        },
        "executor": {"type": "manual", "reason": "理由"},
    }


def write_yaml(path: Path, data: dict) -> None:
    import yaml
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")


class FakeArgs:
    def __init__(self, root, keyword, field=None):
        self.root    = root
        self.keyword = keyword
        self.field   = field


# ── _extract_texts ────────────────────────────────────────────────────────────

class TestExtractTexts:
    def test_extracts_aim(self):
        data = make_unit_data(aim="テスト用 aim")
        texts = dict(_extract_texts(data, ("aim",)))
        assert texts.get("aim") == "テスト用 aim"

    def test_extracts_job_list(self):
        data = make_unit_data(job=["作業A", "作業B"])
        pairs = _extract_texts(data, ("job",))
        values = [t for _, t in pairs]
        assert "作業A" in values
        assert "作業B" in values

    def test_extracts_io_subfields(self):
        data = make_unit_data(io_run=["Google Drive にアップロード"])
        pairs = _extract_texts(data, ("io",))
        fields = {f for f, _ in pairs}
        assert "io.run" in fields


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
