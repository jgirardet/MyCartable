from pathlib import Path

import pytest
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
    dist_binary = dist / "binary"
    for x, y in zip(dist_binary.glob("**/*"), binary.glob("**/*")):
        assert x.relative_to(dist) == y.relative_to(root)


def test_run_exec_in_dir():
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
    )

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        assert proc.poll() is None
        print("execution sans problème après 10 secondes")
        proc.kill()
        assert True

    else:
        print("Le programme s'est intéromput plus tôt")
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            print("Le programme est bloqué")
            print(proc.stdout.read().decode())
            print(proc.stderr.read().decode())
            # on quite
        else:
            print("Message d'erreur")
            print(out.decode())
        sys.exit(-1)


if __name__ == "__main__":
    pytest.main([str(Path(__file__).parent)])
