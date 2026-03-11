#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       audio.py
@brief      Push-to-talk microphone recording utilities.
@details    Implements hold-to-record capture and write-to-WAV behavior.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock

import numpy as np
import sounddevice as sd
import soundfile as sf


logger = logging.getLogger(__name__)



# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class HoldRecorder:
    """
    @brief      Hold-to-record audio capture helper.
    @details    Starts an input stream while a hotkey is held and persists
                captured frames as WAV when recording ends.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    1.0.0
    """
    def __init__(self, sample_rate: int, channels: int) -> None:
        """
        @brief      Initialize recorder instance.
        @param[in]  sample_rate    Audio sample rate in Hz.
        @param[in]  channels       Number of audio channels.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._sample_rate = sample_rate
        self._channels = channels
        self._lock = Lock()
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        """
        @brief      Start recording stream if not already active.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        with self._lock:
            if self._stream is not None:
                return

            self._frames.clear()

            def callback(indata, _frames, _time, status) -> None:
                if status:
                    logger.warning("[audio] warning: %s", status)
                with self._lock:
                    self._frames.append(indata.copy())

            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="float32",
                callback=callback,
            )
            self._stream.start()

    def stop_to_wav(self, path: Path) -> bool:
        """
        @brief      Stop recording and write captured data to WAV.
        @param[in]  path    Target WAV file path.
        @return     True when audio was captured and saved; otherwise False.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        with self._lock:
            if self._stream is None:
                return False

            self._stream.stop()
            self._stream.close()
            self._stream = None

            if not self._frames:
                return False

            audio_data = np.concatenate(self._frames, axis=0)

        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio_data, self._sample_rate)
        return True

    def stop_discard(self) -> None:
        """
        @brief      Stop active recording stream and discard captured frames.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        with self._lock:
            if self._stream is None:
                return

            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._frames.clear()


# ==============================================================================
# END OF FILE
# ==============================================================================
