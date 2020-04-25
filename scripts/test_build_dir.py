import os
import signal
from pathlib import Path

# import pytest
import sys
import subprocess
import platform

# from run import runCommand, cmd_run_dist

root = Path(__file__).parents[1]
sys.path = [str(root)] + sys.path
binary = root / "binary"
dist = root / "dist" / "MyCartable"
filename = "MyCartable" if sys.platform == "linux" else "MyCartable.exe"
exe = dist / filename


def test_binary_included():
    print("test_binary_included()")
    dist_binary = dist / "binary"
    for x, y in zip(dist_binary.glob("**/*"), binary.glob("**/*")):
        assert x.relative_to(dist) == y.relative_to(root)


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
    test_binary_included()
    test_run_exec_in_dir()
