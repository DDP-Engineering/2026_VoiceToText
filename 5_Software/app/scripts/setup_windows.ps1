# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
#
# Setup script for VoiceToText app on Windows.
# Creates virtual environment, installs Python dependencies,
# and optionally installs ffmpeg via winget.
#
# Usage:
#   .\setup_windows.ps1
#   .\setup_windows.ps1 -InstallTranslation
#   .\setup_windows.ps1 -InstallTranslation -ArgosSourceLang ro -ArgosTargetLang de
#   .\setup_windows.ps1 -SkipFfmpeg

param(
    [switch]$InstallTranslation,
    [switch]$SkipFfmpeg,
    [string]$ArgosSourceLang = "",
    [string]$ArgosTargetLang = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# Resolve paths
# -----------------------------------------------------------------------------
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

function Find-WingetFfmpegBin {
    $wingetPackagesRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (-not (Test-Path $wingetPackagesRoot)) {
        return $null
    }

    $ffmpegPkg = Get-ChildItem -Path $wingetPackagesRoot -Directory -Filter "Gyan.FFmpeg*" -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $ffmpegPkg) {
        return $null
    }

    $binFolder = Get-ChildItem -Path $ffmpegPkg.FullName -Recurse -Directory -Filter "bin" -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "ffmpeg.exe") } |
        Select-Object -First 1
    if ($null -eq $binFolder) {
        return $null
    }

    return $binFolder.FullName
}

function Ensure-FfmpegPath {
    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($null -ne $ffmpegCmd) {
        Write-Host "[setup] ffmpeg found: $($ffmpegCmd.Source)"
        return $true
    }

    $detectedBin = Find-WingetFfmpegBin
    if ([string]::IsNullOrWhiteSpace($detectedBin)) {
        return $false
    }

    Write-Host "[setup] ffmpeg detected in winget package path: $detectedBin"
    if ($env:Path -notlike "*$detectedBin*") {
        $env:Path = "$detectedBin;$env:Path"
    }

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (($userPath -notlike "*$detectedBin*")) {
        [Environment]::SetEnvironmentVariable("Path", "$detectedBin;$userPath", "User")
        Write-Host "[setup] Added ffmpeg bin to User PATH. Reopen terminal to apply globally."
    }

    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($null -ne $ffmpegCmd) {
        Write-Host "[setup] ffmpeg now available: $($ffmpegCmd.Source)"
        return $true
    }

    return $false
}

function Install-ArgosLanguagePackage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceLang,
        [Parameter(Mandatory = $true)]
        [string]$TargetLang
    )

    $source = $SourceLang.Trim().ToLowerInvariant()
    $target = $TargetLang.Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($source) -or [string]::IsNullOrWhiteSpace($target)) {
        Write-Warning "[setup] Argos package install skipped: source/target language not specified."
        return
    }

    Write-Host "[setup] Installing Argos package for $source->$target ..."
    $pyCode = @"
import sys
from argostranslate import package

src = sys.argv[1].strip().lower()
dst = sys.argv[2].strip().lower()

package.update_package_index()
available = package.get_available_packages()
candidate = next((p for p in available if p.from_code == src and p.to_code == dst), None)
if candidate is None:
    print(f"[setup] ERROR: No Argos package found for {src}->{dst}")
    sys.exit(2)

download_path = candidate.download()
package.install_from_path(download_path)
print(f"[setup] Installed Argos package: {src}->{dst}")
"@
    & $pythonExe -c $pyCode $source $target
}

Write-Host "========================================"
Write-Host "VoiceToText Setup (Windows)"
Write-Host "========================================"
Write-Host "[setup] Project root: $projectRoot"

# -----------------------------------------------------------------------------
# Create virtual environment
# -----------------------------------------------------------------------------
if (-not (Test-Path $venvPath)) {
    Write-Host "[setup] Creating virtual environment..."
    python -m venv $venvPath
}

if (-not (Test-Path $pythonExe)) {
    throw "Virtual environment python not found: $pythonExe"
}

# -----------------------------------------------------------------------------
# Install dependencies
# -----------------------------------------------------------------------------
Write-Host "[setup] Upgrading pip..."
& $pythonExe -m pip install --upgrade pip

Write-Host "[setup] Installing app + dev dependencies..."
& $pythonExe -m pip install -e ".[dev]"

if ($InstallTranslation) {
    Write-Host "[setup] Installing translation extras..."
    & $pythonExe -m pip install -e ".[translate]"

    if (-not [string]::IsNullOrWhiteSpace($ArgosSourceLang) -and -not [string]::IsNullOrWhiteSpace($ArgosTargetLang)) {
        Install-ArgosLanguagePackage -SourceLang $ArgosSourceLang -TargetLang $ArgosTargetLang
    }
    else {
        Write-Host "[setup] Argos language packages not requested. Use -ArgosSourceLang/-ArgosTargetLang to install."
    }
}

# -----------------------------------------------------------------------------
# Ensure ffmpeg availability
# -----------------------------------------------------------------------------
if (-not $SkipFfmpeg) {
    if (-not (Ensure-FfmpegPath)) {
        Write-Host "[setup] ffmpeg not found. Trying installation with winget..."
        $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
        if ($null -ne $wingetCmd) {
            try {
                winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
                if (-not (Ensure-FfmpegPath)) {
                    Write-Warning "[setup] ffmpeg installed but not resolved in PATH yet. Reopen terminal and rerun setup if needed."
                }
            }
            catch {
                Write-Warning "[setup] winget ffmpeg install failed. Install ffmpeg manually and ensure it is in PATH."
            }
        }
        else {
            Write-Warning "[setup] winget not available. Install ffmpeg manually and ensure it is in PATH."
        }
    }
}

Write-Host "[setup] Done. Start app with: .venv\Scripts\python.exe -m voice_to_text.main"
Write-Host "[setup] Or after activation: voice-to-text"
