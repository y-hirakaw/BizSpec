from __future__ import annotations

from pathlib import Path

from bizspec.core.config import DEFAULT_CONFIG, load_config


class TestLoadConfig:
    def test_returns_defaults_when_missing(self, tmp_path: Path):
        cfg = load_config(tmp_path)
        assert cfg == DEFAULT_CONFIG
        # safety: must be an independent copy, not a shared reference
        cfg["viz"]["heatmap"]["cost_mode"] = "fixed"
        assert DEFAULT_CONFIG["viz"]["heatmap"]["cost_mode"] == "relative"

    def test_returns_defaults_on_invalid_yaml(self, tmp_path: Path):
        (tmp_path / "config.yaml").write_text(": invalid: yaml :", encoding="utf-8")
        cfg = load_config(tmp_path)
        assert cfg == DEFAULT_CONFIG

    def test_returns_defaults_on_non_dict_root(self, tmp_path: Path):
        (tmp_path / "config.yaml").write_text("- just\n- a list\n", encoding="utf-8")
        cfg = load_config(tmp_path)
        assert cfg == DEFAULT_CONFIG

    def test_deep_merge_overrides_only_specified_keys(self, tmp_path: Path):
        (tmp_path / "config.yaml").write_text(
            "viz:\n  heatmap:\n    cost_mode: fixed\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg["viz"]["heatmap"]["cost_mode"] == "fixed"
        # Other keys preserved from defaults
        assert cfg["viz"]["heatmap"]["cost_thresholds"] == [1, 4, 20]
        assert cfg["viz"]["flow"]["cost_mode"] == "relative"

    def test_user_thresholds_replace_defaults(self, tmp_path: Path):
        (tmp_path / "config.yaml").write_text(
            "viz:\n  heatmap:\n    cost_thresholds: [2, 8, 40]\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg["viz"]["heatmap"]["cost_thresholds"] == [2, 8, 40]

    def test_unknown_keys_pass_through(self, tmp_path: Path):
        (tmp_path / "config.yaml").write_text(
            "viz:\n  heatmap:\n    cost_mode: relative\n  future_feature: \"yes\"\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg["viz"]["future_feature"] == "yes"


class TestInitConfigTemplate:
    """init コマンドが書き出すテンプレが load_config で問題なくロードできること。"""

    def test_template_loads_to_defaults(self, tmp_path: Path):
        from bizspec.init_cmd import _CONFIG_YAML_TEMPLATE

        (tmp_path / "config.yaml").write_text(_CONFIG_YAML_TEMPLATE, encoding="utf-8")
        cfg = load_config(tmp_path)
        assert cfg == DEFAULT_CONFIG
