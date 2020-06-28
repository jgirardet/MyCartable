import argparse
import shutil
import subprocess


import os
import sys
import time
from pathlib import Path


PACKAGE = "MyCartable"
QT_VERSION = "5.15.0"
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
VIRTUAL_ENV = ROOT / ".venv"
QT_PATH = ROOT / QT_VERSION
DIST = ROOT / "dist" / PACKAGE
BUILD = ROOT / "build"
QMLTESTS = ROOT / "build" / "qml_tests"


currentProccess = None


def get_env():
    env = os.environ
    path = env["PATH"]
    if sys.platform == "linux":
        new = f"{VIRTUAL_ENV / 'bin'}:{QT_PATH / 'gcc_64' / 'bin'}:"
    elif sys.platform == "win32":
        new = f"{VIRTUAL_ENV / 'Scripts'};"
    env["PATH"] = new + path
    return env


def get_shell():
    return os.environ.get("SHELL", None)


def cmd_rien():
    runCommand("pip -V")


def runCommand(command, cwd=str(ROOT), sleep_time=0.2, with_env=True):
    global currentProccess
    print(f"##### running: {command} #####")
    env = get_env() if with_env else None
    shell = True if sys.platform == "linux" else False
    process = subprocess.Popen(
        command,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        executable=get_shell(),
        cwd=cwd,
        env=env,
        universal_newlines=True,
    )
    currentProccess = process
    while process.poll() is None:
        for line in process.stdout:
            print(line, end="")
        time.sleep(sleep_time)
    if process.returncode == 0:
        print(
            f"##### finished: {command}  ==>>  OK  with return code {process.returncode} #####"
        )
        currentProccess = None
        return True
    else:
        print(
            f"##### finished: {command}  ==>>  ECHEC  with return code {process.returncode} #####"
        )
        return sys.exit(process.returncode)


def cmd_black(*args, **kwargs):
    import black

    if args:
        editedfile = Path(args[0])
        black.format_file_in_place(
            editedfile, fast=True, mode=black.FileMode(), write_back=black.WriteBack(1)
        )
    else:
        runCommand("python -m black src tests")



def cmd_package(*args, **kwargs):
    cmd_make_qrc()
    runCommand("briefcase package")
    # cmd_test_binary_as_dir()


def cmd_clean(*args, **kwargs):
    to_remove = [
        *ROOT.rglob(".pytest_cache"),
        *ROOT.rglob("__pycache__"),
        *ROOT.rglob(".mypy_cache"),
        ROOT / "htmlcov",
        BUILD,
        ROOT / "dist",
        DIST,
        ROOT / "aqtinstall.log",
        ".coverage",
        ROOT/"linux",
        ROOT/"windows"
    ]
    if "-venv" in args:
        to_remove.append(VIRTUAL_ENV)
    if "-qt" in args:
        to_remove.append(QT_PATH)

    for p in to_remove:
        if isinstance(p, str):
            p = ROOT / p
        if p.is_dir():
            shutil.rmtree(p)
        elif p.is_file():
            p.unlink()


def cmd_cov(*args, **kwargs):
    pytest_cache = ROOT / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
    test_path = ROOT / "tests" / "python"
    runCommand(f"coverage run --rcfile=.coveragerc -m pytest {test_path}")
    runCommand("coverage report")


def cmd_cov_html(*args, **kwargs):
    cmd_cov()
    runCommand("coverage html")
    html = ROOT / "htmlcov" / "index.html"
    runCommand(f"firefox {html} &")


def cmd_create_env(*args, **kwargs):
    # elif sys.platform == "win32":
    #     python = "python"
    runCommand(f"{sys.executable} -m venv .venv", with_env=False)


def cmd_install(*args, **kwargs):
    runCommand(f"python -m pip install -U pip")
    runCommand(f"pip install -r requirements.txt")


def cmd_install_dev(*args, **kwargs):
    cmd_create_env(*args, *kwargs)
    cmd_install()
    cmd_install_qt()


def cmd_install_qt(*args, **kwargs):
    if QT_PATH.exists():
        shutil.rmtree(QT_PATH)
    QT_PATH.mkdir(parents=True)
    runCommand(f"aqt install {QT_VERSION} linux desktop")


def cmd_js_style(*args, **kwargs):
    import jsbeautifier

    opts = jsbeautifier.default_options()
    opts.max_preserve_newlines = 2
    opts.indent_size = 2
    if args:
        editedfile = Path(args[0])
        editedfile.write_text(jsbeautifier.beautify_file(editedfile, opts))

    else:
        qmldir = ROOT / "src" / "qml"
        qml_tests = ROOT / "tests" / "qml_tests"
        dirs = (qmldir, qml_tests)

        for d in dirs:
            for f in d.rglob("*.qml"):
                f.write_text(jsbeautifier.beautify_file(f, opts))


def cmd_make_qrc(*args, **kwargs):
    input = SRC / "qml.qrc"
    output = SRC / "mycartable" / "package" / "qrc.py"
    runCommand(f"pyside2-rcc {input} -o {output}")


def cmd_dev(*args, **kwargs):
    cmd_make_qrc()
    runCommand(f"briefcase dev")


def cmd_run(*args, **kwargs):
    runCommand(f"briefcase run -u")


def cmd_setup_qml(*args, **kwargs):
    if QMLTESTS.exists():
        shutil.rmtree(QMLTESTS)
    com = f"qmake -o {QMLTESTS}/Makefile tests/qml_tests/qml_tests.pro -spec {sys.platform}-g++ CONFIG+=debug CONFIG+=qml_debug"
    runCommand(com)


def cmd_test_binary_as_dir(*args, **kwargs):
    runCommand("python scripts/test_build_dir.py", with_env=False)


def cmd_test_python(*args, **kwargs):
    test_path = ROOT / "tests" / "python"
    runCommand(f"python -m pytest -s {test_path}", sleep_time=0.001)


def cmd_test_qml(*args, **kwargs):
    qml_tests = "qml_tests"
    if sys.platform == "linux":
        make = "make"
    elif sys.platform == "win32":
        make = "mingw32-make.exe"
    runCommand(f"{make} -C build/qml_tests")
    command_line = str(QMLTESTS / qml_tests)

    filedir = kwargs.get("input", None)
    if filedir:
        command_line = f"{command_line} -input {filedir}"

    elif args:
        testCase, testname = args
        if testCase == "-input":
            command_line = f"{command_line} {testCase} {testname}"
        else:
            testCase = testCase.lstrip("tst_")

            if not testname.startswith("test_"):
                testname = "test_" + testname
            command_line = f"{command_line} {testCase}::{testname}"
    runCommand(command_line)


def cmd_test_qml_reset(*args, **kwargs):
    cmd_setup_qml()
    cmd_test_qml(*args, **kwargs)


def build_commands(*args, **kwargs):
    res = {}
    for i, j in globals().items():
        if callable(j) and i.startswith("cmd_"):
            res[i[4:]] = j
    return res


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("args", nargs="*")
    parser.add_argument("-input", nargs="?")

    args = parser.parse_args()
    com = args.command
    arguments = args.args

    try:
        commands = build_commands()
        if com not in commands:
            print(f"commandes possible : {list(commands.keys())}")
            sys.exit(1)
        print(arguments)
        commands[com](*arguments, input=args.input)
    except KeyboardInterrupt:
        currentProccess.terminate()
        sys.exit(0)
