import os
import sys

WIN = sys.platform == "win32"
LINUX = sys.platform == "linux"


def get_prod():
    prod = False
    if os.environ.get("MYCARTABLE_PROD", None):
        prod = True
    elif WIN and sys.executable.endswith("pythonw.exe"):
        prod = True
    elif LINUX and os.environ.get("APPIMAGE", None):
        prod = True

    return prod
