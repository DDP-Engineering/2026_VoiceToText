#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_overlay.py
@brief      Unit tests for overlay lifecycle behavior.
@details    Verifies close() requests shutdown and waits for UI thread.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from queue import Queue
from threading import Event, current_thread

from voice_to_text.overlay import CaptureOverlay


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================
class _DummyThread:
    def __init__(self) -> None:
        self.ident = 987654
        self.join_called = False
        self.timeout = None

    def is_alive(self) -> bool:
        return True

    def join(self, timeout: float | None = None) -> None:
        self.join_called = True
        self.timeout = timeout


def test_close_joins_overlay_thread() -> None:
    """
    @brief      Verify overlay close waits for background UI thread.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    overlay = CaptureOverlay.__new__(CaptureOverlay)
    overlay._closed = Event()
    overlay._ui_ready = Event()
    overlay._command_queue = Queue()
    overlay._thread = _DummyThread()
    overlay._enabled = True

    overlay.close()

    assert overlay._closed.is_set() is True
    assert overlay._command_queue.get_nowait() == "shutdown"
    assert overlay._thread.join_called is True
    assert overlay._thread.timeout == 1.0


def test_close_does_not_join_current_thread() -> None:
    """
    @brief      Verify close avoids self-join when called on UI thread.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    overlay = CaptureOverlay.__new__(CaptureOverlay)
    overlay._closed = Event()
    overlay._ui_ready = Event()
    overlay._command_queue = Queue()
    overlay._enabled = True
    thread = _DummyThread()
    thread.ident = current_thread().ident
    overlay._thread = thread

    overlay.close()

    assert thread.join_called is False


def test_show_error_enqueues_command() -> None:
    """
    @brief      Verify show_error puts 'error' in command queue.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    overlay = CaptureOverlay.__new__(CaptureOverlay)
    overlay._command_queue = Queue()
    overlay._ui_ready = Event()
    overlay._closed = Event()
    overlay._enabled = True
    overlay.show_error()
    assert overlay._command_queue.get_nowait() == "error"
# ==============================================================================
# END OF FILE
# ==============================================================================
