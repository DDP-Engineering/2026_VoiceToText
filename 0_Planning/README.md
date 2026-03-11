<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# 0_Planning

Basic documentation for 0_Planning in the VoiceToText project.

Yes, popup config UI is feasible and would be a strong next feature.

Missing/high-value functions I’d prioritize:

Config GUI (popup settings window)
Edit hotkey, source/target language, model size, beep, tray behavior, logging.
Buttons: Save, Cancel, Reset defaults.
Tray menu entry: Settings....
Hotkey capture widget
“Press a key now” instead of typing text (rctrl, f9, etc.).
Validates automatically.
Runtime apply/reload
After saving settings, optionally restart listener without full app restart.
Device selection
Select input microphone from available devices.
Test button for mic level/beep.
Logs viewer
Tray action “Open latest log” + quick diagnostics panel.
Update safety checks
On config save: schema validation + clear error popup.
About your popup question:

Yes, we can do it.
Best lightweight cross-platform choice: tkinter (already in standard Python installs on Windows; usually available on Ubuntu with python3-tk).
Integration plan:
Add settings_ui.py (Tk window)
Add tray menu item Settings
On save: write config and optionally restart app service
Keep CLI/tray fallback if GUI unavailable
If you want, I can implement an MVP popup now with these fields:

source_language, target_language, push_to_talk_key, model_size, enable_beep.

