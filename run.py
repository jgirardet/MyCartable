#!/usr/bin/python3

import shutil
import subprocess


import os
import sys
import time
from pathlib import Path


PACKAGE = "MyCartable"
QT_VERSION = "5.14.1"
ROOT = Path(__file__).parent.resolve()
VIRTUAL_ENV = ROOT / ".venv"
QT_PATH = ROOT / QT_VERSION
DIST = ROOT / "dist" / PACKAGE
BUILD = ROOT / "build"
QMLTESTS = ROOT / "build" / "qml_tests"


def get_env():
    env = os.environ
    path = env["PATH"]
    if sys.platform == "linux":
        new = f"{VIRTUAL_ENV / 'bin'}:{QT_PATH / 'gcc_64' / 'bin'}:"
    elif sys.platform == "win32":
        new = f"{VIRTUAL_ENV / 'bin'};"
    env["PATH"] = new + path
    return env


def get_shell():
    return os.environ.get("SHELL", None)


def cmd_rien():
    runCommand("pip -V")


def runCommand(command, cwd=str(ROOT), sleep_time=0.2, with_env=True):
    print(f"##### running: {command} #####")
    env = get_env() if with_env else None
    process = subprocess.Popen(
        command,
        # shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        executable=get_shell(),
        cwd=cwd,
        env=env,
        universal_newlines=True,
    )
    while process.poll() is None:
        for line in process.stdout:
            print(line)
        time.sleep(sleep_time)
    if process.returncode == 0:
        print(
            f"##### finished: {command}  ==>>  OK  with return code {process.returncode} #####"
        )
        return True
    else:
        print(
            f"##### finished: {command}  ==>>  ECHEC  with return code {process.returncode} #####"
        )
        return sys.exit(process.returncode)


def cmd_black():
    runCommand("python -m black")

def cmd_build_binary_as_dir():
    pyinstaller = "pyinstaller"
    runCommand("pyinstaller  scripts/dir.spec --clean -y")
    cmd_test_binary_as_dir()


def cmd_clean():
    to_remove = [
        ROOT / ".pytest_cache",
        QT_PATH,
        ROOT / "htmlcov",
        VIRTUAL_ENV,
        BUILD,
        ROOT / "dist",
        DIST,
        ROOT / "aqtinstall.log",

    ]
    for  p in to_remove:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.is_file():
            p.unlink()



def cmd_cov():
    pytest_cache = ROOT / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
    runCommand("coverage run --rcfile=.coveragerc -m pytest tests")
    runCommand("coverage report")


def cmd_cov_html():
    cmd_cov()
    runCommand("coverage html")
    html = ROOT / "htmlcov" / "index.html"
    runCommand(f"firefox {html} &")


def cmd_create_env():
    if sys.platform == "linux":
        python = "python3"
    elif sys.platform == "win32":
        python = "python"
    runCommand(f"{python} -m venv .venv", with_env=False)

def cmd_install():
    cmd_create_env()
    runCommand(f"python -m pip install -U pip")
    runCommand(f"pip install -r requirements.txt")
    if sys.platform == "linux" and not os.environ.get("CI", False):
        cmd_install_qt()


def cmd_install_qt():
    if QT_PATH.exists():
        shutil.rmtree(QT_PATH)
    QT_PATH.mkdir(parents=True)
    runCommand(f"aqt install {QT_VERSION} linux desktop")


def cmd_make_qrc():
    input = Path("src/main/resources/qml.qrc")
    output = Path("src/main/python/qrc.py")
    runCommand(f"pyside2-rcc {input} -o {output}")


def cmd_runCommand():
    runCommand(f"python src/main/python/main.py")


def cmd_run_dist():
    executable = PACKAGE
    if sys.platform == "win32":
        executable = executable + ".exe"
    runCommand(str(DIST / executable))


def cmd_setup_qml():
    if QMLTESTS.exists():
        shutil.rmtree(QMLTESTS)
    runCommand("python tests/qml_tests/create-js-data.py")
    com = f"qmake -o {QMLTESTS}/Makefile tests/qml_tests/qml_tests.pro -spec {sys.platform}-g++ CONFIG+=debug CONFIG+=qml_debug"
    runCommand(com)


def cmd_test_binary_as_dir():
    runCommand("python scripts/test_build_dir.py", with_env=False)


def cmd_test_python():
    runCommand("python -m pytest -s tests", sleep_time=0.001)


def cmd_test_qml():
    qml_tests = "qml_tests"
    if sys.platform == "linux":
        make = "make"
    elif sys.platform == "win32":
        make = "mingw32-make.exe"
    runCommand(f"{make} -C build/qml_tests")
    runCommand(str(QMLTESTS / qml_tests))


def cmd_test_qml_reset():
    cmd_setup_qml()
    cmd_test_qml()


def build_commands():
    res = {}
    for i, j in globals().items():
        if callable(j) and i.startswith("cmd_"):
            res[i[4:]] = j
    return res


if __name__ == "__main__":
    com = ""
    commands = build_commands()
    com = sys.argv[-1]
    if com not in commands:
        print(f"commandes possible : {list(commands.keys())}")
        sys.exit(1)
    commands[com]()
