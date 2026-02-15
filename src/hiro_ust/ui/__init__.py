"""
Tkinter GUI application for Hiro UST Generator.

Provides user interface for generating UST files from Japanese lyrics
with real-time preview and configurable melody generation.

This module contains the main application window and GUI components.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

from ..logger import get_logger
from ..converter import HiroUSTGenerator
from ..core import HiroUSTProcessor, GeneratorConfig
from ..voice import KEY_ROOTS, get_envelope_presets
from ..melody import SCALES, get_intone_settings
from ..config import HiroConfig
from ..voice.presets import (
    build_preset_from_app,
    apply_preset_to_app,
    save_preset_to_file,
    load_preset_from_file,
)

logger = get_logger(__name__)


class USTGeneratorApp:
    """Main GUI application window for UST generation.

    This class manages the Tkinter UI, handles user interactions,
    and coordinates with the backend processing engine.
    """

    def __init__(self, root):
        """Initialize the application window.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Hiro UST Generator")
        self.root.geometry("900x800")
        self.root.minsize(850, 850)

        logger.info("Initializing USTGeneratorApp")

        # Set window icon
        try:
            if getattr(sys, "frozen", False):
                icon_path = os.path.join(sys._MEIPASS, "hibiki.ico")
            else:
                icon_path = os.path.join(
                    os.path.dirname(__file__), "..", "..", "hibiki.ico"
                )

            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                logger.debug(f"Set window icon: {icon_path}")
        except Exception as e:
            logger.warning(f"Failed to set window icon: {e}")

        # Initialize UI components
        self._create_widgets()
        logger.info("UI initialization complete")

    def _create_widgets(self) -> None:
        """Create and layout all UI widgets."""
        # TODO: Implement UI widget creation
        # This would be extracted from hiro_ust_dev.py USTGeneratorApp.__init__
        # For now, just create a basic window

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = ttk.Label(frame, text="Hiro UST Generator - Refactored UI")
        label.pack()

        info_label = ttk.Label(
            frame,
            text="UI components being organized from hiro_ust_dev.py...",
            foreground="gray",
        )
        info_label.pack(pady=10)

    def generate_ust(self) -> None:
        """Generate UST file from current settings."""
        logger.info("Generate UST button clicked")
        # TODO: Implement UST generation
        pass

    def save_ust(self) -> None:
        """Save UST file to disk."""
        logger.info("Save UST button clicked")
        # TODO: Implement save dialog
        pass

    def preview_phonemes(self) -> None:
        """Show phoneme preview for lyrics."""
        logger.info("Preview phonemes button clicked")
        # TODO: Implement preview
        pass


def main():
    """Main entry point for the GUI application."""
    logger.info("Starting Hiro UST Generator GUI")
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
    logger.info("Application closed")


if __name__ == "__main__":
    main()


__all__ = [
    "USTGeneratorApp",
    "main",
]
