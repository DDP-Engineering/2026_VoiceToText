#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_tray.py
@brief      Unit tests for tray lifecycle guards.
@details    Verifies shutdown prevents service restart.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from pathlib import Path

from voice_to_text.config import AppConfig
from voice_to_text.tray import VoiceToTextTray
import voice_to_text.tray as tray_module


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================
class _DummyApp:
    def __init__(self, _config, esc_to_exit=False) -> None:
        self.stopped = False

    def run(self) -> None:
        return

    def stop(self) -> None:
        self.stopped = True


class _DummyIcon:
    def run(self) -> None:
        return

    def stop(self) -> None:
        return

    def update_menu(self) -> None:
        return


def _build_test_tray(monkeypatch) -> VoiceToTextTray:
    monkeypatch.setattr(tray_module, "VoiceToTextApp", _DummyApp)
    monkeypatch.setattr(VoiceToTextTray, "_build_icon", lambda self: _DummyIcon())
    return VoiceToTextTray(AppConfig(), config_path=Path("config.yaml"))


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_start_service_ignored_while_shutting_down(monkeypatch) -> None:
    """
    @brief      Verify start guard blocks service startup during shutdown.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    tray = _build_test_tray(monkeypatch)
    tray._shutting_down = True
    tray._start_service()
    assert tray._is_running() is False


def test_on_exit_sets_shutdown_flag(monkeypatch) -> None:
    """
    @brief      Verify exit callback marks shutting down before stop.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    tray = _build_test_tray(monkeypatch)
    icon = _DummyIcon()
    tray._on_exit(icon, None)
    assert tray._shutting_down is True
# ==============================================================================
# END OF FILE
# ==============================================================================
