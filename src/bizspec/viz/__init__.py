"""Visualization (viz) パッケージ。

公開 API:
    run_viz(args) -> int             : CLI エントリポイント
    generate_html(...)                : 単一プロセスの HTML を返す
    generate_index_html(...)          : 全プロセス統合 HTML を返す
"""

from .cmd import run_viz
from .builder import _generate_html as generate_html
from .builder import _generate_index_html as generate_index_html

__all__ = [
    "run_viz",
    "generate_html",
    "generate_index_html",
]
