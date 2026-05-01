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
        is_local = True
    elif choice == "2":
        dest = _global_dest()
        scope = "グローバル"
        is_local = False
    else:
        print(f"無効な選択です: {choice!r}", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    existing = [d for d in skill_dirs if (dest / d.name).exists()]
    if existing:
        names = ", ".join(d.name for d in existing)
        print(f"\n⚠️  既存のスキルディレクトリを上書きします: {names}")
        print("    （SKILL.md の正本は src/bizspec/skills/ 側です。.claude/skills/ 側の手動編集は破棄されます）")
        confirm = input("続行しますか？ [y/N]: ").strip().lower()
        if confirm != "y":
            print("中止しました。")
            return 1
    for skill_dir in skill_dirs:
        target = dest / skill_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill_dir, target)
        print(f"  ✓ {skill_dir.name}")

    print(f"\n{scope}の .claude/skills/ にスキルをインストールしました")

    if is_local:
        bizspec_dir = Path.cwd() / "bizspec"
        if not bizspec_dir.exists():
            bizspec_dir.mkdir()
            print(f"  bizspec/ フォルダを作成しました")

    return 0
