from operator import attrgetter, methodcaller
from subprocess import run, CalledProcessError

from pathlib import Path
import sys
import logging


LOG = logging.getLogger(__name__)


def get_binary_root():
    if getattr(sys, "frozen", False):
        # we are running in a bundle
        bundle_dir = Path(sys._MEIPASS)
    else:
        # we are running in a normal Python environment
        bundle_dir = Path(__file__).parents[4]

    if sys.platform == "linux":
        exec_path = bundle_dir / "binary" / "linux"
    elif sys.platform == "win32":
        exec_path = bundle_dir / "binary" / "windows"

    return exec_path.resolve()


def get_binary_path(name):
    root = get_binary_root()
    name = name + ".exe" if sys.platform == "win32" else name
    exec_path = root / name
    return exec_path


def get_command_line_pdftopng(pdf, png_root, resolution):
    cmd = [
        get_binary_path("pdftopng"),
        "-r",
        resolution,
        pdf,
        png_root,
    ]
    return [str(i) for i in cmd]


def collect_files(root: Path, pref="", ext: str = ""):
    res = sorted(root.glob(f"{pref}*{ext}"), key=lambda p: p.name)
    return res


def run_convert_pdf(pdf, png_root, prefix="xxx", resolution=200, timeout=30):
    root = Path(png_root)
    if not root.is_dir():
        root.mkdir(parents=True)

    expected_out = root / prefix

    cmd = get_command_line_pdftopng(pdf, str(expected_out), resolution=resolution)

    try:
        run(cmd, timeout=timeout, check=True, capture_output=True)
    except CalledProcessError as err:
        LOG.error(err.stderr)
        return []
    except TimeoutError as err:
        LOG.error(err.stderr)
        return []

    files = collect_files(root, pref=prefix, ext=".png")
    return files
