# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
#
# Build script for VoiceToText portable Windows package.
# Creates self-contained PyInstaller app, bundles ffmpeg binaries and
# pre-downloads Whisper model into distribution, then zips the artifact.
#
# Usage:
#   .\scripts\build_windows_portable.ps1
#   .\scripts\build_windows_portable.ps1 -ModelSize small
#   .\scripts\build_windows_portable.ps1 -ModelSizes tiny,base,small

param(
    [string]$ModelSize = "small",
    [string[]]$ModelSizes = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pyprojectPath = Join-Path $projectRoot "pyproject.toml"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$distRoot = Join-Path $projectRoot "dist"
$buildRoot = Join-Path $projectRoot "build_portable"
$bundleRoot = Join-Path $buildRoot "bundle"
$bundleFfmpegBin = Join-Path $bundleRoot "ffmpeg\bin"
$projectVersion = $null
if (Test-Path $pyprojectPath) {
    $inProjectSection = $false
    foreach ($line in (Get-Content -Path $pyprojectPath)) {
        $trimmed = $line.Trim()
        if ($trimmed -eq "[project]") {
            $inProjectSection = $true
            continue
        }
        if ($inProjectSection -and $trimmed.StartsWith("[")) {
            break
        }
        if ($inProjectSection -and $trimmed -match '^version\s*=\s*"([^"]+)"') {
            $projectVersion = $Matches[1]
            break
        }
    }
}
if ([string]::IsNullOrWhiteSpace($projectVersion)) {
    $projectVersion = "0.0.0"
}

$modelList = @()
if ($null -ne $ModelSizes -and $ModelSizes.Length -gt 0) {
    $modelList = $ModelSizes
}
elseif (-not [string]::IsNullOrWhiteSpace($ModelSize)) {
    $modelList = @($ModelSize)
}
else {
    $modelList = @("small")
}

$modelList = @($modelList |
    ForEach-Object { $_.Trim().ToLowerInvariant() } |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
    Select-Object -Unique)

if ($modelList.Count -eq 0) {
    throw "No valid model size specified. Use -ModelSize or -ModelSizes."
}

Write-Host "========================================"
Write-Host "VoiceToText Portable Build (Windows)"
Write-Host "========================================"
Write-Host "[build] Project root: $projectRoot"
Write-Host "[build] Model sizes:  $($modelList -join ', ')"
Write-Host "[build] Version:      $projectVersion"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python not found: $venvPython"
}

New-Item -ItemType Directory -Force -Path $distRoot | Out-Null
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $bundleFfmpegBin | Out-Null

Write-Host "[build] Installing build dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e ".[dev]" pyinstaller

$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($null -eq $ffmpegCmd) {
    throw "ffmpeg not found in PATH. Install ffmpeg and retry."
}

$ffmpegDir = Split-Path -Path $ffmpegCmd.Source -Parent
$ffmpegExe = Join-Path $ffmpegDir "ffmpeg.exe"
$ffprobeExe = Join-Path $ffmpegDir "ffprobe.exe"
if (-not (Test-Path $ffmpegExe)) {
    throw "ffmpeg.exe not found at: $ffmpegExe"
}
if (-not (Test-Path $ffprobeExe)) {
    throw "ffprobe.exe not found at: $ffprobeExe"
}

Copy-Item -Force -Path $ffmpegExe -Destination (Join-Path $bundleFfmpegBin "ffmpeg.exe")
Copy-Item -Force -Path $ffprobeExe -Destination (Join-Path $bundleFfmpegBin "ffprobe.exe")
Write-Host "[build] Bundled ffmpeg binaries."

foreach ($currentModel in $modelList) {
    $bundleModels = Join-Path $bundleRoot ("models_{0}" -f $currentModel)
    $portableRoot = Join-Path $buildRoot ("VoiceToText_Portable_{0}" -f $currentModel)
    $zipBaseName = if ($modelList.Count -eq 1 -and $currentModel -eq "small") {
        "VoiceToText_Windows_Portable_v{0}.zip" -f $projectVersion
    }
    else {
        "VoiceToText_Windows_Portable_v{0}_{1}.zip" -f $projectVersion, $currentModel
    }
    $zipPath = Join-Path $distRoot $zipBaseName

    if (Test-Path $bundleModels) {
        Remove-Item -Recurse -Force $bundleModels
    }
    New-Item -ItemType Directory -Force -Path $bundleModels | Out-Null

    Write-Host "[build] Pre-downloading Whisper model: $currentModel"
    & $venvPython -c "import whisper; whisper.load_model('$currentModel', download_root=r'$bundleModels')"

    Push-Location $projectRoot
    try {
        Write-Host "[build] Running PyInstaller for model '$currentModel'..."
        & $venvPython -m PyInstaller `
            --noconfirm `
            --clean `
            --name VoiceToText `
            --onedir `
            --noconsole `
            --paths src `
            --collect-data whisper `
            --collect-all pystray `
            --collect-all PIL `
            --hidden-import pynput.keyboard._win32 `
            --add-data "$bundleModels;models" `
            --add-binary "$bundleFfmpegBin\ffmpeg.exe;ffmpeg\bin" `
            --add-binary "$bundleFfmpegBin\ffprobe.exe;ffmpeg\bin" `
            vtt_launcher.py
    }
    finally {
        Pop-Location
    }

    if (Test-Path $portableRoot) {
        Remove-Item -Recurse -Force $portableRoot
    }
    New-Item -ItemType Directory -Force -Path $portableRoot | Out-Null

    Copy-Item -Recurse -Force -Path (Join-Path $distRoot "VoiceToText\*") -Destination $portableRoot

    $runBat = @"
@echo off
REM VoiceToText portable launcher (tray mode)
start "" "%~dp0VoiceToText.exe" --tray
"@
    Set-Content -Path (Join-Path $portableRoot "Run_VoiceToText.bat") -Value $runBat -Encoding ascii

    $portableReadme = @"
<!--
Copyright (c) 2026 DDP Engineering
This software is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) with additional Non-Commercial restriction.
See the LICENSE and LICENSE_NC.txt files for full license details.
-->

VoiceToText Portable (Windows)
==============================

Contents:
- VoiceToText.exe
- Internal Python runtime and dependencies
- Bundled ffmpeg (ffmpeg.exe / ffprobe.exe)
- Pre-downloaded Whisper model: $currentModel

Run:
- Double click Run_VoiceToText.bat (starts tray mode)
- Or run VoiceToText.exe directly from terminal.

Notes:
- Config path: %%APPDATA%%\DDP_VoiceToText\config.yaml
- Recordings path default: %%LOCALAPPDATA%%\DDP_VoiceToText\recordings
"@
    Set-Content -Path (Join-Path $portableRoot "README_PORTABLE.txt") -Value $portableReadme -Encoding utf8

    if (Test-Path $zipPath) {
        Remove-Item -Force $zipPath
    }
    Compress-Archive -Path (Join-Path $portableRoot "*") -DestinationPath $zipPath

    Write-Host "[build] Portable ZIP created: $zipPath"
}
