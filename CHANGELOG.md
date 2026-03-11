<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Project policy: update this changelog only on explicit user request.

## 2.2.1 - 2026-03-02

### Fixed
- Resolved `AttributeError: 'NoneType' object has no attribute 'write'` crash in portable Windows distribution. The application now correctly redirects `sys.stdout` and `sys.stderr` to a NullWriter when running in windowed (`--noconsole`) mode.

---


### Added
- Optional clipboard restoration feature (`restore_clipboard`) to preserve user clipboard content after pasting transcribed text.
- New `vad_threshold_multiplier` configuration to tune the sensitivity of the adaptive noise floor for silence trimming.
- Red "ERR" state and visual feedback in `CaptureOverlay` for improved error signaling.
- New `Testing` section in `AGENTS.md` documenting test workflows (`pytest`).
- Automated syntax verification for all test files using `py_compile`.

### Changed
- **Project-wide Documentation Refactor**: Standardized all 25 Python files with DDP Engineering legal headers and Randstad-style Doxygen patterns.
- **Shebang & Encoding**: Added standardized `#!/usr/bin/env python3` and `# -*- coding: utf-8 -*-` headers to all source and test files.
- **Core Engine Hardening**: Implemented thread-safe recording in `audio.py` and converted `VoiceToTextApp` to a queue-based processing model for better stability.
- Section delimiters standardized to 80-character width across the entire codebase.

### Fixed
- Resolved `IndentationError` in `settings_ui.py` at line 279.
- Fixed a docstring SyntaxError in `test_settings_ui.py`.
- Improved error reporting from transcription worker to the UI overlay.

### Removed

---

## 2.1.0 - 2026-02-21

### Added

### Changed

### Fixed
- Prevented tray settings worker from restarting the service during application shutdown by adding explicit shutdown guards.
- Hardened overlay teardown to wait for the UI thread to terminate, reducing Tkinter shutdown-time thread exceptions.
- Corrected `settings_cli` fallback behavior to use safe defaults when config loading fails instead of retrying the same failing load path.
- Added regression tests for tray shutdown guards, overlay close lifecycle, and settings CLI fallback behavior.

### Removed

---

## 2.0.0 - 2026-02-21

### Added
- Recording mode support: `hold` and `toggle`.
- Capture overlay support for recording/processing states.
- Lightweight VAD-style silence trimming with configurable thresholds.
- New tests for VAD behavior, toggle-mode control flow, and extended config/model handling.

### Changed
- Whisper model handling now validates configured model names and falls back to `base` for invalid values.
- App and repository documentation updated for new recording mode, overlay, and VAD options.
- `AGENTS.md` updated with explicit Whisper-only backend scope guidance.

### Fixed
- Reduced stop/output race window by synchronizing stop-generation updates with paste output flow.
- Removed plaintext transcript content from runtime logs; logging now records language and output length only.
- Improved `VoiceToText.spec` portability by using repository-relative paths and conditional bundle inclusion.

### Removed

---

## 1.1.1 - 2026-02-21

### Added

### Changed
- Updated `VoiceToText.spec` to use repository-relative paths and conditional bundle inclusion for improved portability across machines/CI.
- Updated root `README.md` configuration path section to match current runtime defaults.
- Updated `AGENTS.md` ffmpeg guidance to reflect current microphone WAV flow behavior.

### Fixed
- Reduced stop/output race window by synchronizing stop-generation updates with paste output flow.
- Removed plaintext transcript content from runtime logs; logging now records language and output length only.

### Removed

---

## 1.1.0 - 2026-02-21

### Added

### Changed

### Fixed
- Resolved tray settings window responsiveness/blocking issue when launched from `voice-to-text --tray`.
- Refined tray lifecycle behavior after settings updates with retained runtime reload flow.

### Removed

---

## 1.0.0 - 2026-02-21

### Added
- Tray `Settings...` popup for runtime configuration updates.
- Hotkey capture control in settings UI.
- Configurable recording safety limit (`max_record_seconds`, default `120`).
- Additional tests for settings helpers and updated configuration defaults.

### Changed
- New default profile:
  - `model_size: base`
  - `source_language: en`
  - `target_language: en`
  - `push_to_talk_key: ctrl_r`
- Unified default app data namespace to `DDP_VoiceToText` for recordings/config/logs.
- Tray start/stop lifecycle hardened with improved thread-safety and responsiveness.

### Fixed
- Start/stop race protections for recording timeout and service restarts.
- Prevented stale in-flight output from being pasted after stop/restart cycles.
- Hardened numeric config parsing to avoid startup failures on malformed values.

### Removed

---

## 0.5.0 - 2026-02-20

### Added
- New unit tests for application behavior:
  - first-run wizard flows and hotkey validation/normalization
  - hotkey alias parsing in runtime
  - `Esc` handling policy for normal vs tray mode
- Extended test coverage with mocked runtime dependencies for fast deterministic app tests.

### Changed
- Config writing now uses structured YAML serialization instead of string replacement.
- `ffmpeg` is no longer required for normal microphone workflow; recorded WAV is loaded directly for transcription.
- Portable ZIP ignore rules updated to support versioned artifact names (`VoiceToText_Windows_Portable*.zip`).

### Fixed
- First-run config creation now tolerates filesystem/write failures without aborting startup.
- Removed non-portable VCS SSH editable dependency from `requirements.lock.txt`.
- Resolved tray-mode transcription terminal flash caused by `ffmpeg` subprocess invocation during normal WAV processing.
- Aligned logging backup defaults (`log_backup_count`) across template, dataclass defaults, and config-loader fallback.

### Removed

---

## 0.4.0 - 2026-02-20

### Added
- First-run configuration wizard for interactive terminal launches when config is missing.
- Wizard prompts for:
  - source language
  - target language
  - push-to-talk hotkey
  - beep enable/disable
- Hotkey alias support for common names:
  - `rctrl`/`rightctrl` -> `ctrl_r`
  - `lctrl`/`leftctrl` -> `ctrl_l`
  - `ralt`/`rightalt` -> `alt_r`
  - `lalt`/`leftalt` -> `alt_l`

### Changed
- Tray-mode startup behavior:
  - `Esc` no longer exits the process when running with `--tray`.
  - Exit control is handled from tray menu (`Stop`/`Exit`).
- Runtime messaging updated to show tray-specific exit instructions.
- App README updated with first-run wizard and tray-mode behavior details.

### Fixed
- First-run wizard input handling on Windows console now tolerates input-handle failures and falls back to defaults instead of crashing.
- Prevented startup failure caused by unsupported alias-style hotkey values (for example `rctrl`) created during first-run setup.

### Removed

---

## 0.3.0 - 2026-02-20

### Added
- Cross-platform system tray mode (`voice-to-text --tray`) for Windows and Ubuntu-style desktop sessions.
- New tray controller module: `5_Software/app/src/voice_to_text/tray.py`.
- Tray menu actions:
  - Start
  - Stop
  - Open Config
  - Exit
- Tray-mode dependencies in project metadata:
  - `pystray`
  - `Pillow`

### Changed
- App lifecycle refactored to support service control from tray:
  - Added explicit `start()`, `wait()`, and `stop()` flow in `VoiceToTextApp`.
- README updated with tray-mode usage and Linux desktop support note.

### Fixed

### Removed

---

## 0.2.0 - 2026-02-20

### Added
- Auto-generated OS-specific user config file with documented parameters when missing.
- OS-specific default recordings directory resolution for deployed app usage.
- `5_Software/app/scripts/README.md` with script usage and troubleshooting.
- Optional Argos language package installation support in setup scripts:
  - Windows: `-ArgosSourceLang` and `-ArgosTargetLang`
  - Linux: `--argos-src` and `--argos-dst`
- Optional recording feedback tones on start/stop with configurable beep parameters.
- Recording retention controls: `keep_recordings`, `max_recordings`, and `max_recordings_age_days`.
- Additional tests for config auto-create and OS-specific config path behavior.

### Changed
- Default source language behavior switched to English-first (`source_language: en`).
- Setup scripts were aligned to structured documentation/layout style used in MatrixRetroGames helper scripts.
- Windows setup script now auto-detects winget FFmpeg install location and updates session/user PATH when needed.
- Translation flow for non-English targets now prefers direct detected-language -> target Argos translation and falls back to en -> target.
- App and software documentation updated to reflect new config location and setup behavior.
- Recording cleanup policy now supports count-based priority cleanup followed by age-based cleanup when enabled.
- Non-Windows beep feedback now uses generated audio via `sounddevice` instead of terminal bell fallback.

### Fixed
- YAML generation bug for Windows paths in default config (`\` escape issue) by writing YAML-safe path values.
- Potential recorder resource leak on `Esc` exit while recording by stopping and discarding active stream cleanly.
- Config loading hardening: fallback to runtime defaults when default config file cannot be created due to filesystem restrictions.

### Removed

---

## 0.1.0 - 2026-02-20

### Added
- Initial `VoiceToText` repository structure and baseline project documentation.
- Licensing and governance files: `LICENSE.txt`, `LICENSE_NC.txt`, `AGENTS.md`, `.gitignore`, `.gitattributes`.
- Python MVP application under `5_Software/app`:
  - Push-to-talk recording flow.
  - Local Whisper speech-to-text integration.
  - Optional translation path (`target_language`) with Argos integration hook.
  - Active-window paste workflow.
- Packaging/project setup files: `pyproject.toml`, requirements profiles (`requirements-dev.txt`, `requirements-translate.txt`), and test suite scaffolding.
- Cross-platform setup automation scripts:
  - `5_Software/app/scripts/setup_windows.ps1`
  - `5_Software/app/scripts/setup_windows.bat`
  - `5_Software/app/scripts/setup_linux.sh`
- Doxygen-style documentation pattern applied to Python source and tests.

### Changed
- README files updated across repository and software folders with legal header and current setup/run workflows.

### Fixed
- Initial runtime dependency gap documented and automated setup updated to cover `ffmpeg` installation/check path.

### Removed

---
_Markdown_  
_Copyright 2026 DDP Engineering. All rights reserved._  
