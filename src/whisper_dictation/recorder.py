"""
Audio recording module using ffmpeg
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Records audio from microphone using ffmpeg"""

    def __init__(self, config):
        self.config = config
        self.temp_dir = Path("/tmp/whisper-dictation")
        self.temp_dir.mkdir(exist_ok=True)
        self.audio_file = self.temp_dir / "recording.wav"
        self.process: subprocess.Popen | None = None

    def start(self):
        """Start recording audio"""
        # Remove old recording
        if self.audio_file.exists():
            self.audio_file.unlink()

        # Start ffmpeg recording
        logger.info("Starting audio recording...")

        try:
            self.process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-f",
                    "pulse",  # PulseAudio/PipeWire input
                    "-i",
                    "default",  # Default microphone
                    "-ar",
                    "16000",  # 16kHz sample rate (whisper requirement)
                    "-ac",
                    "1",  # Mono audio
                    "-acodec",
                    "pcm_s16le",  # 16-bit PCM
                    "-y",  # Overwrite output file
                    str(self.audio_file),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise

    def stop(self) -> Path | None:
        """Stop recording and return audio file path"""
        if not self.process:
            return None

        logger.info("Stopping audio recording...")

        try:
            # Send SIGTERM to ffmpeg for clean shutdown
            self.process.terminate()

            # Wait for process to finish (max 2 seconds)
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logger.warning("ffmpeg didn't stop gracefully, killing...")
                self.process.kill()
                self.process.wait()

            self.process = None

            # Verify file was created
            if self.audio_file.exists() and self.audio_file.stat().st_size > 0:
                logger.info(f"Recording saved to {self.audio_file}")
                return self.audio_file
            else:
                logger.warning("Audio file not created or empty")
                return None

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return None
