#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       settings_cli.py
@brief      Standalone settings window launcher.
@details    Runs settings UI in a separate process to avoid tray/UI thread
            conflicts with Tkinter.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import argparse
from pathlib import Path

from .config import AppConfig, DEFAULT_CONFIG_PATH, load_config, write_config
from .settings_ui import open_settings_window


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def main(config_path_override: str | None = None) -> int:
    """
    @brief      Run settings popup and persist config when saved.
    @return     Process exit code (0 saved, 2 canceled, 1 error).
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    if config_path_override is None:
        parser = argparse.ArgumentParser(description="VoiceToText settings popup")
        parser.add_argument("--config", type=str, default=None, help="Path to YAML config")
        args = parser.parse_args()
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path_override)
    try:
        current_config = load_config(config_path)
    except Exception:
        current_config = AppConfig()

    updated_config = open_settings_window(current_config)
    if updated_config is None:
        return 2

    try:
        write_config(config_path, updated_config)
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ==============================================================================
# END OF FILE
# ==============================================================================
