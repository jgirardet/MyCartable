import os
import sys
from pathlib import Path
import logging

LOG = logging.getLogger(__name__)
# LOG.setLevel(logging.DEBUG)


WIN = sys.platform == "win32"
LINUX = sys.platform == "linux"

def get_prod():
    prod=False
    if os.environ.get("MYCARTABLE_PROD", None):
        prod=True
    elif WIN and sys.executable.endswith("pythonw.exe"):
        prod=True
    elif LINUX and os.environ.get("APPIMAGE", None):
        prod = True

    LOG.info(f"Application en mode {'PROD' if prod else 'DEBUG'}")
    return prod

ROOT = Path(__file__).parent.parent  # type: ignore


def get_root_binary_path():
    binary =  ROOT / "binary"
    if LINUX:
        binary = binary / "linux"
    elif WIN:
        binary= binary / "windows"
    LOG.info(f"BINARY Path : {binary}")
    return binary


