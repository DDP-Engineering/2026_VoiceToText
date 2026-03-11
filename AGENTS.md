# AGENTS.md

Project-level instructions for AI coding agents working in this repository.

## Project Overview

`VoiceToText` is an offline desktop speech workflow tool with push-to-talk capture, local Whisper-based speech-to-text, language translation selection, and text insertion into the active target window (including VS Code and other editors/apps).

## Architecture & Tech Stack

- Platform: Windows and Linux desktop
- Runtime: Python 3.x
- STT Engine: Local Whisper framework (offline, no cloud dependency)
- Core Features: Push-to-talk, selectable translation language, speech-to-text, paste/insert into selected active window
- Packaging Targets: Windows executable and Linux package/distribution artifacts
- License: AGPL-3.0 with additional non-commercial restriction (`LICENSE.txt`, `LICENSE_NC.txt`)

## Repository Layout

- `0_Planning/`: planning and requirements
- `1_Documentation/`: architecture and generic guides
- `2_Tools/`: external tools/utilities
- `3_Hardware/`: hardware design sources (schematic/PCB)
- `4_HardwareDocu/`: hardware output docs (datasheets, notes, production docs)
- `5_Software/`: software source, projects, scripts, SDK
- `6_SoftwareDocu/`: software documentation
- `7_Delivery/`: release artifacts
- `9_Others/`: miscellaneous
- `.agent/workflows/`: agent workflows

## Key Constraints

- Keep implementation efficient and maintainable
- Must run offline for speech recognition and translation workflow
- Keep STT backend scope Whisper-only (do not introduce Parakeet or cloud backends unless explicitly requested)
- Follow repository code style and templates
- Do not introduce license-incompatible content
- Include the project legal header in repository documentation and source code files.

## Build and Run Workflows

- Preferred setup (Windows PowerShell): `5_Software/app/scripts/setup_windows.ps1`
- Preferred setup (Windows cmd): `5_Software/app/scripts/setup_windows.bat`
- Preferred setup (Linux): `5_Software/app/scripts/setup_linux.sh`
- Optional translation extras:
  - Windows: `5_Software/app/scripts/setup_windows.ps1 -InstallTranslation`
  - Linux: `5_Software/app/scripts/setup_linux.sh --translate`
- Runtime launch:
  - With activated venv: `voice-to-text`
  - Without activation: `.venv/Scripts/python.exe -m voice_to_text.main` (Windows) or `.venv/bin/python -m voice_to_text.main` (Linux)
- External runtime dependency: `ffmpeg` is recommended when processing external audio formats. Standard microphone workflow uses recorded WAV directly and can run without `ffmpeg`.

## Testing

- **Framework**: `pytest`
- **How to run**: 
  - Ensure you are in the `5_Software/app` directory.
  - Run `python -m pytest` (recommended for path resolution) or simply `pytest` if the environment is set up.
- **When to run**:
  - **Before PR/Delivery**: Always verify functionality before finalizing any task.
  - **After Refactoring**: Confirm that the logic remains intact (e.g., after standardizing documentation).
  - **When Adding Logic**: Ensure new modules or functions have corresponding tests in the `tests/` directory.
- **Environment**: Use the same virtual environment as the runtime.

## Script Documentation and Layout

- For setup/build helper scripts, follow the same documentation/layout approach used in `2026_MatrixRetroGames/5_Software/scripts/build_dev.bat`:
  - legal header block at top
  - short purpose and usage section
  - explicit sectioned flow (path resolution, validation, execution steps)
  - clear status banners and error messages
- Keep cross-platform setup scripts under `5_Software/app/scripts/`.

## Documentation Style

When editing Python files, follow the Randstad Digital Romania style:

- Shebang and encoding (top of file):
  ```python
  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-
  ```
- Legal Header:
  ```python
  # Copyright (c) 2026 DDP Engineering
  # This software is licensed under the GNU Affero General Public License v3.0
  # (AGPL-3.0) with additional Non-Commercial restriction.
  # See the LICENSE and LICENSE_NC.txt files for full license details.
  ```
- Module Header (Doxygen):
  ```python
  """
  @file       filename.py
  @brief      Summary.
  @details    Detailed description.

  @author     Dan Dumitru Pasare + AI Assistant
  @date       YYYY-MM-DD
  @version    1.0.0
  """
  ```
- Section Delimiters (80 chars total, specific headers):
  ```python
  # ==============================================================================
  # SECTION NAME
  # ==============================================================================
  ```
  Standard sections: `IMPORTS`, `CONSTANTS`, `CLASS DEFINITION`, `HELPER FUNCTIONS`, `END OF FILE`.

- Method/class docstrings:
  - Use explicit Doxygen tags.
  - Every function/method must include `@author`, `@date`, and `@version`.

Function docstring tag order:
1. `@brief`
2. `@details` (optional)
3. `@param[in]` (all params)
4. `@return`
5. `@exception` (optional)
6. `@author`
7. `@date`
8. `@version`

## Software Architecture and Style Rules

If C/C++ code is added, align it with the templates in `1_Documentation/`.

### Python Implementation

- Prefer clear modular structure and type hints.
- Absolute imports are preferred.
- Strictly follow PEP 8 for naming and layout.

### Naming Conventions

Python naming:
- local variables/functions: `snake_case`
- classes: `PascalCase`
- constants: `UPPER_SNAKE_CASE`

C/C++ naming (when applicable):
- local variables: `camelCase`
- local functions: `PascalCase`
- macros/constants: `UPPER_SNAKE_CASE`

### Template Rule

- Preserve all section delimiters from the Randstad style even if the section is currently empty.

## Agent Behavior Guidance

- Prefer repository scripts/workflows over ad-hoc command sequences
- Keep updates pragmatic and minimal
- Maintain compatibility with existing build and documentation flow
- Update `CHANGELOG.md` only when explicitly requested by the user; do not update it automatically.
- When a release version is added/changed in `CHANGELOG.md`, also update `5_Software/app/pyproject.toml` (`[project].version`) in the same change.
