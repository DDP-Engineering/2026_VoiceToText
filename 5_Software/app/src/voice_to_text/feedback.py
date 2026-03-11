#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       feedback.py
@brief      Audio feedback helpers for recording state transitions.
@details    Provides optional beep tones when recording starts/stops.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import platform


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class ToneFeedback:
    """
    @brief      Emits optional beep feedback for UX state changes.
    @details    Uses `winsound.Beep` on Windows; falls back to terminal bell.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    1.0.0
    """

    def __init__(
        self,
        enabled: bool,
        start_frequency_hz: int,
        start_duration_ms: int,
        stop_frequency_hz: int,
        stop_duration_ms: int,
    ) -> None:
        """
        @brief      Initialize tone feedback configuration.
        @param[in]  enabled              Master toggle for beep output.
        @param[in]  start_frequency_hz   Start tone frequency.
        @param[in]  start_duration_ms    Start tone duration.
        @param[in]  stop_frequency_hz    Stop tone frequency.
        @param[in]  stop_duration_ms     Stop tone duration.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._enabled = enabled
        self._start_frequency_hz = start_frequency_hz
        self._start_duration_ms = start_duration_ms
        self._stop_frequency_hz = stop_frequency_hz
        self._stop_duration_ms = stop_duration_ms

    def recording_started(self) -> None:
        """
        @brief      Emit feedback tone for recording start.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._beep(self._start_frequency_hz, self._start_duration_ms)

    def recording_stopped(self) -> None:
        """
        @brief      Emit feedback tone for recording stop.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._beep(self._stop_frequency_hz, self._stop_duration_ms)

    def _beep(self, frequency_hz: int, duration_ms: int) -> None:
        """
        @brief      Emit a single beep using platform-specific strategy.
        @param[in]  frequency_hz    Tone frequency in Hz.
        @param[in]  duration_ms     Tone duration in milliseconds.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        if not self._enabled:
            return

        safe_frequency = max(37, min(32767, int(frequency_hz)))
        safe_duration = max(10, int(duration_ms))

        # Note: Caller is responsible for threading if non-blocking is required.
        if platform.system().lower() == "windows":
            try:
                import winsound
                winsound.Beep(safe_frequency, safe_duration)
                return
            except Exception as exc:
                logger.debug("[feedback] winsound failed: %s", exc)

        try:
            self._beep_with_sounddevice(safe_frequency, safe_duration)
            return
        except Exception as exc:
            logger.debug("[feedback] sounddevice failed: %s", exc)
            # Last fallback for environments without functional sound output.
            print("\a", end="", flush=True)

    def _beep_with_sounddevice(self, frequency_hz: int, duration_ms: int) -> None:
        """
        @brief      Generate and play tone using sounddevice.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        import numpy as np
        import sounddevice as sd

        sample_rate = 44100
        duration_s = float(duration_ms) / 1000.0
        num_samples = max(1, int(sample_rate * duration_s))

        t = np.linspace(0.0, duration_s, num_samples, endpoint=False, dtype=np.float32)
        waveform = 0.2 * np.sin(2.0 * np.pi * frequency_hz * t)

        # block=True is fine here since app.py spawns a thread for this caller.
        sd.play(waveform, samplerate=sample_rate, blocking=True)


# ==============================================================================
# END OF FILE
# ==============================================================================
