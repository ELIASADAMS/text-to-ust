#!/usr/bin/env python3
"""Build the Hiro UST Windows executable with PyInstaller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
ICON_PATH = PROJECT_ROOT / "hibiki.ico"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
APP_NAME = "Hiro_UST_Generator"
ENTRY_POINT = SRC_DIR / "hiro_ust" / "__main__.py"


def clean_build_dirs() -> None:
    for path in (DIST_DIR, BUILD_DIR):
        if path.exists():
            print(f"Cleaning {path} ...")
            shutil.rmtree(path)


def build() -> Path:
    if not SRC_DIR.is_dir():
        raise RuntimeError(f"Source directory not found: {SRC_DIR}")
    if not ENTRY_POINT.is_file():
        raise RuntimeError(f"Entry point not found: {ENTRY_POINT}")

    clean_build_dirs()

    command = [
        sys.executable,
        "-m", "PyInstaller",
        f"--name={APP_NAME}",
        "--onefile",
        "--windowed",
        "--clean",
        f"--paths={SRC_DIR}",
        "--collect-submodules=hiro_ust",
        "--collect-data=hiro_ust",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={PROJECT_ROOT}",
    ]

    if ICON_PATH.is_file():
        command.append(f"--icon={ICON_PATH}")

    command.append(str(ENTRY_POINT))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)

    executable = DIST_DIR / f"{APP_NAME}.exe"
    if not executable.is_file():
        raise RuntimeError(f"Build completed but executable was not found: {executable}")

    size_mb = executable.stat().st_size / (1024 * 1024)
    print(f"Build successful: {executable} ({size_mb:.2f} MB)")
    return executable


if __name__ == "__main__":
    try:
        build()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
