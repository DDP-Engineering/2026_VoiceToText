#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       paste.py
@brief      Clipboard paste integration for active desktop window.
@details    Copies text to clipboard and triggers platform paste shortcut.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import platform

import pyperclip
from pynput.keyboard import Controller, Key


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class TextPaster:
    """
    @brief      Active-window text paste helper.
    @details    Uses clipboard plus keyboard shortcut to insert text in the
                currently focused application.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    1.0.0
    """
    def __init__(self) -> None:
        """
        @brief      Initialize keyboard controller.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._keyboard = Controller()

    def paste(self, text: str, restore_clipboard: bool = False) -> None:
        """
        @brief      Paste text into focused window.
        @param[in]  text                Text to copy and paste.
        @param[in]  restore_clipboard   When true, original clipboard is restored.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        import time
        if not text:
            return

        original_content = None
        if restore_clipboard:
            try:
                original_content = pyperclip.paste()
            except Exception:
                pass

        pyperclip.copy(text)

        is_mac = platform.system().lower() == "darwin"
        modifier = Key.cmd if is_mac else Key.ctrl

        with self._keyboard.pressed(modifier):
            self._keyboard.press("v")
            self._keyboard.release("v")

        if restore_clipboard and original_content is not None:
            # Short delay because some apps are slow at reading from clipboard
            # after the paste command is triggered via OS events.
            time.sleep(0.3)
            try:
                pyperclip.copy(original_content)
            except Exception:
                pass


# ==============================================================================
# END OF FILE
# ==============================================================================
