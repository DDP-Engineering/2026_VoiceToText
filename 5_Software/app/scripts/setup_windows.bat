@echo off
REM
REM Copyright (c) 2026 DDP Engineering
REM This software is licensed under the GNU Affero General Public License v3.0
REM (AGPL-3.0) with additional Non-Commercial restriction.
REM See the LICENSE and LICENSE_NC.txt files for full license details.
REM

REM Setup script for VoiceToText app on Windows
REM Creates virtual environment and installs dependencies.
REM Usage:
REM   setup_windows.bat
REM   setup_windows.bat -InstallTranslation
REM   setup_windows.bat -InstallTranslation -ArgosSourceLang ro -ArgosTargetLang de
REM   setup_windows.bat -SkipFfmpeg

SETLOCAL ENABLEEXTENSIONS

ECHO ========================================
ECHO VoiceToText Setup (Windows)
ECHO ========================================

powershell -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1" %*
IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Windows setup failed.
    EXIT /B %ERRORLEVEL%
)

EXIT /B 0
