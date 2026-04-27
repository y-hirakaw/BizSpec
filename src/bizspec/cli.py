import argparse
import sys
from bizspec.init_cmd import run_init
from bizspec.list_cmd import run_list
from bizspec.new_cmd import run_new
from bizspec.search_cmd import run_search, FIELD_CHOICES
from bizspec.validate import run_validate
from bizspec.viz_cmd import run_viz


def main() -> None:
    parser = argparse.ArgumentParser(prog="bizspec")
    parser.add_argument(
        "--root",
        default=".",
        metavar="DIR",
        help="bizspec/ フォルダを含むルートディレクトリ（デフォルト: カレント）",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Claude Code スキルをインストールする")

    # validate
    val = sub.add_parser("validate", help="BizSpec YAML を検証する")
    val.add_argument("process", nargs="?", help="プロセス名（省略時は全プロセスを検証）")

    # list
    lst = sub.add_parser("list", help="unit 一覧を表示する")
    lst.add_argument("process", nargs="?", help="プロセス名（省略時は全プロセスを表示）")

    # viz
    viz = sub.add_parser("viz", help="フロー図 HTML を生成する")
    viz.add_argument("process", nargs="?", help="プロセス名（省略時は全プロセスを出力）")

    # new
    nw = sub.add_parser("new", help="unit のスケルトン YAML を生成する")
    nw.add_argument("process", help="プロセス名")
    nw.add_argument("unit",    help="unit 名")
    nw.add_argument("--executor", choices=["script", "ai_agent", "manual"], help="executor.type")
    nw.add_argument("--phase", help="phase（例: spec / dev）")
    nw.add_argument("--core",  choices=["true", "false"], help="core フラグ")
    nw.add_argument("--up",   nargs="*", metavar="UNIT", help="link.up に追加する unit 名")
    nw.add_argument("--down", nargs="*", metavar="UNIT", help="link.down に追加する unit 名")
    nw.add_argument("--force", action="store_true", help="既存ファイルを上書きする")

    # search
    srch = sub.add_parser("search", help="全プロセス横断でキーワード検索する")
    srch.add_argument("keyword", help="検索キーワード")
    srch.add_argument(
        "--field", nargs="*", choices=FIELD_CHOICES,
        metavar="FIELD",
        help=f"検索対象フィールド（複数可、省略時は全フィールド）: {FIELD_CHOICES}",
    )

    args = parser.parse_args()

    if args.command == "init":
        sys.exit(run_init(args))
    elif args.command == "validate":
        sys.exit(run_validate(args))
    elif args.command == "list":
        sys.exit(run_list(args))
    elif args.command == "viz":
        sys.exit(run_viz(args))
    elif args.command == "new":
        sys.exit(run_new(args))
    elif args.command == "search":
        sys.exit(run_search(args))
    else:
        parser.print_help()
        sys.exit(1)
