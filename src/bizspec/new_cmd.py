from __future__ import annotations

import sys
from pathlib import Path

SKELETON = """\
unit: {name}
aim: TODO
phase: {phase}
job:
  - TODO
rule:
  - TODO
link:
  up: {up}
  down: {down}
core: {core}
io:
  in:
    - TODO
  run:
    - TODO
  out:
    - TODO
executor:
  type: {executor}
  reason: TODO
"""

VALID_EXECUTORS = {"script", "ai_agent", "manual"}
VALID_CORES     = {"true", "false"}


def run_new(args) -> int:
    root        = Path(args.root).resolve()
    bizspec_dir = root / "bizspec"
    process_dir = bizspec_dir / args.process

    if not bizspec_dir.exists():
        print(f"ERROR: {bizspec_dir} が見つかりません", file=sys.stderr)
        return 1

    # executor バリデーション
    executor = args.executor or "manual"
    if executor not in VALID_EXECUTORS:
        print(f"ERROR: --executor は {sorted(VALID_EXECUTORS)} のいずれかを指定してください", file=sys.stderr)
        return 1

    # core バリデーション
    core = args.core or "false"
    if core not in VALID_CORES:
        print(f"ERROR: --core は true / false のいずれかを指定してください", file=sys.stderr)
        return 1

    # link
    up_items   = "\n".join(f"    - {u}" for u in (args.up   or []))
    down_items = "\n".join(f"    - {d}" for d in (args.down or []))
    up_yaml    = f"\n{up_items}"   if up_items   else " []"
    down_yaml  = f"\n{down_items}" if down_items else " []"

    content = SKELETON.format(
        name=args.unit,
        phase=args.phase or "TODO",
        up=up_yaml,
        down=down_yaml,
        core=core,
        executor=executor,
    )

    process_dir.mkdir(parents=True, exist_ok=True)
    out_path = process_dir / f"{args.unit}.yaml"

    if out_path.exists() and not args.force:
        print(f"ERROR: {out_path.relative_to(root)} はすでに存在します（上書きするには --force）", file=sys.stderr)
        return 1

    out_path.write_text(content, encoding="utf-8")
    print(f"  created: {out_path.relative_to(root)}")
    return 0
