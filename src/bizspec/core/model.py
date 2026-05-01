"""BizSpec YAML スキーマの型ヒント定義。

dict をそのまま扱う既存実装は残したまま、IDE の型補完と静的検査で
スキーマ違反を早期検知できるようにする。実行時の挙動は変えない
（``TypedDict`` は実行時には ``dict`` として振る舞う）。

dataclass への本格移行は別案件。今回は型ヒントのみ。

Python 3.9 では ``typing.NotRequired`` が無いため、オプショナルフィールドを
表現する場合は ``total=False`` の TypedDict を継承で組み合わせる方式を採る。
"""

from __future__ import annotations

from typing import TypedDict, Union


# ── 内部マッピング ────────────────────────────────────────────────────────────

class IO(TypedDict):
    """``unit.io`` — 入力 / 処理 / 出力。"""
    in_: list[str]   # 実 YAML キーは "in" だが Python 予約語のため "in_" を後置
    process: list[str]
    out: list[str]


class Link(TypedDict):
    """``unit.link`` — 同一プロセス内の実行順序。"""
    up: list[str]
    down: list[str]


class Executor(TypedDict):
    """``unit.executor`` — 主体（script / ai_agent / manual）と理由。"""
    type: str
    reason: str


class Effort(TypedDict, total=False):
    """``unit.effort`` — 所要時間 / 月間頻度（オプショナル）。"""
    duration: Union[int, float]
    frequency: int


class Automation(TypedDict, total=False):
    """``unit.automation`` — 自動化の難易度 / 現状（オプショナル）。"""
    difficulty: str  # "low" | "medium" | "high"
    status: str      # "manual" | "partially-automated" | "automated"


class Execution(TypedDict, total=False):
    """``unit.execution`` — 実行制御ヒント（オプショナル）。"""
    parallel_with: list[str]


# ── unit / process ──────────────────────────────────────────────────────────

class _UnitRequired(TypedDict):
    """unit の必須フィールド。"""
    unit: str
    aim: str
    phase: str
    scope: list[str]
    rule: list[str]
    link: Link
    core: Union[bool, str]  # bool または "undetermined"
    io: IO
    executor: Executor


class Unit(_UnitRequired, total=False):
    """BizSpec unit YAML 1 件分の論理構造。

    必須フィールドに加え、オプショナルフィールド（``effort``, ``automation``,
    ``status``, ``deprecated_reason``, ``execution``, ``depends_on``）を含む。
    """
    depends_on: list[str]
    effort: Effort
    automation: Automation
    status: str  # "draft" | "review" | "stable" | "deprecated"
    deprecated_reason: str
    execution: Execution


class ProcessMeta(TypedDict, total=False):
    """``_process.yaml`` のメタ情報（display 用）。"""
    name: str


__all__ = [
    "IO",
    "Link",
    "Executor",
    "Effort",
    "Automation",
    "Execution",
    "Unit",
    "ProcessMeta",
]
