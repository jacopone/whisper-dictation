"""
Text pasting module using ydotool
"""

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class TextPaster:
    """Pastes text into active window using ydotool"""

    def __init__(self, config):
        self.config = config
        self._check_ydotool()

    def _check_ydotool(self):
        """Check if ydotool daemon is running"""
        try:
            result = subprocess.run(["pgrep", "-x", "ydotoold"], capture_output=True)
            if result.returncode != 0:
                logger.warning(
                    "ydotool daemon not running. Start with: systemctl --user start ydotool"
                )
        except Exception as e:
            logger.error(f"Error checking ydotool: {e}")

    def paste(self, text: str):
        """Paste text into active window"""
        if not text:
            return

        logger.info(f"Pasting text: {text[:50]}...")

        try:
            # Small delay to ensure window focus
            time.sleep(0.3)

            # Use ydotool to type text
            subprocess.run(["ydotool", "type", text], check=True)

            logger.info("Text pasted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"ydotool failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error pasting text: {e}")
            raise
