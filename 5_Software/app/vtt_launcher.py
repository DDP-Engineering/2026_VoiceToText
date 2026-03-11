# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
"""
@file       vtt_launcher.py
@brief      PyInstaller launcher entrypoint for VoiceToText.
@details    Provides a stable script entry for freezing the package.
@author     DDP Engineering
@date       2026-02-20
@version    1.0.0
"""
from voice_to_text.main import main


if __name__ == "__main__":
    main()
