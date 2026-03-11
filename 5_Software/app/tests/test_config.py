#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_config.py
@brief      Unit tests for VoiceToText configuration loading.
@details    Verifies default fallback behavior and YAML value mapping.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from pathlib import Path

from voice_to_text.config import AppConfig, get_default_config_path, load_config


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_load_config_default_when_missing(tmp_path: Path) -> None:
    """
    @brief      Verify defaults are returned when config file is missing.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    cfg = load_config(tmp_path / "missing.yaml")
    assert isinstance(cfg, AppConfig)
    assert cfg.push_to_talk_key == "ctrl_r"
    assert cfg.model_size == "base"
    assert cfg.source_language == "en"
    assert cfg.target_language == "en"
    assert cfg.record_mode == "hold"
    assert cfg.max_record_seconds == 120
    assert cfg.overlay_enabled is True
    assert cfg.vad_enabled is True
    assert cfg.keep_recordings is False


def test_load_config_values(tmp_path: Path) -> None:
    """
    @brief      Verify YAML values are mapped into AppConfig.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "push_to_talk_key: f8\nmodel_size: base\nsource_language: de\ntarget_language: en\n",
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.push_to_talk_key == "f8"
    assert cfg.model_size == "base"
    assert cfg.source_language == "de"
    assert cfg.target_language == "en"


def test_load_config_beep_values(tmp_path: Path) -> None:
    """
    @brief      Verify beep-related config values are parsed correctly.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config_beep.yaml"
    config_path.write_text(
        "enable_beep: false\n"
        "beep_start_frequency_hz: 1200\n"
        "beep_start_duration_ms: 50\n"
        "beep_stop_frequency_hz: 400\n"
        "beep_stop_duration_ms: 120\n",
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.enable_beep is False
    assert cfg.beep_start_frequency_hz == 1200
    assert cfg.beep_start_duration_ms == 50
    assert cfg.beep_stop_frequency_hz == 400
    assert cfg.beep_stop_duration_ms == 120


def test_load_config_keep_recordings_true(tmp_path: Path) -> None:
    """
    @brief      Verify keep_recordings toggle is parsed correctly.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config_keep.yaml"
    config_path.write_text("keep_recordings: true\n", encoding="utf-8")

    cfg = load_config(config_path)
    assert cfg.keep_recordings is True


def test_load_config_recording_retention_values(tmp_path: Path) -> None:
    """
    @brief      Verify recording retention config values are parsed correctly.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config_retention.yaml"
    config_path.write_text(
        "max_record_seconds: 180\n"
        "max_recordings: 25\n"
        "max_recordings_age_days: 14\n",
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.max_record_seconds == 180
    assert cfg.max_recordings == 25
    assert cfg.max_recordings_age_days == 14


def test_load_config_logging_values(tmp_path: Path) -> None:
    """
    @brief      Verify logging-related config values are parsed correctly.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config_logging.yaml"
    config_path.write_text(
        "enable_file_logging: true\n"
        "log_level: DEBUG\n"
        "log_rotation_when: D\n"
        "log_rotation_interval: 2\n"
        "log_backup_count: 7\n"
        "logs_dir: C:/Temp/DDP_VoiceToText/logs\n",
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.enable_file_logging is True
    assert cfg.log_level == "DEBUG"
    assert cfg.log_rotation_when == "D"
    assert cfg.log_rotation_interval == 2
    assert cfg.log_backup_count == 7
    assert cfg.logs_dir == "C:/Temp/DDP_VoiceToText/logs"


def test_load_config_overlay_and_vad_values(tmp_path: Path) -> None:
    """
    @brief      Verify overlay and VAD config values are parsed correctly.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "config_overlay_vad.yaml"
    config_path.write_text(
        "record_mode: toggle\n"
        "overlay_enabled: false\n"
        "overlay_position: top-right\n"
        "vad_enabled: true\n"
        "vad_silence_ms: 1200\n"
        "vad_min_speech_ms: 300\n",
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.record_mode == "toggle"
    assert cfg.overlay_enabled is False
    assert cfg.overlay_position == "top-right"
    assert cfg.vad_enabled is True
    assert cfg.vad_silence_ms == 1200
    assert cfg.vad_min_speech_ms == 300
    assert cfg.vad_threshold_multiplier == 3.0
    assert cfg.restore_clipboard is False


def test_load_config_creates_missing_file(tmp_path: Path) -> None:
    """
    @brief      Verify missing config file is auto-created.
    @param[in]  tmp_path    Pytest temporary directory fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    config_path = tmp_path / "autocreated.yaml"
    assert not config_path.exists()

    cfg = load_config(config_path)

    assert isinstance(cfg, AppConfig)
    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    assert "push_to_talk_key" in content
    assert "recordings_dir" in content
    assert "record_mode" in content
    assert "vad_enabled" in content


def test_default_config_path_windows(monkeypatch) -> None:
    """
    @brief      Verify default config path resolution on Windows.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    monkeypatch.setattr("voice_to_text.config.platform.system", lambda: "Windows")
    monkeypatch.setenv("APPDATA", r"C:\Users\tester\AppData\Roaming")

    path = get_default_config_path()
    assert str(path).endswith(r"AppData\Roaming\DDP_VoiceToText\config.yaml")


def test_default_config_path_linux(monkeypatch) -> None:
    """
    @brief      Verify default config path resolution on Linux.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    monkeypatch.setattr("voice_to_text.config.platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/test_xdg_config")

    path = get_default_config_path()
    assert path.as_posix().endswith("/tmp/test_xdg_config/DDP_VoiceToText/config.yaml")
# ==============================================================================
# END OF FILE
# ==============================================================================
