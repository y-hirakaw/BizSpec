"""検証ダイアグノスティクスの共通型。

``VError`` は ``bizspec validate`` および各 CLI（rename/rm 後の再検証）で
共通に使う「ファイル単位のエラー / 警告」のレコード型。

severity:
    - ``"error"``: 検証失敗。CLI の exit code を 1 にする
    - ``"warn"``:  検証は通すが注意喚起したい（未推奨フィールド値など）
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VError:
    file: Path
    field: str
    message: str
    severity: str = "error"  # "error" or "warn"
