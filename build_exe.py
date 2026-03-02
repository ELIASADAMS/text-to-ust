#!/usr/bin/env python3
"""
Build script for creating Hiro UST Generator EXE with PyInstaller.
Creates a standalone Windows executable with all dependencies included.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def build_exe():
    """Build the EXE using PyInstaller."""

    # Get project paths
    project_root = Path(__file__).parent.resolve()
    icon_path = project_root / "hibiki.ico"
    src_path = project_root / "src"
    dist_path = project_root / "dist"
    build_path = project_root / "build"

    print("=" * 60)
    print("Hiro UST Generator - EXE Build Script")
    print("=" * 60)

    # Check if icon exists
    if not icon_path.exists():
        print(f"⚠️  Warning: Icon file not found at {icon_path}")
        print("   The EXE will be created without a custom icon.")
        icon_arg = ""
    else:
        print(f"✓ Icon found: {icon_path}")
        icon_arg = f"--icon={icon_path}"

    # Clean previous builds
    if dist_path.exists():
        print(f"\n🗑️  Cleaning previous build in {dist_path}...")
        shutil.rmtree(dist_path, ignore_errors=True)
    if build_path.exists():
        shutil.rmtree(build_path, ignore_errors=True)

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Hiro_UST_Generator",
        "--onefile",  # Single EXE file
        "--windowed",  # No console window
        # Ensure PyInstaller searches src for packages
        f"--paths={src_path}",
        # Keep icon in bundle
        "--add-data=hibiki.ico;.",
        "--collect-all=hiro_ust",
        # Hidden imports for common modules that may be missed
        "--hidden-import=hiro_ust",
        "--hidden-import=hiro_ust.core",
        "--hidden-import=hiro_ust.cli",
        "--hidden-import=hiro_ust.logger",
        "--hidden-import=hiro_ust.config",
        "--hidden-import=hiro_ust.constants",
        "--hidden-import=hiro_ust.converter",
        "--hidden-import=hiro_ust.converter.hiragana_map",
        "--hidden-import=hiro_ust.converter.kana_to_hiragana",
        "--hidden-import=hiro_ust.converter.mora_trie",
        "--hidden-import=hiro_ust.converter.phonemizer",
        "--hidden-import=hiro_ust.data",
        "--hidden-import=hiro_ust.data.mora_trie_data",
        "--hidden-import=hiro_ust.generator",
        "--hidden-import=hiro_ust.generator.note_generator",
        "--hidden-import=hiro_ust.generator.ust_strings",
        "--hidden-import=hiro_ust.generator.ustx_writer",
        "--hidden-import=hiro_ust.melody",
        "--hidden-import=hiro_ust.melody.envelopes",
        "--hidden-import=hiro_ust.melody.intone_utils",
        "--hidden-import=hiro_ust.melody.melody_logic",
        "--hidden-import=hiro_ust.melody.scales",
        "--hidden-import=hiro_ust.voice",
        "--hidden-import=hiro_ust.voice.key_roots",
        "--hidden-import=hiro_ust.voice.phonetic_utils",
        "--hidden-import=hiro_ust.voice.presets",
        "--hidden-import=hiro_ust.ui",
        "--hidden-import=hiro_ust.ui.dialogs",
        "--hidden-import=hiro_ust.ui.widgets",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=numpy",
        # Ensure yaml is included for ustx_writer
        "--hidden-import=yaml",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
    ]

    # Add icon if available
    if icon_arg:
        cmd.insert(6, icon_arg)  # after --paths arg

    # Add main script
    cmd.append(str(src_path / "hiro_ust" / "cli.py"))

    print("\n📦 Building EXE with PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, cwd=str(project_root), check=True)

        exe_path = dist_path / "Hiro_UST_Generator.exe"

        if exe_path.exists():
            file_size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("✅ EXE Build Successful!")
            print("=" * 60)
            print(f"📍 Location: {exe_path}")
            print(f"📊 Size: {file_size_mb:.2f} MB")
            print("\n✨ Your Hiro UST Generator is ready to use!")
            print("   You can now distribute this EXE file.")
            return True
        else:
            print("\n❌ Error: EXE file was not created!")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        print("Please check the error messages above.")
        return False
    except FileNotFoundError:
        print("\n❌ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
