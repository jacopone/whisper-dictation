"""
GTK4 UI for visual feedback
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import subprocess
import logging

logger = logging.getLogger(__name__)


class DictationUI:
    """Manages UI feedback using notifications and optional GTK window"""

    def __init__(self, config):
        self.config = config
        self.notification_icon = "audio-input-microphone"

    def _notify(self, title: str, message: str, urgency: str = "normal"):
        """Show desktop notification"""
        try:
            subprocess.Popen([
                'notify-send',
                '-i', self.notification_icon,
                '-u', urgency,
                title,
                message,
                '-t', '3000'
            ])
        except Exception as e:
            logger.error(f"Notification error: {e}")

    def show_ready(self):
        """Show ready state"""
        logger.info("UI: Ready")
        # Could show a system tray icon here in the future

    def show_recording(self):
        """Show recording state"""
        logger.info("UI: Recording")
        self._notify("Dictation", "🔴 Recording... (release key to stop)")

    def show_transcribing(self):
        """Show transcribing state"""
        logger.info("UI: Transcribing")
        self._notify("Dictation", "⏳ Transcribing...")

    def show_success(self, text: str):
        """Show success with transcribed text preview"""
        preview = text[:50] + ("..." if len(text) > 50 else "")
        logger.info(f"UI: Success - {preview}")
        self._notify("Dictation Complete", f"✅ {preview}")

    def show_error(self, message: str):
        """Show error message"""
        logger.warning(f"UI: Error - {message}")
        self._notify("Dictation Error", f"❌ {message}", urgency="critical")

    def close(self):
        """Cleanup UI resources"""
        logger.info("UI: Closing")
        # Cleanup if needed


# Future: GTK4 floating window for real-time waveform/status
class DictationWindow(Gtk.Window):
    """Optional floating window for live transcription feedback"""

    def __init__(self):
        super().__init__(title="Whisper Dictation")
        self.set_default_size(400, 100)
        self.set_decorated(False)
        self.set_keep_above(True)

        # Center window
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        # Create label
        self.label = Gtk.Label(label="Ready")
        self.label.set_margin_start(20)
        self.label.set_margin_end(20)
        self.label.set_margin_top(20)
        self.label.set_margin_bottom(20)

        self.set_child(self.label)

    def update_text(self, text: str):
        """Update displayed text"""
        GLib.idle_add(self.label.set_text, text)
