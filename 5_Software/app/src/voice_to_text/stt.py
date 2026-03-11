#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       stt.py
@brief      Speech-to-text and translation pipeline helpers.
@details    Wraps local Whisper transcription and optional offline translation
            through Argos Translate packages.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    2.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys

import numpy as np
import soundfile as sf

from .vad import trim_silence


logger = logging.getLogger(__name__)

# ==============================================================================
# CONSTANTS
# ==============================================================================

AVAILABLE_WHISPER_MODELS = ("tiny", "base", "small", "medium", "large")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def normalize_language_code(language: str) -> str:
    """
    @brief      Normalize language code format.
    @param[in]  language    Raw language code/name.
    @return     Normalized lowercase code using '-' separators.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    return language.strip().lower().replace("_", "-")


def build_whisper_kwargs(source_language: str) -> dict[str, str]:
    """
    @brief      Build optional Whisper language arguments.
    @param[in]  source_language    Input language hint or 'auto'.
    @return     Keyword argument mapping for Whisper transcribe call.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    normalized = normalize_language_code(source_language)
    if not normalized or normalized == "auto":
        return {}
    return {"language": normalized}


def _translate_with_argos(text: str, source_language: str, target_language: str) -> str:
    """
    @brief      Translate text using local Argos models.
    @param[in]  text               Source text to translate.
    @param[in]  source_language    Source language code.
    @param[in]  target_language    Target language code.
    @return     Translated target-language text.
    @exception  RuntimeError when Argos is missing or required models are absent.
    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-03-02
    @version    2.0.0
    """
    try:
        from argostranslate import translate as argos_translate
    except ImportError as exc:
        raise RuntimeError(
            "Target language requires argostranslate. Install with: pip install -e .[translate]"
        ) from exc

    source_code = normalize_language_code(source_language)
    target_code = normalize_language_code(target_language)
    available = argos_translate.get_installed_languages()

    from_lang = next((lang for lang in available if lang.code == source_code), None)
    to_lang = next((lang for lang in available if lang.code == target_code), None)

    if from_lang is None or to_lang is None:
        raise RuntimeError(
            f"Missing local Argos language package for {source_code}->{target_code}. Install packages first."
        )

    translator = from_lang.get_translation(to_lang)
    return translator.translate(text)


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class WhisperTranscriber:
    """
    @brief      Local Whisper transcriber wrapper.
    @details    Supports plain transcription, English translation by Whisper,
                and optional post-translation to other languages via Argos.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    2.0.0
    """
    def __init__(
        self,
        model_size: str,
        vad_enabled: bool = True,
        vad_silence_ms: int = 900,
        vad_min_speech_ms: int = 250,
        vad_threshold_multiplier: float = 3.0,
        vad_trim_leading: bool = True,
        vad_trim_trailing: bool = True,
    ) -> None:
        """
        @brief      Load Whisper model.
        @param[in]  model_size    Whisper model size identifier.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        import whisper

        normalized_model = str(model_size).strip().lower()
        if normalized_model not in AVAILABLE_WHISPER_MODELS:
            logger.warning("[stt] invalid model '%s', falling back to 'base'", model_size)
            normalized_model = "base"

        download_root = self._resolve_model_root()
        self._model = whisper.load_model(normalized_model, download_root=download_root)
        self._model_size = normalized_model
        self._vad_enabled = bool(vad_enabled)
        self._vad_silence_ms = max(0, int(vad_silence_ms))
        self._vad_min_speech_ms = max(0, int(vad_min_speech_ms))
        self._vad_threshold_multiplier = float(vad_threshold_multiplier)
        self._vad_trim_leading = bool(vad_trim_leading)
        self._vad_trim_trailing = bool(vad_trim_trailing)

    def _resolve_model_root(self) -> str | None:
        """
        @brief      Resolve model storage folder, preferring bundled path.
        @return     Model root path string, or None to use Whisper defaults.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        env_override = os.getenv("VOICE_TO_TEXT_MODELS_DIR")
        if env_override:
            return env_override

        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            bundled_models = exe_dir / "models"
            if bundled_models.exists():
                return str(bundled_models)

        return None

    def transcribe(self, audio_path: Path, source_language: str, target_language: str) -> tuple[str, str]:
        """
        @brief      Convert recorded audio into text.
        @param[in]  audio_path        Path to captured WAV file.
        @param[in]  source_language   Input language hint or auto detect.
        @param[in]  target_language   Empty for native transcription, or target code.
        @return     Tuple of (output_text, detected_source_language).
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        audio_input = self._load_wav_audio(audio_path)
        kwargs = build_whisper_kwargs(source_language)
        target = normalize_language_code(target_language)

        if not target:
            result = self._model.transcribe(audio_input, task="transcribe", **kwargs)
            return result.get("text", "").strip(), result.get("language", "unknown")

        if target in {"en", "english"}:
            result = self._model.transcribe(audio_input, task="translate", **kwargs)
            return result.get("text", "").strip(), result.get("language", "unknown")

        native_result = self._model.transcribe(audio_input, task="transcribe", **kwargs)
        native_text = native_result.get("text", "").strip()
        detected_language = normalize_language_code(native_result.get("language", "unknown"))

        if native_text and detected_language and detected_language != "unknown":
            try:
                translated_text = _translate_with_argos(native_text, detected_language, target)
                return translated_text, detected_language
            except RuntimeError as exc:
                logger.warning("[stt] direct translation failed, trying pivot: %s", exc)

        translated_to_english = self._model.transcribe(audio_input, task="translate", **kwargs)
        english_text = translated_to_english.get("text", "").strip()
        translated_text = _translate_with_argos(english_text, "en", target)
        return translated_text, translated_to_english.get("language", "unknown")

    def _load_wav_audio(self, audio_path: Path) -> np.ndarray | str:
        """
        @brief      Load recorded WAV into float32 mono array for Whisper.
        @param[in]  audio_path    Path to recorded wav file.
        @return     Numpy audio array, or path string as fallback.
        @details    Returning ndarray avoids ffmpeg subprocess invocation for
                    standard app recordings and prevents terminal flash.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    2.0.0
        """
        try:
            audio_data, _sample_rate = sf.read(str(audio_path), dtype="float32", always_2d=False)
            if isinstance(audio_data, np.ndarray) and audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1, dtype=np.float32)
            normalized_audio = np.asarray(audio_data, dtype=np.float32)
            trimmed_audio = trim_silence(
                audio=normalized_audio,
                sample_rate=int(_sample_rate),
                enabled=self._vad_enabled,
                silence_ms=self._vad_silence_ms,
                min_speech_ms=self._vad_min_speech_ms,
                vad_threshold_multiplier=self._vad_threshold_multiplier,
                trim_leading=self._vad_trim_leading,
                trim_trailing=self._vad_trim_trailing,
            )
            return trimmed_audio
        except Exception:
            # Fallback to file path if direct loading fails for any reason.
            return str(audio_path)


# ==============================================================================
# END OF FILE
# ==============================================================================
