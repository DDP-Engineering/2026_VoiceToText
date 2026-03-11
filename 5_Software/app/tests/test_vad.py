#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_vad.py
@brief      Unit tests for silence trimming helpers.
@details    Verifies basic behavior of lightweight VAD trimming pipeline.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    1.2.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import numpy as np

from voice_to_text.vad import trim_silence


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_trim_silence_disabled_returns_input() -> None:
    """
    @brief      Verify disabled trimming returns original audio.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.2.0
    """
    audio = np.asarray([0.0, 0.1, 0.0], dtype=np.float32)
    trimmed = trim_silence(
        audio=audio,
        sample_rate=16000,
        enabled=False,
        silence_ms=900,
        min_speech_ms=10,
        vad_threshold_multiplier=3.0,
        trim_leading=True,
        trim_trailing=True,
    )
    assert np.array_equal(trimmed, audio)


def test_trim_silence_removes_edges() -> None:
    """
    @brief      Verify leading/trailing silence is trimmed.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.2.0
    """
    silence = np.zeros(1600, dtype=np.float32)
    speech = np.ones(3200, dtype=np.float32) * 0.2
    audio = np.concatenate([silence, speech, silence])
    trimmed = trim_silence(
        audio=audio,
        sample_rate=16000,
        enabled=True,
        silence_ms=900,
        min_speech_ms=50,
        vad_threshold_multiplier=3.0,
        trim_leading=True,
        trim_trailing=True,
    )
    assert trimmed.size < audio.size
    assert trimmed.size > 0


def test_trim_silence_below_min_returns_empty() -> None:
    """
    @brief      Verify short speech under minimum threshold is rejected.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.2.0
    """
    short_speech = np.ones(100, dtype=np.float32) * 0.3
    trimmed = trim_silence(
        audio=short_speech,
        sample_rate=16000,
        enabled=True,
        silence_ms=900,
        min_speech_ms=200,
        vad_threshold_multiplier=3.0,
        trim_leading=True,
        trim_trailing=True,
    )
    assert trimmed.size == 0
# ==============================================================================
# END OF FILE
# ==============================================================================
