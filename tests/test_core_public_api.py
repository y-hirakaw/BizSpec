"""``bizspec.core`` の公開 API がそろっていることを CI で固定する。

将来の core 整理（dataclass 化など）で意図せず公開 API を破壊しないよう、
``from bizspec.core import X`` できるシンボルをここでピン留めする。
"""

from __future__ import annotations


class TestPublicSymbolsExposed:
    def test_errors_exported(self):
        from bizspec.core import VError
        # severity デフォルト
        from pathlib import Path
        e = VError(Path("a.yaml"), "field", "msg")
        assert e.severity == "error"
        w = VError(Path("a.yaml"), "field", "msg", severity="warn")
        assert w.severity == "warn"

    def test_loader_exported(self):
        from bizspec.core import (
            iter_processes,
            iter_unit_files,
            load_process_meta,
            load_unit,
            load_units,
            load_units_by_name,
            load_units_with_paths,
        )
        # all callable
        for fn in (iter_processes, iter_unit_files, load_process_meta,
                   load_unit, load_units, load_units_by_name, load_units_with_paths):
            assert callable(fn)

    def test_model_typeddicts_exported(self):
        from bizspec.core import (
            IO, Automation, Effort, Executor, Execution, Link, ProcessMeta, Unit,
        )
        # TypedDict は実行時 dict として振る舞う
        link: Link = {"up": [], "down": ["B"]}
        assert link["down"] == ["B"]


class TestValidateBackwardCompat:
    def test_verror_still_importable_from_validate(self):
        """既存テスト・外部コードが import している経路を維持する。"""
        from bizspec.validate import VError
        from bizspec.core.errors import VError as CoreVError
        assert VError is CoreVError
