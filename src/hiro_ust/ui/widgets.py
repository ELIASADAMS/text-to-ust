"""
Reusable Tkinter widgets for GUI components.

Provides custom widgets for:
- Labeled input fields
- Preset management controls
- Progress indicators
- Param adjustment sliders
- Export/import buttons

Reduces code duplication in main GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List


class LabeledEntry(ttk.Frame):
    """Labeled text entry widget.

    Combines label and entry in a single reusable frame.

    Example:
        >>> entry = LabeledEntry(parent, "Tempo (BPM):", "120")
        >>> entry.pack()
        >>> value = entry.get()
    """

    def __init__(
        self,
        parent: tk.Widget,
        label_text: str = "",
        initial_value: str = "",
        width: int = 12,
        **kwargs,
    ):
        """Init labeled entry.

        Args:
            parent: Parent widget
            label_text: Label text
            initial_value: Initial entry value
            width: Entry field width
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side="left", padx=(0, 5))

        self.var = tk.StringVar(value=initial_value)
        self.entry = ttk.Entry(self, textvariable=self.var, width=width)
        self.entry.pack(side="left", fill="x", expand=True)

    def get(self) -> str:
        """Get entry value."""
        return self.var.get()

    def set(self, value: str) -> None:
        """Set entry value."""
        self.var.set(value)

    def bind(self, event: str, callback: Callable) -> None:
        """Bind event to entry."""
        self.entry.bind(event, callback)


class LabeledSpinbox(ttk.Frame):
    """Labeled spinbox widget.

    Combines label and spinbox for numeric input with up/down buttons.
    """

    def __init__(
        self,
        parent: tk.Widget,
        label_text: str = "",
        from_: float = 0,
        to: float = 100,
        increment: float = 1,
        width: int = 8,
        **kwargs,
    ):
        """Init labeled spinbox.

        Args:
            parent: Parent widget
            label_text: Label text
            from_: Minimum value
            to: Maximum value
            increment: Step size
            width: Widget width
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side="left", padx=(0, 5))

        self.var = tk.DoubleVar(value=from_)
        self.spinbox = ttk.Spinbox(
            self,
            from_=from_,
            to=to,
            increment=increment,
            textvariable=self.var,
            width=width,
        )
        self.spinbox.pack(side="left", fill="x", expand=True)

    def get(self) -> float:
        """Get spinbox value."""
        try:
            return float(self.var.get())
        except ValueError:
            return 0.0

    def set(self, value: float) -> None:
        """Set spinbox value."""
        self.var.set(value)


class LabeledCombobox(ttk.Frame):
    """Labeled combobox widget.

    Combines label and dropdown selector.
    """

    def __init__(
        self,
        parent: tk.Widget,
        label_text: str = "",
        values: List[str] = None,
        initial: str = "",
        width: int = 15,
        **kwargs,
    ):
        """Init labeled combobox.

        Args:
            parent: Parent widget
            label_text: Label text
            values: List of option strings
            initial: Initial selection
            width: Widget width
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side="left", padx=(0, 5))

        self.var = tk.StringVar(value=initial)
        self.combo = ttk.Combobox(
            self,
            textvariable=self.var,
            values=values or [],
            state="readonly",
            width=width,
        )
        self.combo.pack(side="left", fill="x", expand=True)

    def get(self) -> str:
        """Get selected value."""
        return self.var.get()

    def set(self, value: str) -> None:
        """Set selected value."""
        self.var.set(value)

    def set_values(self, values: List[str]) -> None:
        """Update combobox options."""
        self.combo["values"] = values


class LabeledScale(ttk.Frame):
    """Labeled slider widget.

    Combines label and horizontal scale slider with value display.
    """

    def __init__(
        self,
        parent: tk.Widget,
        label_text: str = "",
        from_: float = 0,
        to: float = 100,
        initial: float = 50,
        resolution: float = 1,
        command: Optional[Callable] = None,
        **kwargs,
    ):
        """Init labeled scale.

        Args:
            parent: Parent widget
            label_text: Label text
            from_: Minimum value
            to: Maximum value
            initial: Initial value
            resolution: Step size
            command: Callback function
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 3))

        self.label = ttk.Label(header_frame, text=label_text)
        self.label.pack(side="left")

        self.value_label = ttk.Label(header_frame, text=str(initial), width=5)
        self.value_label.pack(side="right")

        self.var = tk.DoubleVar(value=initial)
        self.scale = ttk.Scale(
            self,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=self.var,
            command=self._on_scale_change if command else None,
        )
        self.scale.pack(fill="x")

        self.on_change = command

    def _on_scale_change(self, value: str) -> None:
        """Internal callback for scale changes."""
        self.value_label.config(text=f"{float(value):.1f}")
        if self.on_change:
            self.on_change(value)

    def get(self) -> float:
        """Get scale value."""
        return self.var.get()

    def set(self, value: float) -> None:
        """Set scale value."""
        self.var.set(value)
        self.value_label.config(text=f"{value:.1f}")


class CheckbuttonGroup(ttk.Frame):
    """Group of related checkbuttons.

    Manages multiple boolean options with labels.
    """

    def __init__(self, parent: tk.Widget, title: str = "", **kwargs):
        """Init checkbutton group.

        Args:
            parent: Parent widget
            title: Optional group title
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        if title:
            ttk.Label(self, text=title, font=("", 10, "bold")).pack(anchor="w")

        self.checkbuttons = {}
        self.variables = {}

    def add_checkbox(
        self,
        name: str,
        label: str = "",
        default: bool = False,
        command: Optional[Callable] = None,
    ) -> tk.BooleanVar:
        """Add checkbox to group.

        Args:
            name: Internal name
            label: Display label
            default: Initial state
            command: Callback function

        Returns:
            Associated BooleanVar
        """
        var = tk.BooleanVar(value=default)
        self.variables[name] = var

        checkbox = ttk.Checkbutton(
            self,
            text=label,
            variable=var,
            command=command,
        )
        checkbox.pack(anchor="w", pady=2)
        self.checkbuttons[name] = checkbox

        return var

    def get(self, name: str) -> bool:
        """Get checkbox value."""
        return self.variables.get(name, tk.BooleanVar()).get()

    def set(self, name: str, value: bool) -> None:
        """Set checkbox value."""
        if name in self.variables:
            self.variables[name].set(value)

    def get_all(self) -> dict:
        """Get all checkbox values."""
        return {name: var.get() for name, var in self.variables.items()}


class ParamPanel(ttk.LabelFrame):
    """Organized panel for related params.

    Groups labeled controls with consistent spacing.
    """

    def __init__(self, parent: tk.Widget, title: str = "", **kwargs):
        """Init param panel.

        Args:
            parent: Parent widget
            title: Panel title
            **kwargs: Additional ttk.LabelFrame options
        """
        super().__init__(parent, text=title, padding=10, **kwargs)

        self.controls = {}

    def add_entry(
        self,
        name: str,
        label: str,
        initial: str = "",
        width: int = 12,
    ) -> LabeledEntry:
        """Add labeled entry to panel."""
        entry = LabeledEntry(self, label, initial, width)
        entry.pack(fill="x", pady=4)
        self.controls[name] = entry
        return entry

    def add_spinbox(
        self,
        name: str,
        label: str,
        from_: float = 0,
        to: float = 100,
        increment: float = 1,
    ) -> LabeledSpinbox:
        """Add labeled spinbox to panel."""
        spinbox = LabeledSpinbox(self, label, from_, to, increment)
        spinbox.pack(fill="x", pady=4)
        self.controls[name] = spinbox
        return spinbox

    def add_combobox(
        self,
        name: str,
        label: str,
        values: List[str],
        initial: str = "",
    ) -> LabeledCombobox:
        """Add labeled combobox to panel."""
        combo = LabeledCombobox(self, label, values, initial)
        combo.pack(fill="x", pady=4)
        self.controls[name] = combo
        return combo

    def add_scale(
        self,
        name: str,
        label: str,
        from_: float = 0,
        to: float = 100,
        initial: float = 50,
    ) -> LabeledScale:
        """Add labeled scale to panel."""
        scale = LabeledScale(self, label, from_, to, initial)
        scale.pack(fill="x", pady=4)
        self.controls[name] = scale
        return scale

    def get_values(self) -> dict:
        """Get all control values in panel."""
        values = {}
        for name, control in self.controls.items():
            if hasattr(control, "get"):
                values[name] = control.get()
        return values

    def set_values(self, values: dict) -> None:
        """Set all control values in panel."""
        for name, value in values.items():
            if name in self.controls and hasattr(self.controls[name], "set"):
                self.controls[name].set(value)


class ProgressBar(ttk.Frame):
    """Progress bar with label and percentage display.

    Shows operation progress with visual bar and text percentage.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Init progress bar."""
        super().__init__(parent, **kwargs)

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 2))

        self.label = ttk.Label(header, text="Processing...")
        self.label.pack(side="left")

        self.percent_label = ttk.Label(header, text="0%")
        self.percent_label.pack(side="right")

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x")

    def set_progress(self, value: float) -> None:
        """Set progress value (0-100).

        Args:
            value: Progress percentage
        """
        self.progress["value"] = int(min(100, max(0, value)))
        self.percent_label.config(text=f"{int(value)}%")
        self.update_idletasks()

    def set_label(self, text: str) -> None:
        """Set progress label text."""
        self.label.config(text=text)


class PresetManager(ttk.Frame):
    """Widget for preset save/load management.

    Provides buttons and status display for preset operations.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_save: Optional[Callable] = None,
        on_load: Optional[Callable] = None,
        **kwargs,
    ):
        """Init preset manager.

        Args:
            parent: Parent widget
            on_save: Callback for save button
            on_load: Callback for load button
            **kwargs: Additional ttk.Frame options
        """
        super().__init__(parent, **kwargs)

        self.on_save_callback = on_save
        self.on_load_callback = on_load

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(
            button_frame,
            text="💾 Save Preset",
            command=self._on_save,
        ).pack(side="left", padx=2)

        ttk.Button(
            button_frame,
            text="📂 Load Preset",
            command=self._on_load,
        ).pack(side="left", padx=2)

        self.status_label = ttk.Label(self, text="No preset loaded")
        self.status_label.pack(fill="x", pady=2)

    def _on_save(self) -> None:
        """Internal save callback."""
        if self.on_save_callback:
            self.on_save_callback()

    def _on_load(self) -> None:
        """Internal load callback."""
        if self.on_load_callback:
            self.on_load_callback()

    def set_status(self, text: str) -> None:
        """Set status message."""
        self.status_label.config(text=text)


__all__ = [
    "LabeledEntry",
    "LabeledSpinbox",
    "LabeledCombobox",
    "LabeledScale",
    "CheckbuttonGroup",
    "ParamPanel",
    "ProgressBar",
    "PresetManager",
]
