<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# VoiceToText

Offline desktop voice-to-text project focused on fast dictation workflows.

## What It Does

- Push-to-talk audio capture
- Hold or toggle recording modes
- Local Whisper speech-to-text (offline)
- Optional translation target selection
- Paste/insert output into the active window (VS Code and other applications)
- Optional clipboard restoration to preserve original content after pasting
- Capture overlay indicator with "REC"/"PROC"/"ERR" states and advanced silence filtering (VAD)
- Planned deployable outputs for Windows and Linux

## Project Status

Initial MVP is available under `5_Software/app`.

Current implemented flow:

1. Hold configured hotkey to record.
2. Release hotkey to transcribe.
3. Paste text into the active window.

## Repository Structure

- `0_Planning/`: planning and requirements
- `1_Documentation/`: architecture and templates
- `2_Tools/`: supporting tools/utilities
- `3_Hardware/`: hardware-related sources (if needed)
- `4_HardwareDocu/`: hardware documentation outputs
- `5_Software/`: source code and software assets
- `6_SoftwareDocu/`: software documentation
- `7_Delivery/`: delivery/release artifacts
- `9_Others/`: miscellaneous

## Software MVP Location

- App root: `5_Software/app`
- Entry point: `voice-to-text` (installed via `pyproject.toml`)

## Quick Start

```bash
cd 5_Software/app
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux:
# source .venv/bin/activate
pip install -e .
voice-to-text
```

Optional translation support:

```bash
pip install -e .[translate]
```

## Configuration

Default config file:

- Windows: `%APPDATA%\DDP_VoiceToText\config.yaml`
- Linux: `$XDG_CONFIG_HOME/DDP_VoiceToText/config.yaml` (fallback `~/.config/DDP_VoiceToText/config.yaml`)

Example:

```yaml
push_to_talk_key: f9
model_size: small
source_language: auto
target_language: ""
sample_rate: 16000
channels: 1
recordings_dir: recordings
vad_threshold_multiplier: 3.0
restore_clipboard: false
```

## Licensing

This project is licensed under AGPL-3.0 with additional non-commercial restriction.

See:

- `LICENSE.txt`
- `LICENSE_NC.txt`
