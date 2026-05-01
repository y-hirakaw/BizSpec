"""対話プロンプトの共通ヘルパ。"""

from __future__ import annotations

import sys


def confirm(message: str, *, yes: bool = False) -> bool:
    """ユーザーに ``[y/N]`` 確認する。

    - ``yes=True`` または ``stdin`` が TTY でない（CI / パイプ）場合は自動承認
    - TTY 環境でのみプロンプトを出す
    - 空 Enter / "n" 等で False（中止）
    """
    if yes or not sys.stdin.isatty():
        return True
    try:
        ans = input(f"{message} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans == "y"
