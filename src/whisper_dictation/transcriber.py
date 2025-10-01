"""
Whisper transcription module
"""

import logging
import re
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Transcribes audio using whisper.cpp"""

    def __init__(self, config):
        self.config = config
        self.model_path = config.get_model_path()
        self.temp_dir = Path("/tmp/whisper-dictation")
        self.temp_dir.mkdir(exist_ok=True)

    def transcribe(self, audio_file: Path) -> str | None:
        """Transcribe audio file synchronously"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Whisper model not found at {self.model_path}. "
                f"Download with: whisper-cpp-download-ggml-model {self.config.get('whisper.model', 'medium')}"
            )

        output_file = self.temp_dir / "transcription"
        text_file = output_file.with_suffix(".txt")

        # Remove old transcription
        if text_file.exists():
            text_file.unlink()

        logger.info(f"Transcribing with model: {self.model_path.name}")

        try:
            # Run whisper-cli
            result = subprocess.run(
                [
                    "whisper-cli",
                    "-m",
                    str(self.model_path),
                    "-f",
                    str(audio_file),
                    "--output-txt",
                    "--output-file",
                    str(output_file),
                    "--no-timestamps",
                    "--language",
                    self.config.get("whisper.language", "en"),
                    "--threads",
                    str(self.config.get("whisper.threads", 4)),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Whisper failed: {result.stderr}")
                return None

            # Read transcription
            if not text_file.exists():
                logger.error("Transcription file not created")
                return None

            text = text_file.read_text().strip()

            # Post-process
            text = self._post_process(text)

            # Cleanup
            text_file.unlink()

            return text if text else None

        except subprocess.TimeoutExpired:
            logger.error("Transcription timeout")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    def transcribe_async(
        self,
        audio_file: Path,
        on_complete: Callable[[str | None], None],
        on_error: Callable[[str], None],
    ):
        """Transcribe audio file asynchronously in background thread"""

        def run():
            try:
                text = self.transcribe(audio_file)
                on_complete(text)
            except Exception as e:
                on_error(str(e))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _post_process(self, text: str) -> str:
        """Post-process transcribed text"""
        if not text:
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove filler words if configured
        if self.config.get("processing.remove_filler_words", True):
            text = re.sub(r"\b(um|uh|like|you know)\b", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s+", " ", text).strip()

        # Auto-capitalize first letter if configured
        if self.config.get("processing.auto_capitalize", True) and text:
            text = text[0].upper() + text[1:]

        return text
