import os
import signal
from itertools import zip_longest
from pathlib import Path

# import pytest
import sys
import subprocess
import platform

# from run import runCommand, cmd_run_dist

root = Path(__file__).parents[1].resolve()
sys.path = [str(root)] + sys.path
binary = root / "binary"
dist = root / "dist" / "MyCartable"
main_path = root / "src" / "main"
filename = "MyCartable" if sys.platform == "linux" else "MyCartable.exe"
exe = dist / filename


# def test_binary_included():
#     print("test_binary_included()")
#     dist_binary = dist / "binary"
#     for x, y in zip(dist_binary.glob("**/*"), binary.glob("**/*")):
#         assert x.relative_to(dist) == y.relative_to(root)

DATA_DIR_INCLUDED = [binary, main_path / "fonts", main_path / "icons"]


def test_data_one_dir_included(path: Path):
    path = path.resolve()
    dist_data = (dist / path.name).resolve()

    assert dist_data.exists(), f"{dist_data} est absent du dist"

    path_files = list(x.relative_to(path) for x in path.rglob("*"))
    dist_files = set(x.relative_to(dist_data) for x in dist_data.rglob("*"))
    for i in path_files:
        assert i in dist_files, f"{i} absent   {dist_files}"


def test_data_dir_included():
    for p in DATA_DIR_INCLUDED:
        print(p)
        test_data_one_dir_included(p)


def test_run_exec_in_dir():
    print("test_run_exec")
    STARTUPINFO = None
    if platform.system == "Windows":
        STARTUPINFO = subprocess.STARTUPINFO()
        STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        STARTUPINFO.wShowWindow = subprocess.SW_HIDE
    proc = subprocess.Popen(
        [str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        startupinfo=STARTUPINFO,
        universal_newlines=True,
    )
    print("process is launched")
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        assert proc.poll() is None
        print("execution sans probleme après 10 secondes")
        proc.terminate()
    else:
        print("Le programme s'est interomput prematurement")
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            print("Le programme est bloque")
            print(proc.stdout.read())
            print(proc.stderr.read())
            # on quite
        else:
            print("Message d'erreur")
            print(out)
        raise Exception("Echec du programme")


if __name__ == "__main__":
    test_data_dir_included()
    test_run_exec_in_dir()
