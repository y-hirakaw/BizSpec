from __future__ import annotations

from pathlib import Path
import bizspec.init_cmd as init_cmd


# ── バンドル確認 ──────────────────────────────────────────────────────────────

def test_skills_src_exists():
    assert init_cmd._SKILLS_SRC.is_dir()


def test_expected_skills_present():
    names = {d.name for d in init_cmd._SKILLS_SRC.iterdir() if d.is_dir()}
    assert "bizspec-refine" in names
    assert "bizspec-run" in names
    assert "bizspec-refactor" in names


def test_all_skills_have_skill_md():
    for skill_dir in init_cmd._SKILLS_SRC.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        assert skill_md.exists(), f"{skill_dir.name}/SKILL.md が見つかりません"
        assert skill_md.stat().st_size > 0, f"{skill_dir.name}/SKILL.md が空です"


def test_skill_md_has_frontmatter():
    """各 SKILL.md が name フィールドを持つ frontmatter で始まることを確認する"""
    for skill_dir in init_cmd._SKILLS_SRC.iterdir():
        if not skill_dir.is_dir():
            continue
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---"), f"{skill_dir.name}/SKILL.md に frontmatter がありません"
        assert "name:" in content, f"{skill_dir.name}/SKILL.md に name フィールドがありません"


# ── インストール動作 ───────────────────────────────────────────────────────────

def test_init_local_default(monkeypatch, tmp_path):
    """エンターキー（空文字）でローカルにインストールされる"""
    dest = tmp_path / ".claude" / "skills"
    monkeypatch.setattr(init_cmd, "_local_dest", lambda: dest)
    monkeypatch.setattr("builtins.input", lambda _: "")
    result = init_cmd.run_init(None)
    assert result == 0
    assert dest.is_dir()
    installed = {d.name for d in dest.iterdir()}
    assert "bizspec-refine" in installed
    assert "bizspec-run" in installed


def test_init_local_explicit(monkeypatch, tmp_path):
    """'1' を選択してもローカルにインストールされる"""
    dest = tmp_path / ".claude" / "skills"
    monkeypatch.setattr(init_cmd, "_local_dest", lambda: dest)
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = init_cmd.run_init(None)
    assert result == 0
    assert "bizspec-refine" in {d.name for d in dest.iterdir()}


def test_init_global(monkeypatch, tmp_path):
    """'2' を選択するとグローバルにインストールされる"""
    dest = tmp_path / ".claude" / "skills"
    monkeypatch.setattr(init_cmd, "_global_dest", lambda: dest)
    monkeypatch.setattr("builtins.input", lambda _: "2")
    result = init_cmd.run_init(None)
    assert result == 0
    assert dest.is_dir()
    assert "bizspec-refine" in {d.name for d in dest.iterdir()}


def test_init_invalid_choice(monkeypatch, capsys):
    """無効な選択肢は終了コード 1 を返す"""
    monkeypatch.setattr("builtins.input", lambda _: "9")
    result = init_cmd.run_init(None)
    assert result == 1


def test_init_overwrites_existing(monkeypatch, tmp_path):
    """既存のスキルディレクトリは上書きされる"""
    dest = tmp_path / ".claude" / "skills"
    stale = dest / "bizspec-refine"
    stale.mkdir(parents=True)
    (stale / "OLD.md").write_text("old content")

    monkeypatch.setattr(init_cmd, "_local_dest", lambda: dest)
    monkeypatch.setattr("builtins.input", lambda _: "")
    init_cmd.run_init(None)

    assert not (stale / "OLD.md").exists()
    assert (stale / "SKILL.md").exists()


def test_init_skill_md_content_matches_source(monkeypatch, tmp_path):
    """インストール後の SKILL.md がソースと同一内容である"""
    dest = tmp_path / ".claude" / "skills"
    monkeypatch.setattr(init_cmd, "_local_dest", lambda: dest)
    monkeypatch.setattr("builtins.input", lambda _: "")
    init_cmd.run_init(None)

    for skill_dir in init_cmd._SKILLS_SRC.iterdir():
        if not skill_dir.is_dir():
            continue
        src_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        dst_content = (dest / skill_dir.name / "SKILL.md").read_text(encoding="utf-8")
        assert src_content == dst_content, f"{skill_dir.name}/SKILL.md の内容が一致しません"
