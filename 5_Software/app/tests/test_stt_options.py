#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       test_stt_options.py
@brief      Unit tests for STT option helpers.
@details    Validates language normalization and Whisper argument building.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

import sys

from voice_to_text.stt import AVAILABLE_WHISPER_MODELS, WhisperTranscriber, build_whisper_kwargs, normalize_language_code


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def test_normalize_language_code() -> None:
    """
    @brief      Verify language code normalization behavior.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert normalize_language_code("EN_us") == "en-us"


def test_build_whisper_kwargs_auto() -> None:
    """
    @brief      Verify auto source language yields empty Whisper kwargs.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert build_whisper_kwargs("auto") == {}


def test_build_whisper_kwargs_specific() -> None:
    """
    @brief      Verify explicit source language is passed to Whisper kwargs.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert build_whisper_kwargs("de") == {"language": "de"}


def test_available_whisper_models_contains_base() -> None:
    """
    @brief      Verify model option list includes base model.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    assert "base" in AVAILABLE_WHISPER_MODELS


def test_transcriber_invalid_model_falls_back_to_base(monkeypatch) -> None:
    """
    @brief      Verify invalid model name falls back to base model.
    @param[in]  monkeypatch    Pytest monkeypatch fixture.
    @return     None
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    1.0.0
    """
    captured = {}

    class _WhisperStub:
        @staticmethod
        def load_model(model_size, download_root=None):
            captured["model_size"] = model_size
            captured["download_root"] = download_root

            class _Model:
                @staticmethod
                def transcribe(*_args, **_kwargs):
                    return {"text": "", "language": "unknown"}

            return _Model()

    monkeypatch.setitem(sys.modules, "whisper", _WhisperStub)
    transcriber = WhisperTranscriber(model_size="not-a-model", vad_threshold_multiplier=3.0)
    assert transcriber._model_size == "base"
    assert captured["model_size"] == "base"
# ==============================================================================
# END OF FILE
# ==============================================================================
