<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# VoiceToText

VoiceToText is an offline desktop speech workflow project focused on fast dictation, local transcription, optional local translation, and direct text insertion into the active application.

## Overview

The current software implementation is under [5_Software/app](5_Software/app). It provides a complete local workflow built around Whisper-based speech-to-text:

- push-to-talk microphone capture
- `hold` and `toggle` recording modes
- local Whisper transcription
- optional translation to English through Whisper
- optional offline translation to other languages through locally installed Argos Translate packages
- paste/insert into the currently active window
- optional clipboard restore after paste
- recording/processing/error overlay
- silence trimming and speech filtering
- system tray mode with start, stop, settings, config, and logs actions
- Windows portable packaging flow with bundled `ffmpeg` and pre-downloaded Whisper models

## Project Status

The app is no longer just a repository skeleton. The repo contains:

- Python application source
- setup scripts for Windows and Linux
- first-run configuration flow
- popup settings UI
- automated tests with `pytest`
- Windows portable build script
- delivery area for release artifacts

## Repository Structure

- `0_Planning/`: planning and requirements
- `1_Documentation/`: templates and generic architecture material
- `2_Tools/`: supporting repository utilities
- `3_Hardware/`: hardware-related sources
- `4_HardwareDocu/`: hardware documentation outputs
- `5_Software/`: software source, scripts, packaging assets
- `6_SoftwareDocu/`: software documentation
- `7_Delivery/`: release and delivery artifacts
- `9_Others/`: miscellaneous assets

## Main Software Location

- App root: [5_Software/app](5_Software/app)
- Python package: [5_Software/app/src/voice_to_text](5_Software/app/src/voice_to_text)
- Entry point: `voice-to-text`
- Current package version: `2.2.1`

## Feature Summary

- Offline speech-to-text using local Whisper
- Offline-friendly workflow with no cloud dependency required for the core app
- Optional translation workflow
  - `target_language: en` uses Whisper translation
  - other target languages use local Argos packages
- Global hotkey capture for dictation
- Active-window paste automation
- Recording queue for rapid consecutive captures
- Configurable beeps, overlay, VAD, logging, and recording retention
- Tray-based background runtime on supported desktop environments

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

Recommended automated setup:

Windows PowerShell:

```powershell
cd 5_Software/app
.\scripts\setup_windows.ps1
```

Windows `cmd`:

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

Optional translation extras:

```bash
pip install -e .[translate]
```

`ffmpeg` is recommended when processing external audio formats. Standard microphone workflow records WAV directly and can run without `ffmpeg`.

## Run

Standard mode:

```bash
cd 5_Software/app
voice-to-text
```

Tray mode:

```bash
cd 5_Software/app
voice-to-text --tray
```

In standard mode, the default workflow is:

1. Press or hold the configured hotkey.
2. Speak.
3. Release the hotkey or stop the toggle recording.
4. Let Whisper process the recording.
5. Paste the result into the active target window.

## Configuration

Default config file:

- Windows: `%APPDATA%\DDP_VoiceToText\config.yaml`
- Linux: `$XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml` (fallback `~/.config/DDP_VoiceToText/config.yaml`)

On first run, the app creates the config automatically. In interactive terminal mode it can also guide the user through a short first-run setup.

Example:

```yaml
push_to_talk_key: ctrl_r
record_mode: hold
model_size: base
source_language: en
target_language: "en"
sample_rate: 16000
channels: 1
max_record_seconds: 120
enable_beep: true
overlay_enabled: true
overlay_position: center
vad_enabled: true
vad_silence_ms: 900
vad_min_speech_ms: 250
vad_threshold_multiplier: 3.0
restore_clipboard: false
enable_file_logging: true
recordings_dir: recordings
```

## Testing

The software test suite is under [5_Software/app/tests](5_Software/app/tests) and currently covers:

- application runtime behavior
- configuration loading
- first-run flow
- overlay logic
- paste logic
- settings launcher and settings UI helpers
- STT option handling
- tray lifecycle guards
- VAD helpers

Run tests from [5_Software/app](5_Software/app):

```bash
python -m pytest
```

## Packaging

Windows portable packaging is supported through:

- [5_Software/app/scripts/build_windows_portable.ps1](5_Software/app/scripts/build_windows_portable.ps1)

The portable build bundles:

- the app executable
- runtime dependencies
- `ffmpeg.exe` and `ffprobe.exe`
- a pre-downloaded Whisper model

Example:

```powershell
cd 5_Software/app
.\scripts\build_windows_portable.ps1 -ModelSize small
```

## Licensing

This project is licensed under AGPL-3.0 with additional non-commercial restriction.

See:

- `LICENSE.txt`
- `LICENSE_NC.txt`
