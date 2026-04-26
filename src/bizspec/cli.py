import argparse
import sys
from bizspec.list_cmd import run_list
from bizspec.validate import run_validate


def main() -> None:
    parser = argparse.ArgumentParser(prog="bizspec")
    parser.add_argument(
        "--root",
        default=".",
        metavar="DIR",
        help="bizspec/ フォルダを含むルートディレクトリ（デフォルト: カレント）",
    )
    sub = parser.add_subparsers(dest="command")

    # validate
    val = sub.add_parser("validate", help="BizSpec YAML を検証する")
    val.add_argument("process", nargs="?", help="プロセス名（省略時は全プロセスを検証）")

    # list
    lst = sub.add_parser("list", help="unit 一覧を表示する")
    lst.add_argument("process", nargs="?", help="プロセス名（省略時は全プロセスを表示）")

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(run_validate(args))
    elif args.command == "list":
        sys.exit(run_list(args))
    else:
        parser.print_help()
        sys.exit(1)
