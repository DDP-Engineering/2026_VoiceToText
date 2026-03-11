<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# VoiceToText App (MVP)

Offline push-to-talk desktop app using local Whisper.

## Features (MVP)

- Hold a hotkey to record microphone input
- Select recording mode: hold-to-talk or toggle-to-talk
- Convert speech to text locally (Whisper)
- Optional translation target selection
- Paste text into the currently active window (VS Code and others)
- Visual capture overlay for recording/processing/error states
- Queued transcription: multiple rapid recordings are processed sequentially
- Optional silence filtering (VAD-style trimming)

## Setup

```bash
cd 5_Software/app
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux:
# source .venv/bin/activate
pip install -e .
```

## Automated Setup (Recommended)

Windows (PowerShell):

```powershell
cd 5_Software/app
.\scripts\setup_windows.ps1
```

Windows (cmd, no execution policy issues):

```bat
cd 5_Software\app
scripts\setup_windows.bat
```

Linux:

```bash
cd 5_Software/app
chmod +x scripts/setup_linux.sh
./scripts/setup_linux.sh
```

Optional flags:

- Translation extras:
  - Windows: `.\scripts\setup_windows.ps1 -InstallTranslation`
  - Linux: `./scripts/setup_linux.sh --translate`
- Translation extras + Argos language package install:
  - Windows: `.\scripts\setup_windows.ps1 -InstallTranslation -ArgosSourceLang ro -ArgosTargetLang de`
  - Linux: `./scripts/setup_linux.sh --translate --argos-src=ro --argos-dst=de`
- Skip ffmpeg handling:
  - Windows: `.\scripts\setup_windows.ps1 -SkipFfmpeg`
  - Linux: `./scripts/setup_linux.sh --skip-ffmpeg`

### Windows PowerShell: activation policy issue

If you see `running scripts is disabled on this system`, use one option below.

Temporary (current shell only):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Persistent for current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Without changing execution policy:

```powershell
cmd /c .venv\Scripts\activate.bat
```

Optional offline translation (requires Argos packages installed locally):

```bash
pip install -e .[translate]
```

Argos language packages are only required when `target_language` is non-empty and not `en`.
You can install them using the setup scripts (examples above) or manually with Argos tooling.
`ffmpeg` is optional for normal VoiceToText microphone workflow (recorded WAV is handled directly).
Keep `ffmpeg` installed only if you plan to process additional external audio formats.

## Run

```bash
voice-to-text
```

Exit with `Esc`.

Tray mode (Windows/Ubuntu):

```bash
voice-to-text --tray
```

Tray menu actions:

- Start
- Stop
- Settings...
- Open Config
- Exit

In tray mode, `Esc` does not terminate the app process. Use tray `Stop` or `Exit`.
`Settings...` opens a popup configuration window; saving applies the new settings and reloads the background service.

Ubuntu note:

- Tray visibility depends on desktop environment support (GNOME may require AppIndicator extension/package).

## Windows Portable Build

Build a self-contained Windows package with bundled `ffmpeg` and pre-downloaded Whisper model:

```powershell
cd 5_Software/app
.\scripts\build_windows_portable.ps1
```

Optional model size:

```powershell
.\scripts\build_windows_portable.ps1 -ModelSize base
```

Build multiple model variants in one run:

```powershell
.\scripts\build_windows_portable.ps1 -ModelSizes tiny,base,small
```

Portable artifact:

- Single default build (`small`): `dist/VoiceToText_Windows_Portable_v<version>.zip`
- Non-default single model: `dist/VoiceToText_Windows_Portable_v<version>_<model>.zip`
- Multi-model build: one ZIP per model (same `<model>` suffix pattern)

## Config

Default config file path:

- Windows: `%APPDATA%\DDP_VoiceToText\config.yaml`
- Linux: `$XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml` (fallback `~/.config/DDP_VoiceToText/config.yaml`)

If the config file does not exist, the app creates it automatically on first run with documented parameters.
In interactive terminal mode, a small first-run wizard asks for:

- source language
- target language
- push-to-talk hotkey
- beep on/off

In tray mode (or non-interactive runs), defaults are written automatically without prompts.

Example:

```yaml
push_to_talk_key: ctrl_r
model_size: base
source_language: en
target_language: "en"
sample_rate: 16000
channels: 1
max_record_seconds: 120
record_mode: hold
enable_beep: true
beep_start_frequency_hz: 880
beep_start_duration_ms: 70
beep_stop_frequency_hz: 520
beep_stop_duration_ms: 90
overlay_enabled: true
overlay_position: center
vad_enabled: true
vad_silence_ms: 900
vad_min_speech_ms: 250
vad_threshold_multiplier: 3.0
vad_trim_leading: true
vad_trim_trailing: true
keep_recordings: false
max_recordings: 0
max_recordings_age_days: 0
restore_clipboard: false
enable_file_logging: true
log_level: INFO
log_rotation_when: midnight
log_rotation_interval: 1
log_backup_count: 7
logs_dir: "C:/Users/<user>/AppData/Roaming/DDP_VoiceToText/logs"
recordings_dir: "C:/Users/<user>/AppData/Local/DDP_VoiceToText/recordings"
```

Notes:

- `target_language: ""` keeps source language output.
- `target_language: en` uses Whisper translation to English.
- Other target languages require local Argos Translate language packages.
- Default recordings location is OS-specific user data folder; you can override via `recordings_dir`.
- Default profile is:
  - `source_language: en`
  - `target_language: en`
  - `model_size: base`
  - `push_to_talk_key: ctrl_r`
- Beep feedback can be toggled with `enable_beep`.
- `record_mode` supports:
  - `hold`: press+hold to record, release to process
  - `toggle`: press once to start, press again to stop/process
- Overlay can be enabled and positioned via `overlay_enabled` and `overlay_position`.
- `vad_enabled` enables silence trimming before transcription.
- `vad_silence_ms` and `vad_min_speech_ms` tune silence/speech filtering thresholds.
- `vad_threshold_multiplier` adjusts the sensitivity of the adaptive noise floor (default `3.0`).
- `restore_clipboard`: if `true`, the application attempts to restore your previous clipboard content after pasting the transcribed text.
- `max_record_seconds` enforces a safety cap for a single hold-to-talk recording (`120` by default, `0` disables the limit).
- `keep_recordings: false` deletes captured audio files after processing (recommended default).
- `max_recordings` (when `> 0`) keeps only the newest N recordings.
- `max_recordings_age_days` (when `> 0`) deletes recordings older than N days.
- Cleanup priority is: `max_recordings` first, then `max_recordings_age_days`.
- Logs are written to terminal and rotating date-based files in `logs_dir` (default daily rotation).
