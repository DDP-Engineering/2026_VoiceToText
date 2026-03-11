#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       tray.py
@brief      System tray integration for VoiceToText runtime control.
@details    Provides a tray icon with start/stop/open-config/exit actions.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import logging
import os
import platform
from pathlib import Path
import subprocess
import sys
from threading import Lock, Thread

from .app import VoiceToTextApp
from .config import AppConfig, DEFAULT_CONFIG_PATH, load_config, write_default_config
from .logging_setup import setup_logging
from .overlay import CaptureOverlay


logger = logging.getLogger(__name__)


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class VoiceToTextTray:
    """
    @brief      Tray controller for VoiceToText service lifecycle.
    @details    Hosts a tray icon and controls app start/stop in background.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    2.0.0
    """

    def __init__(self, config: AppConfig, config_path: Path | None = None) -> None:
        """
        @brief      Initialize tray controller.
        @param[in]  config         Runtime configuration for VoiceToText app.
        @param[in]  config_path    Optional explicit config file path.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        self._config = config
        self._config_path = config_path or DEFAULT_CONFIG_PATH
        self._app = VoiceToTextApp(config, esc_to_exit=False)
        self._worker: Thread | None = None
        self._worker_lock = Lock()
        self._settings_lock = Lock()
        self._settings_open = False
        self._running = False
        self._shutting_down = False
        self._icon = self._build_icon()

    def run(self) -> None:
        """
        @brief      Run tray icon main loop.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        self._start_service()
        self._icon.run()

    def _build_icon(self):
        """
        @brief      Build tray icon and menu.
        @return     pystray.Icon instance.
        """
        import pystray
        from PIL import Image, ImageDraw

        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((6, 6, 58, 58), fill=(26, 120, 225, 255))
        draw.rectangle((28, 14, 36, 42), fill=(255, 255, 255, 255))
        draw.rectangle((22, 42, 42, 48), fill=(255, 255, 255, 255))

        menu = pystray.Menu(
            pystray.MenuItem("Start", self._on_start, enabled=lambda _item: not self._is_running()),
            pystray.MenuItem("Stop", self._on_stop, enabled=lambda _item: self._is_running()),
            pystray.MenuItem("Settings...", self._on_settings),
            pystray.MenuItem("Open Config", self._on_open_config),
            pystray.MenuItem("Open Logs", self._on_open_logs),
            pystray.MenuItem("Exit", self._on_exit),
        )
        return pystray.Icon("VoiceToText", image, "VoiceToText", menu)

    def _is_running(self) -> bool:
        """
        @brief      Read running state with lock protection.
        @return     True when service is running.
        """
        with self._worker_lock:
            return self._running

    def _start_service(self) -> None:
        """
        @brief      Start background VoiceToText service if not running.
        @return     None
        """
        with self._worker_lock:
            if self._running or self._shutting_down:
                return

            def worker_run() -> None:
                try:
                    self._app.run()
                finally:
                    with self._worker_lock:
                        self._running = False
                        self._worker = None

            self._running = True
            self._worker = Thread(target=worker_run, name="VoiceToTextWorker", daemon=True)
            try:
                self._worker.start()
            except Exception:
                self._running = False
                self._worker = None
                raise

    def _stop_service(self) -> None:
        """
        @brief      Stop background VoiceToText service if running.
        @return     None
        """
        worker: Thread | None
        with self._worker_lock:
            worker = self._worker
            if not self._running:
                return
            self._running = False

        self._app.stop()
        if worker is not None:
            worker.join(timeout=3.0)

    def _on_start(self, icon, _item) -> None:
        """
        @brief      Tray callback for start action.
        @param[in]  icon    Tray icon instance.
        @return     None
        """
        self._start_service()
        icon.update_menu()

    def _on_stop(self, icon, _item) -> None:
        """
        @brief      Tray callback for stop action.
        @param[in]  icon    Tray icon instance.
        @return     None
        """
        def stop_worker() -> None:
            self._stop_service()
            icon.update_menu()

        Thread(target=stop_worker, name="VoiceToTextStop", daemon=True).start()

    def _on_open_config(self, _icon, _item) -> None:
        """
        @brief      Tray callback to open user config file.
        @return     None
        """
        config_path = self._config_path
        if not config_path.exists():
            write_default_config(config_path)

        system_name = platform.system().lower()
        try:
            if system_name == "windows":
                os.startfile(str(config_path))
            else:
                subprocess.Popen(["xdg-open", str(config_path)])
        except Exception as exc:
            logger.error("[tray] open config failed: %s", exc)

    def _on_open_logs(self, _icon, _item) -> None:
        """
        @brief      Tray callback to open logs directory.
        @return     None
        """
        logs_dir = Path(self._config.logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)

        system_name = platform.system().lower()
        try:
            if system_name == "windows":
                os.startfile(str(logs_dir))
            else:
                subprocess.Popen(["xdg-open", str(logs_dir)])
        except Exception as exc:
            logger.error("[tray] open logs failed: %s", exc)

    def _on_settings(self, icon, _item) -> None:
        """
        @brief      Tray callback to open popup settings editor.
        @param[in]  icon    Tray icon instance.
        @return     None
        """
        with self._settings_lock:
            if self._settings_open:
                logger.info("[tray] settings window is already open")
                return
            self._settings_open = True

        def settings_worker() -> None:
            try:
                was_running = self._is_running()
                if was_running:
                    self._stop_service()

                if getattr(sys, "frozen", False):
                    command = [
                        sys.executable,
                        "--open-settings",
                        "--config",
                        str(self._config_path),
                    ]
                else:
                    command = [
                        sys.executable,
                        "-m",
                        "voice_to_text.settings_cli",
                        "--config",
                        str(self._config_path),
                    ]

                try:
                    result = subprocess.run(command, check=False, timeout=600)
                except Exception as exc:
                    logger.error("[tray] settings UI launch failed: %s", exc)
                    if was_running and not self._shutting_down:
                        self._start_service()
                    return

                if result.returncode not in (0, 2):
                    logger.error("[tray] settings UI failed with exit code %d", result.returncode)
                    if was_running and not self._shutting_down:
                        self._start_service()
                    return
                if result.returncode == 2:
                    if was_running and not self._shutting_down:
                        self._start_service()
                    return

                # Reload persisted config to ensure canonical parsing and defaults.
                try:
                    self._config = load_config(self._config_path)
                except Exception as exc:
                    logger.error("[tray] failed to reload config: %s", exc)
                    if was_running and not self._shutting_down:
                        self._start_service()
                    return

                setup_logging(self._config)
                loading_overlay = CaptureOverlay(
                    enabled=self._config.overlay_enabled,
                    position=self._config.overlay_position,
                )
                loading_overlay.show_loading()
                try:
                    self._app = VoiceToTextApp(self._config, esc_to_exit=False)
                finally:
                    loading_overlay.hide()
                    loading_overlay.close()
                if was_running and not self._shutting_down:
                    self._start_service()
                icon.update_menu()
            finally:
                with self._settings_lock:
                    self._settings_open = False

        Thread(target=settings_worker, name="VoiceToTextSettings", daemon=True).start()

    def _on_exit(self, icon, _item) -> None:
        """
        @brief      Tray callback for application exit.
        @param[in]  icon    Tray icon instance.
        @return     None
        """
        with self._worker_lock:
            self._shutting_down = True
        self._stop_service()
        icon.stop()


# ==============================================================================
# END OF FILE
# ==============================================================================
