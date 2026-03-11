#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_paste.py
@brief      Unit tests for clipboard paste logic.
@details    Verifies basic pasting and optional clipboard restoration.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-03-02
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from voice_to_text.paste import TextPaster


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
@pytest.fixture
def mock_pyperclip():
    with patch("voice_to_text.paste.pyperclip") as mock:
        yield mock


@pytest.fixture
def mock_controller():
    with patch("voice_to_text.paste.Controller") as mock:
        yield mock


def test_paste_basic(mock_pyperclip, mock_controller) -> None:
    """
    @brief      Verify basic paste logic triggers clipboard copy and key events.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    paster = TextPaster()
    paster.paste("hello world")

    mock_pyperclip.copy.assert_called_once_with("hello world")
    # Verify keyboard controller was used
    assert mock_controller.return_value.pressed.called


def test_paste_restore_clipboard(mock_pyperclip, mock_controller) -> None:
    """
    @brief      Verify clipboard is restored when restore_clipboard is True.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    mock_pyperclip.paste.return_value = "original"
    
    paster = TextPaster()
    # Mock sleep to avoid slow tests
    with patch("time.sleep"):
        paster.paste("new content", restore_clipboard=True)

    # Check sequence: paste() (to get backup) -> copy(new) -> copy(original)
    mock_pyperclip.paste.assert_called_once()
    assert mock_pyperclip.copy.call_count == 2
    mock_pyperclip.copy.assert_any_call("new content")
    mock_pyperclip.copy.assert_any_call("original")


def test_paste_no_restore_by_default(mock_pyperclip, mock_controller) -> None:
    """
    @brief      Verify clipboard is NOT restored by default.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    mock_pyperclip.paste.return_value = "original"
    
    paster = TextPaster()
    paster.paste("new content")

    assert mock_pyperclip.paste.called is False
    mock_pyperclip.copy.assert_called_once_with("new content")
# ==============================================================================
# END OF FILE
# ==============================================================================
