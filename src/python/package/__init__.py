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


ROOT = Path(sys._MEIPASS) if PROD else Path(__file__).parents[3]
DATA = ROOT / "content" if PROD else ROOT / "src" / "data"
print("ROOT : %s", str(ROOT))
print("DATA : %s", str(DATA))

if sys.platform == "linux":
    BINARY = DATA / "binary" / "linux"
elif sys.platform == "win32":
    BINARY = DATA / "binary" / "windows"
print("BINARY : %s", str(BINARY))
