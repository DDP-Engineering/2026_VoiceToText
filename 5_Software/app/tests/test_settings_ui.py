#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_settings_ui.py
@brief      Unit tests for settings UI helpers.
@details    Verifies key token mapping and hotkey validation logic.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from voice_to_text.settings_ui import _is_supported_hotkey, _parse_non_negative_int, _tk_keysym_to_hotkey


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_tk_keysym_to_hotkey_common_keys() -> None:
    """
    @brief      Verify tkinter keysym conversion for common special keys.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert _tk_keysym_to_hotkey("Control_R") == "ctrl_r"
    assert _tk_keysym_to_hotkey("Alt_L") == "alt_l"
    assert _tk_keysym_to_hotkey("Escape") == "esc"
    assert _tk_keysym_to_hotkey("F9") == "f9"
    assert _tk_keysym_to_hotkey("a") == "a"


def test_is_supported_hotkey_validation() -> None:
    """
    @brief      Verify supported and unsupported hotkey token validation.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert _is_supported_hotkey("a") is True
    assert _is_supported_hotkey("f9") is True
    assert _is_supported_hotkey("ctrl_r") is True
    assert _is_supported_hotkey("invalid_hotkey_name") is False


def test_parse_non_negative_int() -> None:
    """
    @brief      Verify parser for non-negative integer inputs.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert _parse_non_negative_int("120") == 120
    assert _parse_non_negative_int("0") == 0
    assert _parse_non_negative_int("-1") is None
    assert _parse_non_negative_int("abc") is None
# ==============================================================================
# END OF FILE
# ==============================================================================
