<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->
# Scripts

Helper scripts for preparing the VoiceToText runtime environment.

## Files

- `setup_windows.ps1`: Main Windows setup script (PowerShell).
- `setup_windows.bat`: Windows wrapper for easier execution from `cmd`.
- `setup_linux.sh`: Main Linux setup script (bash).
- `build_windows_portable.ps1`: Build self-contained Windows portable ZIP.

## What The Scripts Do

- Create `.venv` if missing.
- Upgrade `pip`.
- Install project dependencies (`-e .[dev]`).
- Optionally install translation extras (`-e .[translate]`).
- Check/install `ffmpeg` (required by Whisper audio decoding).
- Optionally install Argos language packages for specific translation pairs.
- Build script additionally bundles:
  - `ffmpeg.exe` and `ffprobe.exe`
  - pre-downloaded Whisper model files
  - PyInstaller self-contained app directory and ZIP

## Windows Usage

PowerShell:

```powershell
cd 5_Software/app
.\scripts\setup_windows.ps1
```

With translation extras:

```powershell
.\scripts\setup_windows.ps1 -InstallTranslation
```

With translation extras and Argos package install:

```powershell
.\scripts\setup_windows.ps1 -InstallTranslation -ArgosSourceLang ro -ArgosTargetLang de
```

Skip ffmpeg checks/install:

```powershell
.\scripts\setup_windows.ps1 -SkipFfmpeg
```

From `cmd`:

```bat
cd 5_Software\app
scripts\setup_windows.bat
```

## Linux Usage

```bash
cd 5_Software/app
chmod +x scripts/setup_linux.sh
./scripts/setup_linux.sh
```

With translation extras:

```bash
./scripts/setup_linux.sh --translate
```

With translation extras and Argos package install:

```bash
./scripts/setup_linux.sh --translate --argos-src=ro --argos-dst=de
```

Skip ffmpeg checks/install:

```bash
./scripts/setup_linux.sh --skip-ffmpeg
```

## Windows Portable Build

```powershell
cd 5_Software/app
.\scripts\build_windows_portable.ps1
```

Optional model size:

```powershell
.\scripts\build_windows_portable.ps1 -ModelSize base
```

Artifact:

- `dist/VoiceToText_Windows_Portable.zip`


## Argos Notes

- Argos packages are needed only for non-English targets (`target_language` not empty and not `en`).
- For `target_language: en`, Whisper native translation is used.

## Troubleshooting

- Windows script execution policy:
  - Use `setup_windows.bat` from `cmd`, or
  - run PowerShell with:
    - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- If `ffmpeg` is still not found after install, close and reopen terminal, then verify:
  - `ffmpeg -version`
