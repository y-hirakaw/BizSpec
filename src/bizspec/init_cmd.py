from __future__ import annotations

import shutil
import sys
from pathlib import Path

_SKILLS_SRC = Path(__file__).parent / "skills"


def _local_dest() -> Path:
    return Path.cwd() / ".claude" / "skills"


def _global_dest() -> Path:
    return Path.home() / ".claude" / "skills"


def run_init(_args) -> int:
    skill_dirs = sorted(d for d in _SKILLS_SRC.iterdir() if d.is_dir())

    print("スキルのインストール先を選択してください:")
    print("  [1] ローカル（このプロジェクトの .claude/skills/）")
    print("  [2] グローバル（~/.claude/skills/）")
    try:
        choice = input("選択 [1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nキャンセルしました")
        return 1

    if choice in ("", "1"):
        dest = _local_dest()
        scope = "ローカル"
    elif choice == "2":
        dest = _global_dest()
        scope = "グローバル"
    else:
        print(f"無効な選択です: {choice!r}", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    for skill_dir in skill_dirs:
        target = dest / skill_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill_dir, target)
        print(f"  ✓ {skill_dir.name}")

    print(f"\n{scope}の .claude/skills/ にスキルをインストールしました")
    return 0
