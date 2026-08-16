"""Clean public GUI adapter for the legacy Hiro generator.

The generator implementation is still being migrated out of ``hiro_ust_dev``.
This adapter keeps the existing working generation logic while presenting one
stable application surface to users.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .hiro_ust_dev import USTGeneratorApp as _LegacyUSTGeneratorApp


class USTGeneratorApp(_LegacyUSTGeneratorApp):
    """User-facing Hiro GUI with a simplified export workflow."""

    JAPANESE_FONT_CANDIDATES = (
        "Yu Gothic UI",
        "Yu Gothic",
        "Meiryo UI",
        "Meiryo",
        "Noto Sans CJK JP",
        "Segoe UI",
    )

    def __init__(self, root):
        super().__init__(root)
        self._apply_japanese_fonts()
        self._simplify_export_controls()

    def _apply_japanese_fonts(self) -> None:
        """Use a Japanese-capable font for lyrics and phoneme preview."""
        chosen = "Segoe UI"
        try:
            available = set(root_font for root_font in self.root.tk.call("font", "families"))
            for candidate in self.JAPANESE_FONT_CANDIDATES:
                if candidate in available:
                    chosen = candidate
                    break
        except tk.TclError:
            pass

        for widget_name in ("lyrics_text", "preview_text"):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.configure(font=(chosen, 11))

        self.root.option_add("*Font", "{%s} 10" % chosen)

    def _walk_widgets(self, parent):
        for child in parent.winfo_children():
            yield child
            yield from self._walk_widgets(child)

    def _simplify_export_controls(self) -> None:
        """Replace three overlapping export actions with one export button."""
        export_button = None
        redundant_buttons = []

        for widget in self._walk_widgets(self.root):
            if not isinstance(widget, ttk.Button):
                continue
            text = widget.cget("text")
            if text == "🎵 Gen":
                export_button = widget
            elif text in {"💾 Save", "🌟 Export USTX"}:
                redundant_buttons.append(widget)

        if export_button is not None:
            export_button.configure(text="📤 Export", command=self.save_ust_only)

        for widget in redundant_buttons:
            widget.destroy()


__all__ = ["USTGeneratorApp"]
