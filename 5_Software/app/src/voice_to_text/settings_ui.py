#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       settings_ui.py
@brief      Popup settings UI for VoiceToText.
@details    Provides a small Tkinter window for editing key runtime settings,
            including hotkey capture and input validation.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from dataclasses import asdict
import tkinter as tk
from tkinter import messagebox, ttk

from pynput.keyboard import Key

from .config import AppConfig


# ==============================================================================
# CONSTANTS
# ==============================================================================

_ALLOWED_MODEL_SIZES = ("tiny", "base", "small", "medium", "large")
_ALLOWED_RECORD_MODES = ("hold", "toggle")
_ALLOWED_OVERLAY_POSITIONS = ("center", "top-center", "low-center", "top-right", "top-left", "bottom-center")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def open_settings_window(current_config: AppConfig) -> AppConfig | None:
    """
    @brief      Show settings popup and return updated config when saved.
    @param[in]  current_config    Current application config.
    @return     Updated AppConfig on Save, or None on Cancel/Close.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    root = tk.Tk()
    root.title("VoiceToText Settings")
    root.resizable(False, False)

    result: dict[str, AppConfig | None] = {"config": None}

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    source_language_var = tk.StringVar(value=current_config.source_language)
    target_language_var = tk.StringVar(value=current_config.target_language)
    model_size_var = tk.StringVar(value=current_config.model_size)
    record_mode_var = tk.StringVar(value=current_config.record_mode)
    hotkey_var = tk.StringVar(value=current_config.push_to_talk_key)
    max_record_seconds_var = tk.StringVar(value=str(current_config.max_record_seconds))
    enable_beep_var = tk.BooleanVar(value=current_config.enable_beep)
    overlay_enabled_var = tk.BooleanVar(value=current_config.overlay_enabled)
    overlay_position_var = tk.StringVar(value=current_config.overlay_position)
    overlay_position_changed = {"value": False}
    vad_enabled_var = tk.BooleanVar(value=current_config.vad_enabled)
    vad_silence_ms_var = tk.StringVar(value=str(current_config.vad_silence_ms))
    vad_min_speech_ms_var = tk.StringVar(value=str(current_config.vad_min_speech_ms))

    ttk.Label(frame, text="Source language").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=source_language_var, width=22).grid(row=0, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Target language").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=target_language_var, width=22).grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Model size").grid(row=2, column=0, sticky="w", pady=4)
    model_combo = ttk.Combobox(frame, textvariable=model_size_var, values=_ALLOWED_MODEL_SIZES, state="readonly", width=20)
    model_combo.grid(row=2, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Record mode").grid(row=3, column=0, sticky="w", pady=4)
    mode_combo = ttk.Combobox(frame, textvariable=record_mode_var, values=_ALLOWED_RECORD_MODES, state="readonly", width=20)
    mode_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Push-to-talk hotkey").grid(row=4, column=0, sticky="w", pady=4)
    hotkey_entry = ttk.Entry(frame, textvariable=hotkey_var, state="readonly", width=22)
    hotkey_entry.grid(row=4, column=1, sticky="ew", pady=4)
    ttk.Button(frame, text="Capture", command=lambda: _capture_hotkey(root, hotkey_var)).grid(row=4, column=2, padx=(8, 0), pady=4)

    ttk.Label(frame, text="Max record seconds").grid(row=5, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=max_record_seconds_var, width=22).grid(row=5, column=1, sticky="ew", pady=4)
    ttk.Label(frame, text="(0 = no limit)").grid(row=5, column=2, sticky="w", padx=(8, 0), pady=4)

    ttk.Checkbutton(frame, text="Enable beep feedback", variable=enable_beep_var).grid(
        row=6, column=0, columnspan=3, sticky="w", pady=6
    )

    ttk.Checkbutton(frame, text="Enable capture overlay", variable=overlay_enabled_var).grid(
        row=7, column=0, columnspan=3, sticky="w", pady=6
    )

    ttk.Label(frame, text="Overlay position").grid(row=8, column=0, sticky="w", pady=4)
    overlay_combo = ttk.Combobox(
        frame,
        textvariable=overlay_position_var,
        values=_ALLOWED_OVERLAY_POSITIONS,
        state="readonly",
        width=20,
    )
    overlay_combo.grid(row=8, column=1, sticky="ew", pady=4)
    overlay_combo.bind("<<ComboboxSelected>>", lambda _event: overlay_position_changed.__setitem__("value", True))

    ttk.Checkbutton(frame, text="Enable silence filtering (VAD)", variable=vad_enabled_var).grid(
        row=9, column=0, columnspan=3, sticky="w", pady=6
    )

    ttk.Label(frame, text="VAD silence ms").grid(row=10, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=vad_silence_ms_var, width=22).grid(row=10, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="VAD min speech ms").grid(row=11, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=vad_min_speech_ms_var, width=22).grid(row=11, column=1, sticky="ew", pady=4)

    button_row = ttk.Frame(frame)
    button_row.grid(row=12, column=0, columnspan=3, sticky="e", pady=(10, 0))

    def on_save() -> None:
        source_language = source_language_var.get().strip().lower() or "en"
        target_language = target_language_var.get().strip().lower()
        model_size = model_size_var.get().strip().lower()
        record_mode = record_mode_var.get().strip().lower()
        hotkey = hotkey_var.get().strip().lower()
        max_record_seconds = _parse_non_negative_int(max_record_seconds_var.get())
        vad_silence_ms = _parse_non_negative_int(vad_silence_ms_var.get())
        vad_min_speech_ms = _parse_non_negative_int(vad_min_speech_ms_var.get())
        overlay_position = overlay_position_var.get().strip().lower()

        if model_size not in _ALLOWED_MODEL_SIZES:
            messagebox.showerror("Invalid value", "Model size must be one of: tiny, base, small, medium, large")
            return

        if record_mode not in _ALLOWED_RECORD_MODES:
            messagebox.showerror("Invalid value", "Record mode must be hold or toggle.")
            return

        if not _is_supported_hotkey(hotkey):
            messagebox.showerror("Invalid value", "Hotkey is not supported. Use Capture or a valid key token.")
            return

        if max_record_seconds is None:
            messagebox.showerror("Invalid value", "Max record seconds must be an integer >= 0.")
            return

        if vad_silence_ms is None or vad_min_speech_ms is None:
            messagebox.showerror("Invalid value", "VAD values must be integers >= 0.")
            return

        if overlay_position_changed["value"] and overlay_position not in _ALLOWED_OVERLAY_POSITIONS:
            messagebox.showerror(
                "Invalid value",
                "Overlay position must be one of: center, top-center, low-center, bottom-center, top-right, top-left.",
            )
            return
        if not overlay_position_changed["value"]:
            overlay_position = current_config.overlay_position

        config_map = asdict(current_config)
        config_map.update(
            {
                "source_language": source_language,
                "target_language": target_language,
                "model_size": model_size,
                "record_mode": record_mode,
                "push_to_talk_key": hotkey,
                "max_record_seconds": max_record_seconds,
                "enable_beep": bool(enable_beep_var.get()),
                "overlay_enabled": bool(overlay_enabled_var.get()),
                "overlay_position": overlay_position,
                "vad_enabled": bool(vad_enabled_var.get()),
                "vad_silence_ms": vad_silence_ms,
                "vad_min_speech_ms": vad_min_speech_ms,
            }
        )
        result["config"] = AppConfig(**config_map)
        root.destroy()

    def on_cancel() -> None:
        result["config"] = None
        root.destroy()

    ttk.Button(button_row, text="Save", command=on_save).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(button_row, text="Cancel", command=on_cancel).grid(row=0, column=1)

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()
    return result["config"]


def _is_supported_hotkey(hotkey_name: str) -> bool:
    """
    @brief      Validate hotkey token against supported parser logic.
    @param[in]  hotkey_name    Hotkey token to validate.
    @return     True when token is supported.
    """
    if not hotkey_name:
        return False
    if len(hotkey_name) == 1:
        return True
    return hasattr(Key, hotkey_name)


def _parse_non_negative_int(value: str) -> int | None:
    """
    @brief      Parse a non-negative integer from string input.
    @param[in]  value    Raw input string.
    @return     Parsed int value, or None when invalid.
    """
    try:
        parsed = int(value.strip())
    except (TypeError, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


def _capture_hotkey(root: tk.Tk, hotkey_var: tk.StringVar) -> None:
    """
    @brief      Capture next key press and set hotkey variable.
    @param[in]  root          Parent root window.
    @param[in]  hotkey_var    Target hotkey variable to update.
    @return     None
    """
    capture_window = tk.Toplevel(root)
    capture_window.title("Capture Hotkey")
    capture_window.resizable(False, False)
    capture_window.grab_set()

    ttk.Label(
        capture_window,
        text="Press one key now (Esc cancels).",
        padding=12,
    ).grid(row=0, column=0)

    def on_key_press(event: tk.Event) -> None:
        key_name = _tk_keysym_to_hotkey(event.keysym)
        if key_name == "esc":
            capture_window.destroy()
            return
        if key_name:
            hotkey_var.set(key_name)
            capture_window.destroy()

    capture_window.bind("<KeyPress>", on_key_press)
    capture_window.focus_force()


def _tk_keysym_to_hotkey(keysym: str) -> str:
    """
    @brief      Convert tkinter keysym token to VoiceToText hotkey token.
    @param[in]  keysym    Tkinter keysym value.
    @return     Normalized hotkey token.
    """
    if not keysym:
        return ""

    mapping = {
        "Control_L": "ctrl_l",
        "Control_R": "ctrl_r",
        "Alt_L": "alt_l",
        "Alt_R": "alt_r",
        "Shift_L": "shift_l",
        "Shift_R": "shift_r",
        "Escape": "esc",
        "Return": "enter",
        "space": "space",
        "Tab": "tab",
        "BackSpace": "backspace",
    }
    if keysym in mapping:
        return mapping[keysym]

    lowered = keysym.lower()
    if lowered.startswith("f") and lowered[1:].isdigit():
        return lowered
    if len(lowered) == 1:
        return lowered

    return lowered


# ==============================================================================
# END OF FILE
# ==============================================================================
