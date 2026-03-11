#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       first_run.py
@brief      First-run interactive configuration wizard.
@details    Prompts user for core settings when config file is missing.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import sys
from pathlib import Path

from pynput.keyboard import Key

from .config import AppConfig, write_config


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def maybe_run_first_run_wizard(config_path: Path, tray_mode: bool) -> None:
    """
    @brief      Run first-run wizard when config is missing and terminal is interactive.
    @param[in]  config_path    Target config file path.
    @param[in]  tray_mode      Whether app is launching in tray mode.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    if config_path.exists():
        return

    # In tray mode and non-interactive launches, skip prompts.
    if tray_mode or not sys.stdin.isatty():
        _safe_write_config(config_path, AppConfig())
        return

    print("First-run setup for VoiceToText")
    print("Press Enter to keep defaults shown in [].")

    source_language = _ask("Source language (auto/en/ro/de)", "en").strip().lower() or "en"
    target_language = _ask("Target language (empty keeps source, en for english)", "en").strip().lower()
    hotkey = _ask_hotkey("ctrl_r")
    enable_beep = _ask_bool("Enable beep feedback", True)

    config = AppConfig(
        source_language=source_language,
        target_language=target_language,
        push_to_talk_key=hotkey,
        enable_beep=enable_beep,
    )
    if _safe_write_config(config_path, config):
        print(f"Config created: {config_path}")
    else:
        print("Config write failed; continuing with runtime defaults.")


def _ask(prompt: str, default: str) -> str:
    """
    @brief      Prompt user for string input with default.
    @param[in]  prompt     Question prompt text.
    @param[in]  default    Default fallback value.
    @return     User-entered string or default.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    try:
        value = input(f"{prompt} [{default}]: ")
    except (EOFError, OSError):
        return default
    if not value:
        return default
    return value


def _ask_bool(prompt: str, default: bool) -> bool:
    """
    @brief      Prompt user for boolean input with default.
    @param[in]  prompt     Question prompt text.
    @param[in]  default    Default boolean value.
    @return     Parsed boolean.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    default_label = "Y/n" if default else "y/N"
    try:
        value = input(f"{prompt} [{default_label}]: ").strip().lower()
    except (EOFError, OSError):
        return default
    if not value:
        return default
    return value in {"y", "yes", "1", "true", "on"}


def _ask_hotkey(default: str) -> str:
    """
    @brief      Prompt user for hotkey and validate supported format.
    @param[in]  default    Default hotkey value.
    @return     Validated hotkey token.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    key_aliases = {
        "rctrl": "ctrl_r",
        "right_ctrl": "ctrl_r",
        "rightctrl": "ctrl_r",
        "lctrl": "ctrl_l",
        "left_ctrl": "ctrl_l",
        "leftctrl": "ctrl_l",
        "ralt": "alt_r",
        "right_alt": "alt_r",
        "rightalt": "alt_r",
        "lalt": "alt_l",
        "left_alt": "alt_l",
        "leftalt": "alt_l",
    }
    examples = "ctrl_r, ctrl_l, alt_r, alt_l, f9, a"

    while True:
        value = _ask("Push-to-talk hotkey", default).strip().lower() or default
        normalized = key_aliases.get(value, value)
        if len(normalized) == 1 or hasattr(Key, normalized):
            return normalized
        print(f"Unsupported hotkey '{value}'. Examples: {examples}")


def _safe_write_config(config_path: Path, config: AppConfig) -> bool:
    """
    @brief      Write config file and tolerate filesystem errors.
    @param[in]  config_path    Target config path.
    @param[in]  config         Config object to persist.
    @return     True when write succeeds; otherwise False.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    try:
        write_config(config_path, config)
        return True
    except (OSError, RuntimeError) as exc:
        print(f"[first-run] warning: failed to write config: {exc}", file=sys.stderr)
        return False


# ==============================================================================
# END OF FILE
# ==============================================================================
