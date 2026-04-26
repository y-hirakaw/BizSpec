import argparse
import sys
from bizspec.init_cmd import run_init
from bizspec.list_cmd import run_list
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

    args = parser.parse_args()

    if args.command == "init":
        sys.exit(run_init(args))
    elif args.command == "validate":
        sys.exit(run_validate(args))
    elif args.command == "list":
        sys.exit(run_list(args))
    elif args.command == "viz":
        sys.exit(run_viz(args))
    else:
        parser.print_help()
        sys.exit(1)
