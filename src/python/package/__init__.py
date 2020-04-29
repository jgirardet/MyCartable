import os
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    # we are running in a bundle
    PROD = True
else:
    # we are running in a normal Python environment
    PROD = False


ROOT = Path(sys._MEIPASS) if PROD else Path(__file__).parents[3]
DATA = ROOT / "data" if PROD else ROOT / "src" / "data"

if sys.platform == "linux":
    BINARY = DATA / "binary" / "linux"
elif sys.platform == "win32":
    BINARY = DATA / "binary" / "windows"
