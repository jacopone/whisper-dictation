#!/usr/bin/env python3
"""
Main daemon for whisper-dictation
Monitors keyboard for push-to-talk hotkey and coordinates transcription
"""

import argparse
import logging
import signal
import sys
from pathlib import Path

from evdev import InputDevice, ecodes, list_devices

from .config import Config
from .paste import TextPaster
from .recorder import AudioRecorder
from .transcriber import WhisperTranscriber
from .ui import DictationUI

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

    def _is_virtual_device(self, device_name):
        """Check if device name matches virtual device patterns"""
        virtual_patterns = [
            "virtual",
            "ydotoold",
            "xdotool",
            "uinput",
            "sleep button",
            "power button",
            "lid switch",
            "video bus",
        ]
        return any(pattern.lower() in device_name.lower() for pattern in virtual_patterns)

    def _has_required_keys(self, capabilities):
        """Check if device has letter keys and modifier keys"""
        if ecodes.EV_KEY not in capabilities:
            return False, False
        keys = capabilities[ecodes.EV_KEY]
        has_letters = ecodes.KEY_A in keys
        has_modifiers = (
            ecodes.KEY_LEFTMETA in keys
            or ecodes.KEY_RIGHTMETA in keys
            or ecodes.KEY_LEFTCTRL in keys
        )
        return has_letters, has_modifiers

    def _select_best_keyboard(self, candidates):
        """Select the best keyboard from candidates"""
        if not candidates:
            return None
        # Prefer keyboards with "keyboard" in the name
        for device, path in candidates:
            if "keyboard" in device.name.lower():
                logger.info(f"Selected keyboard: {device.name} at {path}")
                return device
        # Otherwise return the first candidate
        device, path = candidates[0]
        logger.info(f"Selected first candidate: {device.name} at {path}")
        return device

    def find_keyboard_device(self):
        """Find the main keyboard device that supports our hotkey"""
        candidates = []

        for device_path in list_devices():
            try:
                device = InputDevice(device_path)
                has_letters, has_modifiers = self._has_required_keys(device.capabilities())

                if not has_letters:
                    logger.debug(f"Skip {device.name}: no letter keys")
                    continue

                if not has_modifiers:
                    logger.debug(f"Skip {device.name}: no modifier keys")
                    continue

                if self._is_virtual_device(device.name):
                    logger.info(f"Skip virtual device: {device.name} at {device_path}")
                    continue

                logger.info(f"Candidate keyboard: {device.name} at {device_path}")
                candidates.append((device, device_path))

            except (OSError, PermissionError) as e:
                logger.debug(f"Cannot access {device_path}: {e}")
                continue

        if not candidates:
            logger.error("No suitable keyboard devices found!")
            return None

        return self._select_best_keyboard(candidates)

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
            audio_file, on_complete=on_transcription_complete, on_error=on_transcription_error
        )

    def _track_key_state(self, event):
        """Track pressed/released keys"""
        if event.value == 1:  # Key down
            self.keys_pressed.add(event.code)
            logger.debug(f"Key DOWN: {event.code} | Currently pressed: {self.keys_pressed}")
        elif event.value == 0:  # Key up
            self.keys_pressed.discard(event.code)
            logger.debug(f"Key UP: {event.code} | Currently pressed: {self.keys_pressed}")

    def _log_hotkey_debug(self, event, hotkey_key, hotkey_modifiers, has_modifiers, hotkey_pressed):
        """Log hotkey matching for debugging"""
        if event.value == 1 and (event.code == hotkey_key or event.code in hotkey_modifiers):
            logger.info(
                f"Hotkey component pressed: code={event.code}, "
                f"expected_mods={hotkey_modifiers}, expected_key={hotkey_key}, "
                f"has_mods={has_modifiers}, is_hotkey={hotkey_pressed}"
            )

    def on_key_event(self, event):
        """Handle keyboard events"""
        if event.type != ecodes.EV_KEY:
            return

        # Track key state
        self._track_key_state(event)

        # Get configured hotkey
        hotkey_modifiers = self.config.get_hotkey_modifiers()
        hotkey_key = self.config.get_hotkey_key()

        # Check if ANY of the modifier keys are pressed (e.g., left OR right Super)
        has_modifiers = any(mod in self.keys_pressed for mod in hotkey_modifiers)
        hotkey_pressed = hotkey_key in self.keys_pressed

        # Log for debugging
        self._log_hotkey_debug(event, hotkey_key, hotkey_modifiers, has_modifiers, hotkey_pressed)

        # Handle hotkey press
        if (
            has_modifiers
            and event.code == hotkey_key
            and event.value == 1
            and not self.is_recording
        ):
            logger.info("🎤 HOTKEY COMBO DETECTED - Starting recording!")
            self.start_recording()

        # Handle hotkey release
        if event.code == hotkey_key and event.value == 0 and self.is_recording:
            logger.info("🛑 HOTKEY RELEASED - Stopping recording!")
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
    parser = argparse.ArgumentParser(description="Whisper Dictation Daemon")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging (shows all key events)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging (shows INFO messages)"
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        help="Override language (en, it, es, fr, etc.). Default: from config file",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Override model (tiny, base, small, medium, large). Default: from config file",
    )
    args = parser.parse_args()

    # Configure logging based on flags
    log_level = logging.WARNING  # Default: quiet
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    daemon = DictationDaemon()

    # Override config with command-line arguments
    if args.language:
        daemon.config.config["whisper"]["language"] = args.language
        logger.info(f"Language override: {args.language}")

    if args.model:
        daemon.config.config["whisper"]["model"] = args.model
        logger.info(f"Model override: {args.model}")

    daemon.run()


if __name__ == "__main__":
    main()
