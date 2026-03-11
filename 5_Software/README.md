<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# 5_Software

Software workspace for the VoiceToText project.

## Scope

- Python offline speech workflow application
- Local Whisper speech-to-text pipeline
- Optional local translation path
- Desktop paste integration with visual status overlay (REC/WAIT/ERR)
- Robust multi-threaded workflow with queued background processing

## Current Implementation

- Main app location: `5_Software/app`
- Source package: `5_Software/app/src/voice_to_text`
- Tests: `5_Software/app/tests`

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

## Testing

```bash
cd 5_Software/app
pytest
```

## Notes

- The app is designed to run offline.
- Packaging targets are planned for Windows executable and Linux distribution formats.
- For Windows virtual environment activation troubleshooting (PowerShell execution policy), see `5_Software/app/README.md`.

