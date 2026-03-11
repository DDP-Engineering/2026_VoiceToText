#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_app_behavior.py
@brief      Unit tests for VoiceToTextApp runtime behavior.
@details    Covers hotkey alias parsing and Esc handling policy.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from pynput.keyboard import Key, KeyCode

from voice_to_text.app import VoiceToTextApp
from voice_to_text.config import AppConfig
import voice_to_text.app as app_module


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================
class _DummyRecorder:
    def __init__(self, sample_rate: int, channels: int) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.started = False

    def start(self) -> None:
        self.started = True
        return

    def stop_to_wav(self, _path) -> bool:
        return False

    def stop_discard(self) -> None:
        return


class _DummyTranscriber:
    def __init__(self, model_size: str, **_kwargs) -> None:
        self.model_size = model_size

    def transcribe(self, **_kwargs):
        return "", "unknown"


class _DummyPaster:
    def paste(self, _text: str) -> None:
        return


class _DummyFeedback:
    def __init__(self, **_kwargs) -> None:
        return

    def recording_started(self) -> None:
        return

    def recording_stopped(self) -> None:
        return


class _DummyOverlay:
    def __init__(self, **_kwargs) -> None:
        from threading import Event
        self.state = "hidden"
        self._ui_ready = Event()
        self._ui_ready.set()

    def show_recording(self) -> None:
        self.state = "recording"

    def show_processing(self) -> None:
        self.state = "processing"

    def hide(self) -> None:
        self.state = "hidden"

    def show_error(self) -> None:
        self.state = "error"

    def close(self) -> None:
        return


class _DummyListener:
    def __init__(self, on_press, on_release) -> None:
        self._on_press = on_press
        self._on_release = on_release

    def start(self) -> None:
        return

    def join(self) -> None:
        return

    def stop(self) -> None:
        return


def _patch_runtime_dependencies(monkeypatch) -> None:
    """
    @brief      Patch heavy runtime dependencies for fast unit tests.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    """
    monkeypatch.setattr(app_module, "HoldRecorder", _DummyRecorder)
    monkeypatch.setattr(app_module, "WhisperTranscriber", _DummyTranscriber)
    monkeypatch.setattr(app_module, "TextPaster", _DummyPaster)
    monkeypatch.setattr(app_module, "ToneFeedback", _DummyFeedback)
    monkeypatch.setattr(app_module, "CaptureOverlay", _DummyOverlay)
    monkeypatch.setattr(app_module, "Listener", _DummyListener)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_hotkey_alias_rctrl_maps_to_ctrl_r(monkeypatch) -> None:
    """
    @brief      Verify rctrl alias maps to Key.ctrl_r.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig(push_to_talk_key="rctrl")
    app = VoiceToTextApp(cfg)
    assert app._hotkey == Key.ctrl_r


def test_hotkey_single_char_maps_to_keycode(monkeypatch) -> None:
    """
    @brief      Verify single character hotkey maps to KeyCode.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig(push_to_talk_key="a")
    app = VoiceToTextApp(cfg)
    assert isinstance(app._hotkey, KeyCode)
    assert app._hotkey.char == "a"


def test_on_release_esc_exits_when_enabled(monkeypatch) -> None:
    """
    @brief      Verify Esc exits listener when esc_to_exit is enabled.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig(push_to_talk_key="f9")
    app = VoiceToTextApp(cfg, esc_to_exit=True)

    called = {"stop": False}

    def _stop_stub() -> None:
        called["stop"] = True

    app.stop = _stop_stub
    result = app._on_release(Key.esc)

    assert result is False
    assert called["stop"] is True


def test_on_release_esc_ignored_in_tray_mode(monkeypatch) -> None:
    """
    @brief      Verify Esc is ignored when esc_to_exit is disabled.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig(push_to_talk_key="f9")
    app = VoiceToTextApp(cfg, esc_to_exit=False)

    called = {"stop": False}

    def _stop_stub() -> None:
        called["stop"] = True

    app.stop = _stop_stub
    result = app._on_release(Key.esc)

    assert result is True
    assert called["stop"] is False


def test_toggle_mode_press_starts_and_second_press_stops(monkeypatch) -> None:
    """
    @brief      Verify toggle mode starts on first press and stops on second press.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig(push_to_talk_key="f9", record_mode="toggle")
    app = VoiceToTextApp(cfg)

    finalized = {"count": 0}

    def _finalize_stub(_session_id: int) -> None:
        finalized["count"] += 1

    app._finalize_recording = _finalize_stub

    app._on_press(Key.f9)
    assert app._recording is True
    app._on_release(Key.f9)
    app._on_press(Key.f9)

    assert app._recording is False
    assert finalized["count"] == 1


def test_app_starts_and_stops_worker(monkeypatch) -> None:
    """
    @brief      Verify worker thread lifecycle during app start/stop.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    _patch_runtime_dependencies(monkeypatch)
    cfg = AppConfig()
    app = VoiceToTextApp(cfg)
    
    app.start()
    assert app._worker_thread is not None
    assert app._worker_running.is_set()
    
    app.stop()
    assert not app._worker_running.is_set()
    # Check sentinel
    assert app._job_queue.get() == (-1, -1)
# ==============================================================================
# END OF FILE
# ==============================================================================
