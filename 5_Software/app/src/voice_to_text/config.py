#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       config.py
@brief      Configuration loading and defaults for VoiceToText.
@details    Provides application configuration dataclass and YAML loader
            utilities for runtime configuration.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    2.0.0
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import platform
from typing import Any



# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def get_default_config_path() -> Path:
    """
    @brief      Resolve OS-specific default configuration file path.
    @return     Absolute path to default config file.
    @note       Windows: %APPDATA%\\DDP_VoiceToText\\config.yaml
    @note       Linux: $XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml or ~/.config/DDP_VoiceToText/config.yaml
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    system_name = platform.system().lower()

    if system_name == "windows":
        app_data = os.getenv("APPDATA")
        if app_data:
            return Path(app_data) / "DDP_VoiceToText" / "config.yaml"
        return Path.home() / "AppData" / "Roaming" / "DDP_VoiceToText" / "config.yaml"

    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "DDP_VoiceToText" / "config.yaml"

    return Path.home() / ".config" / "DDP_VoiceToText" / "config.yaml"


def get_default_recordings_dir() -> Path:
    """
    @brief      Resolve OS-specific default recordings directory.
    @return     Absolute path to recordings output directory.
    @note       Windows: %LOCALAPPDATA%\\DDP_VoiceToText\\recordings
    @note       Linux: $XDG_DATA_HOME/DDP_VoiceToText/recordings or ~/.local/share/DDP_VoiceToText/recordings
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    system_name = platform.system().lower()

    if system_name == "windows":
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "DDP_VoiceToText" / "recordings"
        return Path.home() / "AppData" / "Local" / "DDP_VoiceToText" / "recordings"

    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "DDP_VoiceToText" / "recordings"

    return Path.home() / ".local" / "share" / "DDP_VoiceToText" / "recordings"


def get_default_logs_dir() -> Path:
    """
    @brief      Resolve OS-specific default logs directory.
    @return     Absolute path to logs directory.
    @note       Windows: %APPDATA%\\DDP_VoiceToText\\logs
    @note       Linux: $XDG_STATE_HOME/DDP_VoiceToText/logs or ~/.local/state/DDP_VoiceToText/logs
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    system_name = platform.system().lower()

    if system_name == "windows":
        app_data = os.getenv("APPDATA")
        if app_data:
            return Path(app_data) / "DDP_VoiceToText" / "logs"
        return Path.home() / "AppData" / "Roaming" / "DDP_VoiceToText" / "logs"

    xdg_state_home = os.getenv("XDG_STATE_HOME")
    if xdg_state_home:
        return Path(xdg_state_home) / "DDP_VoiceToText" / "logs"

    return Path.home() / ".local" / "state" / "DDP_VoiceToText" / "logs"

# ==============================================================================
# CONSTANTS
# ==============================================================================


DEFAULT_CONFIG_PATH = get_default_config_path()


DEFAULT_CONFIG_TEMPLATE = """# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
#
# VoiceToText configuration file
# Location (default):
# - Windows: %APPDATA%\\DDP_VoiceToText\\config.yaml
# - Linux:   $XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml
#            (fallback ~/.config/DDP_VoiceToText/config.yaml)
#
# Hotkey used for push-to-talk.
# Examples: ctrl_r, ctrl_l, f9, a
push_to_talk_key: ctrl_r

# Record mode:
# - hold: press and hold to record
# - toggle: press once to start, press again to stop
record_mode: hold

# Whisper model size.
# Typical values: tiny, base, small, medium, large
model_size: base

# Source language code or auto.
# Examples: auto, en, de, ro
source_language: en

# Target language output:
# - empty string: keep source language
# - en: whisper native translate-to-english
# - other codes: via local Argos packages
target_language: "en"

# Audio capture sample rate (Hz).
sample_rate: 16000

# Number of microphone channels.
channels: 1

# Max hold-to-talk duration in seconds (0 disables limit).
max_record_seconds: 120

# Enable or disable beep feedback on recording start/stop.
enable_beep: true

# Recording start beep tone parameters.
beep_start_frequency_hz: 880
beep_start_duration_ms: 70

# Recording stop beep tone parameters.
beep_stop_frequency_hz: 520
beep_stop_duration_ms: 90

# Overlay options.
overlay_enabled: true
overlay_position: center

# Silence filtering options.
vad_enabled: true
vad_silence_ms: 900
vad_min_speech_ms: 250
vad_trim_leading: true
vad_trim_trailing: true

# Keep recorded audio files on disk after processing.
keep_recordings: false

# Maximum number of recordings to keep (0 disables count limit).
max_recordings: 0

# Maximum recording age in days (0 disables age-based cleanup).
max_recordings_age_days: 0

# Logging options.
enable_file_logging: true
log_level: INFO
log_rotation_when: midnight
log_rotation_interval: 1
log_backup_count: 7
logs_dir: "{logs_dir}"

# Folder used to store recorded wav files.
# Default uses OS-specific user data location.
recordings_dir: "{recordings_dir}"
"""


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


@dataclass(slots=True)
class AppConfig:
    """
    @brief      VoiceToText runtime configuration container.
    @details    Holds all configurable application parameters loaded from
                YAML or default values.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    2.0.0
    """
    push_to_talk_key: str = "ctrl_r"
    record_mode: str = "hold"
    model_size: str = "base"
    source_language: str = "en"
    target_language: str = "en"
    sample_rate: int = 16000
    channels: int = 1
    max_record_seconds: int = 120
    enable_beep: bool = True
    beep_start_frequency_hz: int = 880
    beep_start_duration_ms: int = 70
    beep_stop_frequency_hz: int = 520
    beep_stop_duration_ms: int = 90
    overlay_enabled: bool = True
    overlay_position: str = "center"
    vad_enabled: bool = True
    vad_silence_ms: int = 900
    vad_min_speech_ms: int = 250
    vad_threshold_multiplier: float = 3.0
    vad_trim_leading: bool = True
    vad_trim_trailing: bool = True
    keep_recordings: bool = False
    max_recordings: int = 0
    max_recordings_age_days: int = 0
    restore_clipboard: bool = False
    enable_file_logging: bool = True
    log_level: str = "INFO"
    log_rotation_when: str = "midnight"
    log_rotation_interval: int = 1
    log_backup_count: int = 7
    logs_dir: str = field(default_factory=lambda: str(get_default_logs_dir()))
    recordings_dir: str = field(default_factory=lambda: str(get_default_recordings_dir()))


def write_default_config(path: Path) -> None:
    """
    @brief      Create default YAML configuration file with documented fields.
    @param[in]  path    Target config file path.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    write_config(path, AppConfig())


def write_config(path: Path, config: AppConfig) -> None:
    """
    @brief      Write YAML configuration file from AppConfig values.
    @param[in]  path      Target config file path.
    @param[in]  config    Configuration values to persist.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to write config files.") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    config_data = {
        "push_to_talk_key": str(config.push_to_talk_key),
        "record_mode": str(config.record_mode),
        "model_size": str(config.model_size),
        "source_language": str(config.source_language),
        "target_language": str(config.target_language),
        "sample_rate": int(config.sample_rate),
        "channels": int(config.channels),
        "max_record_seconds": max(0, int(config.max_record_seconds)),
        "enable_beep": bool(config.enable_beep),
        "beep_start_frequency_hz": int(config.beep_start_frequency_hz),
        "beep_start_duration_ms": int(config.beep_start_duration_ms),
        "beep_stop_frequency_hz": int(config.beep_stop_frequency_hz),
        "beep_stop_duration_ms": int(config.beep_stop_duration_ms),
        "overlay_enabled": bool(config.overlay_enabled),
        "overlay_position": str(config.overlay_position),
        "vad_enabled": bool(config.vad_enabled),
        "vad_silence_ms": max(0, int(config.vad_silence_ms)),
        "vad_min_speech_ms": max(0, int(config.vad_min_speech_ms)),
        "vad_trim_leading": bool(config.vad_trim_leading),
        "vad_trim_trailing": bool(config.vad_trim_trailing),
        "keep_recordings": bool(config.keep_recordings),
        "max_recordings": max(0, int(config.max_recordings)),
        "max_recordings_age_days": max(0, int(config.max_recordings_age_days)),
        "enable_file_logging": bool(config.enable_file_logging),
        "log_level": str(config.log_level),
        "log_rotation_when": str(config.log_rotation_when),
        "log_rotation_interval": max(1, int(config.log_rotation_interval)),
        "log_backup_count": max(1, int(config.log_backup_count)),
        # Use POSIX-style separators in YAML to avoid Windows backslash escape issues.
        "logs_dir": Path(config.logs_dir).as_posix(),
        "recordings_dir": Path(config.recordings_dir).as_posix(),
    }

    header = (
        "# Copyright (c) 2026 DDP Engineering\n"
        "# This software is licensed under the GNU Affero General Public License v3.0\n"
        "# (AGPL-3.0) with additional Non-Commercial restriction.\n"
        "# See the LICENSE and LICENSE_NC.txt files for full license details.\n"
        "#\n"
        "# VoiceToText configuration file\n"
        "# - Windows default: %APPDATA%\\DDP_VoiceToText\\config.yaml\n"
        "# - Linux default:   $XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml\n"
        "#                    (fallback ~/.config/DDP_VoiceToText/config.yaml)\n"
    )
    yaml_text = yaml.safe_dump(config_data, sort_keys=False, allow_unicode=False)
    path.write_text(f"{header}\n{yaml_text}", encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    """
    @brief      Load YAML file as dictionary.
    @param[in]  path    Path to YAML configuration file.
    @return     Parsed configuration mapping.
    @exception  RuntimeError when PyYAML is not installed.
    @exception  ValueError when YAML root is not a mapping.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load config files.") from exc

    with path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config must be a map/object: {path}")

    return data


def _to_bool(value: Any, default: bool) -> bool:
    """
    @brief      Convert input value to bool with tolerant parsing.
    @param[in]  value      Raw input value.
    @param[in]  default    Fallback value for unrecognized types.
    @return     Parsed boolean.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def _to_int(value: Any, default: int, minimum: int | None = None) -> int:
    """
    @brief      Convert input value to int with fallback and lower bound.
    @param[in]  value       Raw input value.
    @param[in]  default     Fallback integer value.
    @param[in]  minimum     Optional minimum accepted value.
    @return     Parsed integer or bounded fallback.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    if minimum is not None:
        parsed = max(minimum, parsed)
    return parsed


def _normalize_overlay_position(value: Any) -> str:
    """
    @brief      Normalize overlay position token to supported values.
    @param[in]  value    Raw position token.
    @return     Normalized overlay position.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    normalized = str(value).strip().lower()
    allowed = {"center", "top-center", "low-center", "top-right", "top-left", "bottom-center"}
    if normalized not in allowed:
        return "center"
    if normalized == "bottom-center":
        return "low-center"
    return normalized


def load_config(path: str | Path | None = None) -> AppConfig:
    """
    @brief      Load application configuration.
    @param[in]  path    Optional explicit config file path.
    @return     AppConfig instance with user values or defaults.
    @note       Uses OS-specific default path when no path is provided.
    @note       Creates a default config file if missing.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        try:
            write_default_config(config_path)
        except OSError:
            # Continue with defaults when config path is not writable.
            return AppConfig()
        return AppConfig()

    data = _load_yaml(config_path)

    return AppConfig(
        push_to_talk_key=str(data.get("push_to_talk_key", "ctrl_r")),
        record_mode=str(data.get("record_mode", "hold")).strip().lower() or "hold",
        model_size=str(data.get("model_size", "base")),
        source_language=str(data.get("source_language", "en")),
        target_language=str(data.get("target_language", "en")),
        sample_rate=_to_int(data.get("sample_rate", 16000), 16000, minimum=1),
        channels=_to_int(data.get("channels", 1), 1, minimum=1),
        max_record_seconds=_to_int(data.get("max_record_seconds", 120), 120, minimum=0),
        enable_beep=_to_bool(data.get("enable_beep", True), True),
        beep_start_frequency_hz=_to_int(data.get("beep_start_frequency_hz", 880), 880, minimum=1),
        beep_start_duration_ms=_to_int(data.get("beep_start_duration_ms", 70), 70, minimum=1),
        beep_stop_frequency_hz=_to_int(data.get("beep_stop_frequency_hz", 520), 520, minimum=1),
        beep_stop_duration_ms=_to_int(data.get("beep_stop_duration_ms", 90), 90, minimum=1),
        overlay_enabled=_to_bool(data.get("overlay_enabled", True), True),
        overlay_position=_normalize_overlay_position(data.get("overlay_position", "center")),
        vad_enabled=_to_bool(data.get("vad_enabled", True), True),
        vad_silence_ms=_to_int(data.get("vad_silence_ms", 900), 900, minimum=0),
        vad_min_speech_ms=_to_int(data.get("vad_min_speech_ms", 250), 250, minimum=0),
        vad_threshold_multiplier=float(data.get("vad_threshold_multiplier", 3.0)),
        vad_trim_leading=_to_bool(data.get("vad_trim_leading", True), True),
        vad_trim_trailing=_to_bool(data.get("vad_trim_trailing", True), True),
        keep_recordings=_to_bool(data.get("keep_recordings", False), False),
        max_recordings=_to_int(data.get("max_recordings", 0), 0, minimum=0),
        max_recordings_age_days=_to_int(data.get("max_recordings_age_days", 0), 0, minimum=0),
        restore_clipboard=_to_bool(data.get("restore_clipboard", False), False),
        enable_file_logging=_to_bool(data.get("enable_file_logging", True), True),
        log_level=str(data.get("log_level", "INFO")),
        log_rotation_when=str(data.get("log_rotation_when", "midnight")),
        log_rotation_interval=_to_int(data.get("log_rotation_interval", 1), 1, minimum=1),
        log_backup_count=_to_int(data.get("log_backup_count", 7), 7, minimum=1),
        logs_dir=str(data.get("logs_dir", str(get_default_logs_dir()))),
        recordings_dir=str(data.get("recordings_dir", str(get_default_recordings_dir()))),
    )


# ==============================================================================
# END OF FILE
# ==============================================================================
