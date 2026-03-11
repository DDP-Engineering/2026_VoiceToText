#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       logging_setup.py
@brief      Logging configuration for VoiceToText runtime.
@details    Configures console and rotating file handlers.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .config import AppConfig


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def setup_logging(config: AppConfig) -> None:
    """
    @brief      Configure root logging handlers.
    @param[in]  config    Application runtime config.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    logger = logging.getLogger()
    logger.handlers.clear()

    level_name = (config.log_level or "INFO").strip().upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    if config.enable_file_logging:
        logs_dir = Path(config.logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            filename=logs_dir / "voice_to_text.log",
            when=config.log_rotation_when,
            interval=config.log_rotation_interval,
            backupCount=config.log_backup_count,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)


# ==============================================================================
# END OF FILE
# ==============================================================================
