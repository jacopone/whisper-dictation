#!/usr/bin/env python3
"""
Main daemon for whisper-dictation
Monitors keyboard for push-to-talk hotkey and coordinates transcription
"""

import os
import sys
import signal
import logging
from pathlib import Path
from evdev import InputDevice, categorize, ecodes, list_devices

from .recorder import AudioRecorder
from .transcriber import WhisperTranscriber
from .ui import DictationUI
from .paste import TextPaster
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DictationDaemon:
    """Main daemon that coordinates all components"""

    def __init__(self, config_path: Path = None):
        self.config = Config(config_path)
        self.recorder = AudioRecorder(self.config)
        self.transcriber = WhisperTranscriber(self.config)
        self.ui = DictationUI(self.config)
        self.paster = TextPaster(self.config)

        self.keys_pressed = set()
        self.is_recording = False
        self.keyboard_device = None

    def find_keyboard_device(self):
        """Find the main keyboard device that supports our hotkey"""
        for device_path in list_devices():
            try:
                device = InputDevice(device_path)
                capabilities = device.capabilities()

                # Check if device has key events
                if ecodes.EV_KEY not in capabilities:
                    continue

                keys = capabilities[ecodes.EV_KEY]

                # Check for standard keyboard keys and modifiers
                has_letters = ecodes.KEY_A in keys
                has_modifiers = (
                    ecodes.KEY_LEFTMETA in keys or
                    ecodes.KEY_RIGHTMETA in keys or
                    ecodes.KEY_LEFTCTRL in keys
                )

                if has_letters and has_modifiers:
                    logger.info(f"Found keyboard device: {device.name} at {device_path}")
                    return device

            except (OSError, PermissionError) as e:
                logger.debug(f"Cannot access {device_path}: {e}")
                continue

        return None

    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            return

        logger.info("Starting recording...")
        self.is_recording = True

        # Show UI
        self.ui.show_recording()

        # Start recording
        self.recorder.start()

    def stop_recording_and_transcribe(self):
        """Stop recording and transcribe audio"""
        if not self.is_recording:
            return

        logger.info("Stopping recording...")
        self.is_recording = False

        # Stop recorder
        audio_file = self.recorder.stop()

        # Update UI
        self.ui.show_transcribing()

        # Check if we have audio
        if not audio_file or not audio_file.exists() or audio_file.stat().st_size < 10000:
            logger.warning("No audio recorded or file too small")
            self.ui.show_error("No audio recorded")
            return

        # Transcribe in background
        def on_transcription_complete(text):
            if text:
                logger.info(f"Transcription: {text}")
                self.paster.paste(text)
                self.ui.show_success(text)
            else:
                logger.warning("No speech detected")
                self.ui.show_error("No speech detected")

        def on_transcription_error(error):
            logger.error(f"Transcription error: {error}")
            self.ui.show_error(f"Transcription failed: {error}")

        self.transcriber.transcribe_async(
            audio_file,
            on_complete=on_transcription_complete,
            on_error=on_transcription_error
        )

    def on_key_event(self, event):
        """Handle keyboard events"""
        if event.type != ecodes.EV_KEY:
            return

        # Track pressed keys
        if event.value == 1:  # Key down
            self.keys_pressed.add(event.code)
        elif event.value == 0:  # Key up
            self.keys_pressed.discard(event.code)

        # Get configured hotkey
        hotkey_modifiers = self.config.get_hotkey_modifiers()
        hotkey_key = self.config.get_hotkey_key()

        # Check if all modifiers are pressed
        has_modifiers = all(mod in self.keys_pressed for mod in hotkey_modifiers)

        # Check if hotkey is pressed
        hotkey_pressed = hotkey_key in self.keys_pressed

        # Start recording when hotkey combo is pressed
        if has_modifiers and event.code == hotkey_key and event.value == 1:
            if not self.is_recording:
                self.start_recording()

        # Stop recording when hotkey is released
        elif event.code == hotkey_key and event.value == 0:
            if self.is_recording:
                self.stop_recording_and_transcribe()

    def run(self):
        """Main daemon loop"""
        logger.info("Starting Whisper Dictation daemon...")

        # Find keyboard
        self.keyboard_device = self.find_keyboard_device()
        if not self.keyboard_device:
            logger.error("Could not find keyboard device")
            logger.error("Make sure you're in the 'input' group: sudo usermod -aG input $USER")
            sys.exit(1)

        # Setup signal handlers
        def cleanup(sig, frame):
            logger.info("Shutting down...")
            if self.is_recording:
                self.recorder.stop()
            self.ui.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        logger.info(f"Monitoring keyboard: {self.keyboard_device.name}")
        logger.info(f"Press {self.config.get_hotkey_display()} to start dictation")

        # Initialize UI
        self.ui.show_ready()

        # Event loop
        try:
            for event in self.keyboard_device.read_loop():
                self.on_key_event(event)
        except KeyboardInterrupt:
            cleanup(None, None)
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            cleanup(None, None)


def main():
    """Entry point"""
    daemon = DictationDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
