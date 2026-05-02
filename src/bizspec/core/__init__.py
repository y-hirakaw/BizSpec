"""BizSpec の共有レイヤー。

各コマンドモジュール（`list_cmd`, `viz_cmd`, `rename_cmd` など）が
重複して持っていた YAML 読み込み・プロセス走査・型ヘルパを集約する。

`validate.py` はパースエラーを意図的に報告する役割があるため、共通
loader は使わず独自実装を保持している。
"""

from .config import DEFAULT_CONFIG, load_config
from .errors import VError
from .loader import (
    iter_processes,
    iter_unit_files,
    load_unit,
    load_units,
    load_units_with_paths,
    load_units_by_name,
    load_process_meta,
)
from .model import (
    IO,
    Automation,
    Effort,
    Executor,
    Execution,
    Link,
    ProcessMeta,
    Unit,
)

__all__ = [
    # config
    "DEFAULT_CONFIG",
    "load_config",
    # errors
    "VError",
    # loader
    "iter_processes",
    "iter_unit_files",
    "load_unit",
    "load_units",
    "load_units_with_paths",
    "load_units_by_name",
    "load_process_meta",
    # model
    "IO",
    "Automation",
    "Effort",
    "Executor",
    "Execution",
    "Link",
    "ProcessMeta",
    "Unit",
]
