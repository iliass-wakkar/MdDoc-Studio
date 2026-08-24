#!/usr/bin/env python3
"""
Unified Entry Point for Standalone Desktop Executable.
Launches the native GUI by default, or handles CLI/Web if arguments are provided.
"""

import os
import sys

if getattr(sys, 'frozen', False):
    # PyInstaller temp folder
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, bundle_dir)

from mddoc.gui import launch_gui
from mddoc.cli import main as cli_main

if __name__ == "__main__":
    # If no CLI arguments provided, launch GUI directly
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["--gui", "-g"]):
        launch_gui()
    else:
        cli_main()
