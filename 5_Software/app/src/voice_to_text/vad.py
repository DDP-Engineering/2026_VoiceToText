#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       vad.py
@brief      Simple energy-based silence trimming helpers.
@details    Provides lightweight VAD-like behavior without extra runtime
            dependencies.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-21
@version    1.2.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import numpy as np


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def trim_silence(
    audio: np.ndarray,
    sample_rate: int,
    enabled: bool,
    silence_ms: int,
    min_speech_ms: int,
    vad_threshold_multiplier: float,
    trim_leading: bool,
    trim_trailing: bool,
) -> np.ndarray:
    """
    @brief      Trim leading/trailing low-energy regions.
    @param[in]  audio          Mono float audio samples.
    @param[in]  sample_rate    Audio sample rate.
    @param[in]  enabled        Master VAD toggle.
    @param[in]  silence_ms     Silence window (ms) used by thresholding.
    @param[in]  min_speech_ms  Minimum accepted speech length (ms).
    @param[in]  vad_threshold_multiplier  Multiplier for noise-floor adaptive threshold.
    @param[in]  trim_leading   Enable leading trim.
    @param[in]  trim_trailing  Enable trailing trim.
    @return     Trimmed audio, or empty array when below minimum speech.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.2.0
    """
    if not enabled:
        return audio

    if audio.size == 0 or sample_rate <= 0:
        return np.asarray([], dtype=np.float32)

    samples = np.asarray(audio, dtype=np.float32)
    abs_samples = np.abs(samples)
    max_amp = float(np.max(abs_samples)) if abs_samples.size > 0 else 0.0
    if max_amp <= 1e-6:
        return np.asarray([], dtype=np.float32)

    # Adaptive threshold tuned for low-gain microphones and quiet speech.
    noise_floor = float(np.percentile(abs_samples, 20))
    threshold = max(0.003, noise_floor * vad_threshold_multiplier, max_amp * 0.03)
    voiced = abs_samples >= threshold
    voiced_idx = np.flatnonzero(voiced)
    if voiced_idx.size == 0:
        return np.asarray([], dtype=np.float32)

    start_idx = int(voiced_idx[0]) if trim_leading else 0
    end_idx = int(voiced_idx[-1]) + 1 if trim_trailing else samples.shape[0]

    # Keep a short context margin around detected speech.
    silence_margin = int(max(0, silence_ms) * sample_rate / 1000.0 * 0.2)
    margin = min(silence_margin, int(sample_rate * 0.05))
    start_idx = max(0, start_idx - margin)
    end_idx = min(samples.shape[0], end_idx + margin)

    trimmed = samples[start_idx:end_idx]
    min_samples = int(max(0, min_speech_ms) * sample_rate / 1000.0)
    if trimmed.size < min_samples:
        return np.asarray([], dtype=np.float32)
    return trimmed


# ==============================================================================
# END OF FILE
# ==============================================================================
