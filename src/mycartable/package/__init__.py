import os
import sys
from pathlib import Path
import logging

# LOG = logging.getLogger("ojlihk")
# LOG.setLevel(logging.DEBUG)

if getattr(sys, "frozen", False):
    # we are running in a bundle
    PROD = True
else:
    # we are running in a normal Python environment
    PROD = False


# ROOT = Path(sys._MEIPASS) if PROD else Path(__file__).parents[3]  # type: ignore
ROOT = Path(__file__).parent.parent  # type: ignore
# DATA = ROOT / "data" if PROD else ROOT / "src" / "data"
# print(f"ROOT : {str(ROOT)}")
# print(f"DATA : {str(DATA)}")

BINARY: Path

if sys.platform == "linux":
    BINARY = ROOT / "binary" / "linux"
elif sys.platform == "win32":
    BINARY = ROOT / "binary" / "windows"
print(f"BINARY : {str(BINARY)}")
