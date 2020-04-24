#!/usr/bin/python3

import shutil
import subprocess


import os
import sys
import time
from pathlib import Path


QT_VERSION="5.14.1"
ROOT = Path(__file__).parent
QT_PATH= ROOT / QT_VERSION
DIST = ROOT / "dist" / "MyCartable"
QMLTESTS = ROOT / "build" / "qml_tests"


def get_env():
    env = os.environ
    if sys.platform == "linux":
        env['PATH'] = str(QT_PATH /"gcc_64"/"bin") + ":" + env['PATH']
    return env

def get_shell():
    return os.environ.get('SHELL', None)

def runCommand(command, cwd = str(ROOT), sleep_time=0.2):
    print(f"##### running: {command} #####")
    env = get_env()
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  executable=get_shell(), cwd=cwd, env=env)
    while process.poll() is None:
        for line in process.stdout:
            print(line.strip(b'\n').decode())
        time.sleep(sleep_time)
    if process.returncode == 0:
        print(f"##### finished: {command}  ==>>  OK  with return code {process.returncode} #####")
    else:
        print(f"##### finished: {command}  ==>>  ECHEC  with return code {process.returncode} #####")
        sys.exit(process.returncode)

def cmd_black():
    runCommand("python -m black")

def cmd_cov():
    pytest_cache = ROOT / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
    runCommand('coverage run --rcfile=.coveragerc -m pytest')
    runCommand('coverage report')

def cmd_cov_html():
    cmd_cov()
    runCommand("coverage html")
    html = ROOT / "htmlcov" / "index.html"
    runCommand(f'firefox {html} &')

def cmd_build_binary_as_dir():
    runCommand("pyinstaller  scripts/dir.spec --clean -y")
    cmd_test_binary_as_dir()

def cmd_install():
    runCommand("conda env create -f MyCartableEnv.yml")

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
    executable = "MyCartable"
    if sys.platform == "win32":
        executable   = executable + ".exe"
    runCommand(str(DIST/executable))

def cmd_setup_qml():
    if QMLTESTS.exists():
        shutil.rmtree(QMLTESTS)
    runCommand("python tests/qml_tests/create-js-data.py")
    if sys.platform == "linux":
        runCommand(f"qmake -o {QMLTESTS}/Makefile tests/qml_tests/qml_tests.pro -spec linux-g++ CONFIG+=debug CONFIG+=qml_debug")


def cmd_test_binary_as_dir():
    runCommand("python scripts/test_build_dir.py")

def cmd_test_python():
    runCommand("python -m pytest -s")

def cmd_test_qml():
    qml_tests = "qml_tests"

    if sys.platform == "linux":
        runCommand("make -C build/qml_tests")
    runCommand(str(QMLTESTS / qml_tests))

def cmd_test_qml_reset():
    cmd_setup_qml()
    cmd_test_qml()

def build_commands():
    res = {}
    for i, j in globals().items():
        if callable(j) and i.startswith('cmd_'):
            res[i[4:]] = j
    return res


if __name__ == '__main__':
    com = ""
    commands = build_commands()
    com = sys.argv[-1]
    if com not in commands:
        print(f"commandes possible : {list(commands.keys())}")
        sys.exit(1)
    commands[com]()
