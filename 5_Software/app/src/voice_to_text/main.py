#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       main.py
@brief      CLI entry point for VoiceToText application.
@details    Parses CLI arguments, loads config, and starts app runtime.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .app import VoiceToTextApp
from .config import DEFAULT_CONFIG_PATH, load_config
from .first_run import maybe_run_first_run_wizard
from .logging_setup import setup_logging
from .settings_cli import main as settings_cli_main


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def _configure_bundled_ffmpeg() -> None:
    """
    @brief      Prepend bundled ffmpeg directory to PATH when available.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    search_roots: list[Path] = []

    if getattr(sys, "frozen", False):
        search_roots.append(Path(sys.executable).resolve().parent)
    else:
        search_roots.append(Path.cwd())

    binary_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"

    for root in search_roots:
        candidate_dirs = [
            root / "ffmpeg" / "bin",
            root / "ffmpeg",
            root / "_internal" / "ffmpeg" / "bin",
            root / "_internal" / "ffmpeg",
        ]
        for candidate in candidate_dirs:
            ffmpeg_exe = candidate / binary_name
            if ffmpeg_exe.exists():
                current_path = os.environ.get("PATH", "")
                os.environ["PATH"] = f"{candidate}{os.pathsep}{current_path}"
                return

        # Fallback for packaging layouts that move binaries under nested folders.
        try:
            matches = list(root.rglob(binary_name))
        except OSError:
            matches = []
        if matches:
            ffmpeg_dir = matches[0].parent
            current_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{ffmpeg_dir}{os.pathsep}{current_path}"
            return


def _handle_noconsole_stdout() -> None:
    """
    @brief      Redirect stdout/stderr to a NullWriter if they are None.
    @details    PyInstaller's --noconsole mode on Windows sets sys.stdout and
                sys.stderr to None, causing libraries like tqdm to crash.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    class NullWriter:
        def write(self, *args, **kwargs):
            pass

        def flush(self, *args, **kwargs):
            pass

    if sys.stdout is None:
        sys.stdout = NullWriter()
    if sys.stderr is None:
        sys.stderr = NullWriter()


def main() -> None:
    """
    @brief      Launch VoiceToText from command line.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.1
    """
    _handle_noconsole_stdout()
    parser = argparse.ArgumentParser(description="Offline push-to-talk voice-to-text")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config")
    parser.add_argument("--tray", action="store_true", help="Run application in system tray mode")
    parser.add_argument("--open-settings", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.open_settings:
        raise SystemExit(settings_cli_main(args.config))

    _configure_bundled_ffmpeg()
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    maybe_run_first_run_wizard(config_path, args.tray)
    config = load_config(args.config)
    setup_logging(config)
    if args.tray:
        try:
            from .tray import VoiceToTextTray
        except ImportError as exc:
            raise RuntimeError(
                "Tray mode dependencies are missing. Install/update with: pip install -e .[dev]"
            ) from exc

        tray = VoiceToTextTray(config, config_path=config_path)
        tray.run()
        return

    app = VoiceToTextApp(config)
    app.run()


if __name__ == "__main__":
    main()


# ==============================================================================
# END OF FILE
# ==============================================================================
