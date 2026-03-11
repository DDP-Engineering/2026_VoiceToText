#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       overlay.py
@brief      Lightweight recording status overlay.
@details    Displays a small always-on-top visual indicator while recording
            and processing speech input.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import atexit
import logging
from queue import Empty, Queue
from threading import Event, Thread, current_thread
from typing import Literal


# ==============================================================================
# CONSTANTS
# ==============================================================================


logger = logging.getLogger(__name__)


_POSITION = Literal["center", "top-right", "top-left", "top-center", "low-center", "bottom-center"]


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================
class CaptureOverlay:
    """
    @brief      Small visual overlay for capture/processing states.
    @details    Uses Tkinter when available. If overlay creation fails,
                methods degrade to no-op behavior.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-21
    @version    2.0.0
    """

    def __init__(
        self,
        enabled: bool = True,
        position: _POSITION = "center",
    ) -> None:
        """
        @brief      Initialize capture overlay.
        @param[in]  enabled               Enable/disable overlay.
        @param[in]  position              Overlay position token.
        """
        self._enabled = bool(enabled)
        self._position: _POSITION = (
            position
            if position in {"center", "top-right", "top-left", "top-center", "low-center", "bottom-center"}
            else "center"
        )
        self._state = "hidden"
        self._ui_ready = Event()
        self._closed = Event()
        self._command_queue: Queue[str] = Queue()
        self._thread: Thread | None = None

        if not self._enabled:
            self._ui_ready.set()
            return

        try:
            import tkinter  # noqa: F401
        except Exception as exc:
            logger.warning("[overlay] tkinter unavailable: %s", exc)
            self._enabled = False
            self._ui_ready.set()
            return

        self._thread = Thread(target=self._ui_thread_main, name="VoiceToTextOverlay", daemon=True)
        self._thread.start()
        self._ui_ready.wait(timeout=1.0)
        atexit.register(self.close)

    def show_recording(self) -> None:
        """
        @brief      Show recording state overlay.
        @return     None
        """
        self._enqueue("recording")

    def show_processing(self) -> None:
        """
        @brief      Show processing state overlay.
        @return     None
        """
        self._enqueue("processing")

    def show_error(self) -> None:
        """
        @brief      Show error state briefly.
        @return     None
        """
        self._enqueue("error")

    def show_loading(self) -> None:
        """
        @brief      Show loading/wait state.
        @return     None
        """
        self._enqueue("loading")

    def hide(self) -> None:
        """
        @brief      Hide overlay window.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        self._enqueue("hide")

    def close(self) -> None:
        """
        @brief      Stop overlay UI thread and release UI resources.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        if self._closed.is_set():
            return
        self._command_queue.put("shutdown")
        self._closed.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            if thread.ident != current_thread().ident:
                thread.join(timeout=1.0)

    def _enqueue(self, command: str) -> None:
        if not self._enabled or self._closed.is_set():
            return
        self._command_queue.put(command)

    def _ui_thread_main(self) -> None:
        try:
            import tkinter as tk
        except Exception:
            self._enabled = False
            self._ui_ready.set()
            return

        try:
            root = tk.Tk()
            root.withdraw()
            window = tk.Toplevel(root)
            window.withdraw()
            window.overrideredirect(True)
            window.attributes("-topmost", True)
            window.attributes("-alpha", 0.9)
            window.configure(bg="black")
            label = tk.Label(
                window,
                bg="black",
                fg="white",
                padx=12,
                pady=8,
                font=("Segoe UI", 10, "bold"),
                text="REC",
            )
            label.pack()

            self._ui_ready.set()

            def place_window() -> None:
                window.update_idletasks()
                width = window.winfo_reqwidth()
                height = window.winfo_reqheight()
                screen_w = window.winfo_screenwidth()
                screen_h = window.winfo_screenheight()

                if self._position == "top-right":
                    x = max(0, screen_w - width - 24)
                    y = 24
                elif self._position == "top-left":
                    x = 24
                    y = 24
                elif self._position == "top-center":
                    x = max(0, (screen_w - width) // 2)
                    y = 24
                elif self._position in {"low-center", "bottom-center"}:
                    x = max(0, (screen_w - width) // 2)
                    y = max(0, screen_h - height - 48)
                else:
                    x = max(0, (screen_w - width) // 2)
                    y = max(0, (screen_h - height) // 2)

                window.geometry(f"+{x}+{y}")

            def apply_state(command: str) -> bool:
                if command == "shutdown":
                    try:
                        window.withdraw()
                        window.destroy()
                        root.quit()
                    except Exception:
                        pass
                    return False
                if command == "hide":
                    window.withdraw()
                    self._state = "hidden"
                    return True

                if command == "recording":
                    label.configure(text="REC", bg="#8B0000", fg="white")
                elif command == "loading":
                    label.configure(text="WAIT", bg="#1F3A5F", fg="white")
                elif command == "error":
                    label.configure(text="ERR", bg="#B22222", fg="white")
                else:
                    label.configure(text="...", bg="#4A4A4A", fg="white")
                place_window()
                window.deiconify()
                window.lift()
                window.attributes("-topmost", True)
                self._state = command
                return True

            def poll_queue() -> None:
                keep_running = True
                while keep_running:
                    try:
                        command = self._command_queue.get_nowait()
                    except Empty:
                        break
                    try:
                        keep_running = apply_state(command)
                    except Exception as exc:
                        logger.warning("[overlay] state transition failed: %s", exc)
                        keep_running = False
                if keep_running and not self._closed.is_set():
                    root.after(50, poll_queue)
                elif keep_running:
                    apply_state("shutdown")

            root.after(50, poll_queue)
            root.mainloop()
        except Exception as exc:
            logger.warning("[overlay] ui thread failed: %s", exc)
            self._enabled = False
            self._ui_ready.set()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


# ==============================================================================
# END OF FILE
# ==============================================================================
