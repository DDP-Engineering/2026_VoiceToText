#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.

"""
@file       app.py
@brief      End-to-end VoiceToText application controller.
@details    Owns recorder/transcriber/paster components and coordinates
            push-to-talk lifecycle.

@author     Dan Dumitru Pasare + AI Assistant
@date       2026-02-20
@version    1.0.0
"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
from queue import Queue, Empty
from threading import Event, Lock, Thread, Timer
import time

from pynput.keyboard import Key, KeyCode, Listener

from .audio import HoldRecorder
from .config import AppConfig
from .feedback import ToneFeedback
from .overlay import CaptureOverlay
from .paste import TextPaster
from .stt import WhisperTranscriber


logger = logging.getLogger(__name__)


# ==============================================================================
# CLASS DEFINITION
# ==============================================================================


class VoiceToTextApp:
    """
    @brief      End-to-end VoiceToText application controller.
    @details    Owns recorder/transcriber/paster components and coordinates
                push-to-talk lifecycle.

    @author     Dan Dumitru Pasare + AI Assistant
    @date       2026-02-20
    @version    1.0.0
    """
    def __init__(self, config: AppConfig, esc_to_exit: bool = True) -> None:
        """
        @brief      Initialize app with runtime configuration.
        @param[in]  config         Application configuration.
        @param[in]  esc_to_exit    When true, Esc stops the app listener.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        self._config = config
        self._esc_to_exit = esc_to_exit
        self._recorder = HoldRecorder(sample_rate=config.sample_rate, channels=config.channels)
        self._transcriber = WhisperTranscriber(
            model_size=config.model_size,
            vad_enabled=config.vad_enabled,
            vad_silence_ms=config.vad_silence_ms,
            vad_min_speech_ms=config.vad_min_speech_ms,
            vad_threshold_multiplier=config.vad_threshold_multiplier,
            vad_trim_leading=config.vad_trim_leading,
            vad_trim_trailing=config.vad_trim_trailing,
        )
        self._paster = TextPaster()
        self._feedback = ToneFeedback(
            enabled=config.enable_beep,
            start_frequency_hz=config.beep_start_frequency_hz,
            start_duration_ms=config.beep_start_duration_ms,
            stop_frequency_hz=config.beep_stop_frequency_hz,
            stop_duration_ms=config.beep_stop_duration_ms,
        )
        self._overlay: CaptureOverlay | None = None
        self._create_overlay()
        self._recording = False
        self._record_mode = (config.record_mode or "hold").strip().lower()
        if self._record_mode not in {"hold", "toggle"}:
            logger.warning("[recording] invalid record_mode='%s', using 'hold'", config.record_mode)
            self._record_mode = "hold"
        self._hotkey_is_down = False
        self._recording_lock = Lock()
        self._recording_session_id = 0
        self._max_record_seconds = max(0, int(config.max_record_seconds))
        self._hotkey = self._parse_hotkey(config.push_to_talk_key)
        self._recordings_dir = Path(config.recordings_dir)
        self._listener: Listener | None = None
        self._listener_lock = Lock()
        
        self._job_queue: Queue[tuple[int, int]] = Queue()
        self._worker_thread: Thread | None = None
        self._worker_running = Event()
        
        self._output_lock = Lock()
        self._stop_requested = Event()
        self._service_generation = 0
        self._generation_lock = Lock()
        
        self._max_record_timer: Timer | None = None
        self._timer_lock = Lock()

    def run(self) -> None:
        """
        @brief      Start keyboard listener and run application loop.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        logger.info("VoiceToText running.")
        logger.info("Hold '%s' to record, release to transcribe and paste.", self._config.push_to_talk_key)
        if self._esc_to_exit:
            logger.info("Press Esc to exit.")
        else:
            logger.info("Tray mode active. Use tray menu Stop/Exit.")

        self.start()
        self.wait()

    def start(self) -> None:
        """
        @brief      Start keyboard listener without blocking.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        with self._listener_lock:
            if self._listener is not None:
                return

            self._stop_requested.clear()
            if self._overlay is None:
                self._create_overlay()
            
            with self._generation_lock:
                self._service_generation += 1
            
            self._worker_running.set()
            self._worker_thread = Thread(target=self._worker_loop, name="VoiceToTextWorker", daemon=True)
            self._worker_thread.start()
            
            self._listener = Listener(on_press=self._on_press, on_release=self._on_release)
            self._listener.start()

    def wait(self) -> None:
        """
        @brief      Wait for listener thread to stop.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        listener = self._listener
        if listener is None:
            return
        listener.join()

    def stop(self) -> None:
        """
        @brief      Stop listener and active recording, if any.
        @return     None
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        with self._listener_lock:
            listener = self._listener
            self._listener = None

        self._stop_requested.set()
        with self._generation_lock:
            self._service_generation += 1
            
        self._worker_running.clear()
        self._job_queue.put((-1, -1)) # Sentinel to wake up worker

        with self._recording_lock:
            was_recording = self._recording
            self._recording = False
            self._hotkey_is_down = False
            
        with self._timer_lock:
            if self._max_record_timer:
                self._max_record_timer.cancel()
                self._max_record_timer = None

        if was_recording:
            self._recorder.stop_discard()
            Thread(target=self._feedback.recording_stopped, daemon=True).start()
            
        self._overlay_hide()
        self._overlay_close()

        if listener is not None:
            listener.stop()

    def _worker_loop(self) -> None:
        """
        @brief      Long-lived worker for processing recorded audio.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        while self._worker_running.is_set():
            try:
                session_id, generation = self._job_queue.get(timeout=0.5)
                if session_id == -1:
                    break
                self._handle_recording(session_id, generation)
                self._job_queue.task_done()
            except Empty:
                continue
            except Exception as exc:
                logger.error("[worker] unexpected error: %s", exc)

    def _parse_hotkey(self, hotkey_name: str) -> Key | KeyCode:
        """
        @brief      Convert configured hotkey name into pynput key object.
        @author     Dan Dumitru Pasare + AI Assistant
        @date       2026-03-02
        @version    1.0.0
        """
        normalized = hotkey_name.strip().lower()
        key_aliases = {
            "rctrl": "ctrl_r", "right_ctrl": "ctrl_r", "rightctrl": "ctrl_r",
            "lctrl": "ctrl_l", "left_ctrl": "ctrl_l", "leftctrl": "ctrl_l",
            "ralt": "alt_r", "right_alt": "alt_r", "rightalt": "alt_r",
            "lalt": "alt_l", "left_alt": "alt_l", "leftalt": "alt_l",
        }
        normalized = key_aliases.get(normalized, normalized)

        if len(normalized) == 1:
            return KeyCode.from_char(normalized)

        if hasattr(Key, normalized):
            return getattr(Key, normalized)

        raise ValueError(f"Unsupported hotkey: {hotkey_name}")

    def _key_matches(self, key: Key | KeyCode) -> bool:
        expected = self._hotkey
        if isinstance(expected, KeyCode) and isinstance(key, KeyCode):
            return expected.char == key.char
        return key == expected

    def _on_press(self, key: Key | KeyCode) -> None:
        should_start = False
        should_finalize = False
        record_session_id = 0
        with self._recording_lock:
            if not self._key_matches(key):
                return
            if self._hotkey_is_down:
                return
            self._hotkey_is_down = True

            if self._record_mode == "toggle":
                if self._recording:
                    self._recording = False
                    record_session_id = self._recording_session_id
                    should_finalize = True
                else:
                    self._recording = True
                    self._recording_session_id += 1
                    record_session_id = self._recording_session_id
                    should_start = True
            elif not self._recording:
                self._recording = True
                self._recording_session_id += 1
                record_session_id = self._recording_session_id
                should_start = True
        
        if should_start:
            self._start_recording(record_session_id)
        elif should_finalize:
            self._finalize_recording(record_session_id)

    def _on_release(self, key: Key | KeyCode):
        if key == Key.esc and self._esc_to_exit:
            self.stop()
            logger.info("Exiting...")
            return False

        should_finalize = False
        record_session_id = 0
        with self._recording_lock:
            if self._key_matches(key):
                self._hotkey_is_down = False
                if self._record_mode == "hold" and self._recording:
                    self._recording = False
                    record_session_id = self._recording_session_id
                    should_finalize = True
        if should_finalize:
            self._finalize_recording(record_session_id)

        return True

    def _start_recording(self, record_session_id: int) -> None:
        self._overlay_show_recording()
        self._recorder.start()
        Thread(target=self._feedback.recording_started, daemon=True).start()
        logger.info("[recording] start")
        self._start_max_record_timer(record_session_id)

    def _finalize_recording(self, record_session_id: int) -> None:
        Thread(target=self._feedback.recording_stopped, daemon=True).start()
        self._overlay_show_processing()
        
        with self._timer_lock:
            if self._max_record_timer:
                self._max_record_timer.cancel()
                self._max_record_timer = None
                
        with self._generation_lock:
            gen = self._service_generation
        self._job_queue.put((record_session_id, gen))

    def _start_max_record_timer(self, record_session_id: int) -> None:
        if self._max_record_seconds <= 0:
            return

        def timeout_callback() -> None:
            with self._recording_lock:
                if not self._recording or self._recording_session_id != record_session_id:
                    return
                self._recording = False
            logger.info("[recording] max duration reached (%ss)", self._max_record_seconds)
            self._finalize_recording(record_session_id)

        with self._timer_lock:
            if self._max_record_timer:
                self._max_record_timer.cancel()
            self._max_record_timer = Timer(self._max_record_seconds, timeout_callback)
            self._max_record_timer.name = "VoiceToTextRecordTimeout"
            self._max_record_timer.daemon = True
            self._max_record_timer.start()

    def _handle_recording(self, record_session_id: int, generation_at_start: int) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = self._recordings_dir / f"capture_{timestamp}.wav"

        captured = self._recorder.stop_to_wav(audio_path)
        if not captured:
            logger.info("[recording] no audio captured")
            self._overlay_hide()
            return

        logger.info("[recording] saved %s", audio_path)
        try:
            try:
                text, detected_lang = self._transcriber.transcribe(
                    audio_path=audio_path,
                    source_language=self._config.source_language,
                    target_language=self._config.target_language,
                )
            except Exception as exc:
                logger.error("[stt] error: %s", exc)
                self._overlay_show_error()
                return

            if not text:
                logger.info("[stt] empty transcription")
                self._overlay_hide()
                return

            if self._stop_requested.is_set():
                logger.info("[stt] output skipped (service stopped)")
                return
                
            with self._generation_lock:
                if generation_at_start != self._service_generation:
                    logger.info("[stt] output skipped (service generation changed)")
                    return
            
            with self._output_lock:
                self._paster.paste(text, restore_clipboard=self._config.restore_clipboard)

            logger.info("[stt] language=%s chars=%d", detected_lang, len(text))
        finally:
            self._overlay_hide()
            if not self._config.keep_recordings:
                try:
                    if audio_path.exists():
                        audio_path.unlink()
                except OSError as exc:
                    logger.warning("[recording] cleanup warning: %s", exc)
            else:
                self._apply_recording_retention(audio_path)

    def _create_overlay(self) -> None:
        self._overlay = CaptureOverlay(
            enabled=self._config.overlay_enabled,
            position=self._config.overlay_position,
        )

    def _overlay_show_recording(self) -> None:
        if self._overlay: self._overlay.show_recording()

    def _overlay_show_processing(self) -> None:
        if self._overlay: self._overlay.show_processing()

    def _overlay_show_error(self) -> None:
        if self._overlay: self._overlay.show_error()

    def _overlay_hide(self) -> None:
        if self._overlay: self._overlay.hide()

    def _overlay_close(self) -> None:
        if self._overlay:
            self._overlay.close()
            self._overlay = None

    def _apply_recording_retention(self, current_audio_path: Path) -> None:
        try:
            recording_files = sorted(
                self._recordings_dir.glob("*.wav"),
                key=lambda item: item.stat().st_mtime,
            )
        except OSError as exc:
            logger.warning("[recording] retention warning: %s", exc)
            return

        max_recordings = self._config.max_recordings
        if max_recordings > 0 and len(recording_files) > max_recordings:
            excess_count = len(recording_files) - max_recordings
            removable_files = [item for item in recording_files if item != current_audio_path]
            files_to_remove = removable_files[:excess_count]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                except OSError as exc:
                    logger.warning("[recording] cleanup warning: %s", exc)

        max_age_days = self._config.max_recordings_age_days
        if max_age_days > 0:
            cutoff_ts = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            for file_path in self._recordings_dir.glob("*.wav"):
                try:
                    if file_path.stat().st_mtime < cutoff_ts:
                        file_path.unlink()
                except OSError as exc:
                    logger.warning("[recording] cleanup warning: %s", exc)


# ==============================================================================
# END OF FILE
# ==============================================================================
