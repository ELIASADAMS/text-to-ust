"""
File dialog utilities for UST/USTX file operations.
"""

import os
from pathlib import Path
from typing import Optional
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox


class FileDialog:
    """Manager for file open/save dialogs."""

    # File type filters
    FILE_TYPES = {
        "ust": ("UST Files (*.ust)", "*.ust"),
        "ustx": ("USTX Files (*.ustx)", "*.ustx"),
        "both": [
            ("UST/USTX Files", "*.ust *.ustx"),
            ("UST Files", "*.ust"),
            ("USTX Files", "*.ustx"),
        ],
        "text": ("Text Files (*.txt)", "*.txt"),
        "json": ("JSON Files (*.json)", "*.json"),
        "yaml": ("YAML Files (*.yaml *.yml)", "*.yaml *.yml"),
        "all": ("All Files", "*.*"),
    }

    # Default directories
    DEFAULT_DIRS = {
        "ust": "projects",
        "backup": "backup",
        "presets": "presets",
        "config": "config",
    }

    @staticmethod
    def get_default_directory(category: str = "ust") -> str:
        """Get default save directory for category.

        Args:
            category: One of "ust", "backup", "presets", "config"

        Returns:
            Path to default directory (created if needed)
        """
        base_dir = Path.home() / "Music" / "Hiro_UST"
        subdir = FileDialog.DEFAULT_DIRS.get(category, category)
        target_dir = base_dir / subdir

        # Create if doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        return str(target_dir)

    @staticmethod
    def save_ust(
        parent_widget=None,
        initial_name: str = "Hiro_Main",
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Open save dialog for UST file.

        Args:
            parent_widget: Parent Tkinter widget
            initial_name: Default filename (without extension)
            initial_dir: Starting directory (default: user Music folder)

        Returns:
            Full file path if saved, None if cancelled
        """
        if initial_dir is None:
            initial_dir = FileDialog.get_default_directory("ust")

        filepath = filedialog.asksaveasfilename(
            parent=parent_widget,
            initialdir=initial_dir,
            initialfile=f"{initial_name}.ust",
            filetypes=[FileDialog.FILE_TYPES["ust"], FileDialog.FILE_TYPES["all"]],
            defaultextension=".ust",
        )

        return filepath if filepath else None

    @staticmethod
    def save_ustx(
        parent_widget=None,
        initial_name: str = "Hiro_Main",
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Open save dialog for USTX file.

        Args:
            parent_widget: Parent Tkinter widget
            initial_name: Default filename (without extension)
            initial_dir: Starting directory (default: user Music folder)

        Returns:
            Full file path if saved, None if cancelled
        """
        if initial_dir is None:
            initial_dir = FileDialog.get_default_directory("ust")

        filepath = filedialog.asksaveasfilename(
            parent=parent_widget,
            initialdir=initial_dir,
            initialfile=f"{initial_name}.ustx",
            filetypes=[FileDialog.FILE_TYPES["ustx"], FileDialog.FILE_TYPES["all"]],
            defaultextension=".ustx",
        )

        return filepath if filepath else None

    @staticmethod
    def save_preset(
        parent_widget=None,
        initial_name: str = "My_Preset",
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Open save dialog for preset file (JSON).

        Args:
            parent_widget: Parent Tkinter widget
            initial_name: Default filename (without extension)
            initial_dir: Starting directory

        Returns:
            Full file path if saved, None if cancelled
        """
        if initial_dir is None:
            initial_dir = FileDialog.get_default_directory("presets")

        filepath = filedialog.asksaveasfilename(
            parent=parent_widget,
            initialdir=initial_dir,
            initialfile=f"{initial_name}.json",
            filetypes=[FileDialog.FILE_TYPES["json"], FileDialog.FILE_TYPES["all"]],
            defaultextension=".json",
        )

        return filepath if filepath else None

    @staticmethod
    def open_preset(
        parent_widget=None,
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Open file dialog for loading preset.

        Args:
            parent_widget: Parent Tkinter widget
            initial_dir: Starting directory

        Returns:
            Full file path if selected, None if cancelled
        """
        if initial_dir is None:
            initial_dir = FileDialog.get_default_directory("presets")

        filepath = filedialog.askopenfilename(
            parent=parent_widget,
            initialdir=initial_dir,
            filetypes=[FileDialog.FILE_TYPES["json"], FileDialog.FILE_TYPES["all"]],
        )

        return filepath if filepath else None

    @staticmethod
    def select_ust_file(
        parent_widget=None,
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Open file dialog for selecting existing UST file.

        Args:
            parent_widget: Parent Tkinter widget
            initial_dir: Starting directory

        Returns:
            Full file path if selected, None if cancelled
        """
        if initial_dir is None:
            initial_dir = FileDialog.get_default_directory("ust")

        filepath = filedialog.askopenfilename(
            parent=parent_widget,
            initialdir=initial_dir,
            filetypes=[FileDialog.FILE_TYPES["both"], FileDialog.FILE_TYPES["all"]],
        )

        return filepath if filepath else None


class SaveDialog:
    """Dialog for configuring save options."""

    @staticmethod
    def ask_save_format(parent_widget=None) -> Optional[str]:
        """Ask user to choose between UST and USTX format.

        Args:
            parent_widget: Parent Tkinter widget

        Returns:
            "ust", "ustx", or None if cancelled
        """
        from tkinter import simpledialog

        result = messagebox.askyesno(
            "Save Format",
            "Save as USTX (extended format)?\n\n"
            "Yes = USTX (recommended, more features)\n"
            "No = UST (standard format, wider compatibility)",
            parent=parent_widget,
        )

        return "ustx" if result else "ust" if result is False else None

    @staticmethod
    def ask_save_location(parent_widget=None) -> Optional[str]:
        """Ask user to select save location and filename.

        Args:
            parent_widget: Parent Tkinter widget

        Returns:
            Full file path if selected, None if cancelled
        """
        # Auto-choose based on file format preference
        format_choice = SaveDialog.ask_save_format(parent_widget)
        if format_choice == "ustx":
            return FileDialog.save_ustx(parent_widget)
        elif format_choice == "ust":
            return FileDialog.save_ust(parent_widget)
        else:
            return None


class DialogMessages:
    """Standard message dialogs."""

    @staticmethod
    def show_info(
        title: str,
        message: str,
        parent_widget=None,
    ) -> None:
        """Show info dialog.

        Args:
            title: Dialog title
            message: Message text
            parent_widget: Parent Tkinter widget
        """
        messagebox.showinfo(title, message, parent=parent_widget)

    @staticmethod
    def show_warning(
        title: str,
        message: str,
        parent_widget=None,
    ) -> None:
        """Show warning dialog.

        Args:
            title: Dialog title
            message: Message text
            parent_widget: Parent Tkinter widget
        """
        messagebox.showwarning(title, message, parent=parent_widget)

    @staticmethod
    def show_error(
        title: str,
        message: str,
        parent_widget=None,
    ) -> None:
        """Show error dialog.

        Args:
            title: Dialog title
            message: Message text
            parent_widget: Parent Tkinter widget
        """
        messagebox.showerror(title, message, parent=parent_widget)

    @staticmethod
    def ask_yes_no(
        title: str,
        message: str,
        parent_widget=None,
    ) -> bool:
        """Ask yes/no question.

        Args:
            title: Dialog title
            message: Message text
            parent_widget: Parent Tkinter widget

        Returns:
            True if yes, False if no
        """
        return messagebox.askyesno(title, message, parent=parent_widget)

    @staticmethod
    def ask_save_changes(parent_widget=None) -> Optional[bool]:
        """Ask if user wants to save changes.

        Returns:
            True (save), False (don't save), None (cancel)
        """
        result = messagebox.askyesnocancel(
            "Save Changes",
            "Do you want to save changes before closing?",
            parent=parent_widget,
        )
        return result

    @staticmethod
    def show_file_saved(
        filepath: str,
        parent_widget=None,
    ) -> None:
        """Show file saved confirmation.

        Args:
            filepath: Path to saved file
            parent_widget: Parent Tkinter widget
        """
        filename = os.path.basename(filepath)
        directory = os.path.dirname(filepath)
        DialogMessages.show_info(
            "File Saved",
            f"✅ {filename}\n\n📁 {directory}",
            parent_widget,
        )

    @staticmethod
    def show_file_error(
        filepath: str,
        error: Exception,
        parent_widget=None,
    ) -> None:
        """Show file operation error.

        Args:
            filepath: Path where error occurred
            error: Exception that occurred
            parent_widget: Parent Tkinter widget
        """
        filename = os.path.basename(filepath)
        DialogMessages.show_error(
            "File Error",
            f"❌ Failed to save {filename}\n\n{str(error)}",
            parent_widget,
        )


__all__ = [
    "FileDialog",
    "SaveDialog",
    "DialogMessages",
]
