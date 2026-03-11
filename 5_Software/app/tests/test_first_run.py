#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_first_run.py
@brief      Unit tests for first-run wizard behavior.
@details    Validates interactive/non-interactive flows and hotkey handling.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from pathlib import Path

from voice_to_text import first_run


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_first_run_noninteractive_write_failure_is_tolerated(tmp_path: Path, monkeypatch) -> None:
    """
    @brief      Verify non-interactive first-run does not crash on write failure.
    @param[in]  tmp_path       Pytest temporary directory fixture.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config.yaml"

    class _StdinStub:
        @staticmethod
        def isatty() -> bool:
            return False

    monkeypatch.setattr(first_run.sys, "stdin", _StdinStub())

    def _raise_write(_path, _cfg):
        raise OSError("simulated write failure")

    monkeypatch.setattr(first_run, "write_config", _raise_write)

    first_run.maybe_run_first_run_wizard(config_path, tray_mode=False)
    assert not config_path.exists()


def test_first_run_interactive_hotkey_alias_is_normalized(tmp_path: Path, monkeypatch) -> None:
    """
    @brief      Verify wizard normalizes hotkey aliases before writing config.
    @param[in]  tmp_path       Pytest temporary directory fixture.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config.yaml"

    class _StdinStub:
        @staticmethod
        def isatty() -> bool:
            return True

    monkeypatch.setattr(first_run.sys, "stdin", _StdinStub())

    answers = iter(["ro", "en", "rctrl", "y"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    captured = {}

    def _capture_write(_path, cfg):
        captured["path"] = _path
        captured["cfg"] = cfg

    monkeypatch.setattr(first_run, "write_config", _capture_write)

    first_run.maybe_run_first_run_wizard(config_path, tray_mode=False)

    assert captured["path"] == config_path
    assert captured["cfg"].source_language == "ro"
    assert captured["cfg"].target_language == "en"
    assert captured["cfg"].push_to_talk_key == "ctrl_r"
    assert captured["cfg"].enable_beep is True


def test_first_run_interactive_invalid_hotkey_reprompts(tmp_path: Path, monkeypatch) -> None:
    """
    @brief      Verify wizard reprompts when hotkey is invalid.
    @param[in]  tmp_path       Pytest temporary directory fixture.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config.yaml"

    class _StdinStub:
        @staticmethod
        def isatty() -> bool:
            return True

    monkeypatch.setattr(first_run.sys, "stdin", _StdinStub())

    answers = iter(["en", "", "notakey", "lctrl", "n"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    captured = {}

    def _capture_write(_path, cfg):
        captured["cfg"] = cfg

    monkeypatch.setattr(first_run, "write_config", _capture_write)

    first_run.maybe_run_first_run_wizard(config_path, tray_mode=False)

    assert captured["cfg"].push_to_talk_key == "ctrl_l"
    assert captured["cfg"].enable_beep is False
# ==============================================================================
# END OF FILE
# ==============================================================================
