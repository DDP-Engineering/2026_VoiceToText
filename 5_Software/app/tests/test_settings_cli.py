#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_settings_cli.py
@brief      Unit tests for standalone settings launcher behavior.
@details    Verifies fallback and process exit-code behavior for settings_cli.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from dataclasses import asdict

from voice_to_text.config import AppConfig
import voice_to_text.settings_cli as settings_cli


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_main_uses_defaults_when_config_load_fails(monkeypatch, tmp_path) -> None:
    """
    @brief      Verify malformed config fallback uses AppConfig defaults.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @param[in]  tmp_path       Temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    config_path = tmp_path / "config.yaml"

    def _load_raises(_path):
        raise ValueError("bad config")

    captured = {"config": None, "path": None}

    def _open_settings_window(cfg: AppConfig):
        captured["config"] = cfg
        cfg_map = asdict(cfg)
        cfg_map["model_size"] = "small"
        return AppConfig(**cfg_map)

    def _write_config(path, cfg: AppConfig) -> None:
        captured["path"] = path
        captured["written"] = cfg

    monkeypatch.setattr(settings_cli, "load_config", _load_raises)
    monkeypatch.setattr(settings_cli, "open_settings_window", _open_settings_window)
    monkeypatch.setattr(settings_cli, "write_config", _write_config)

    rc = settings_cli.main(str(config_path))
    assert rc == 0
    assert isinstance(captured["config"], AppConfig)
    assert captured["config"].model_size == "base"
    assert captured["path"] == config_path


def test_main_returns_2_on_cancel(monkeypatch, tmp_path) -> None:
    """
    @brief      Verify cancel returns code 2 and does not write config.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @param[in]  tmp_path       Temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    config_path = tmp_path / "config.yaml"
    write_called = {"value": False}

    monkeypatch.setattr(settings_cli, "load_config", lambda _path: AppConfig())
    monkeypatch.setattr(settings_cli, "open_settings_window", lambda _cfg: None)
    monkeypatch.setattr(settings_cli, "write_config", lambda _path, _cfg: write_called.__setitem__("value", True))

    rc = settings_cli.main(str(config_path))
    assert rc == 2
    assert write_called["value"] is False
# ==============================================================================
# END OF FILE
# ==============================================================================
