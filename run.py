import argparse
import shutil
import subprocess


import os
import sys
import time
from pathlib import Path


PACKAGE = "MyCartable"
QT_VERSION = "5.15.2"
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
VIRTUAL_ENV = ROOT / ".venv"
QT_PATH = ROOT / QT_VERSION
DIST = ROOT / "dist" / PACKAGE
BUILD = ROOT / "build"


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


def runCommand(command, cwd=str(ROOT), sleep_time=0.2, with_env=True, exit=True):
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
        if exit:
            return sys.exit(process.returncode)
        else:
            return False


def cmd_black(*args, **kwargs):
    import black

    if args:
        editedfile = Path(args[0])
        black.format_file_in_place(
            editedfile, fast=True, mode=black.FileMode(), write_back=black.WriteBack(1)
        )
    else:
        runCommand("python -m black src tests")


def cmd_create(*args, **kwargs):
    cmd_clean()
    cmd_make_qrc()
    runCommand("briefcase create")


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
        ROOT / "linux",
        ROOT / "windows",
        ROOT / "Tools",
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
    runCommand(f"{sys.executable} -m venv .venv", with_env=False)


def cmd_install(*args, **kwargs):
    runCommand(f"python -m pip install -U pip")
    # runCommand("pip install https://github.com/jgirardet/briefcase/archive/docker-tty.zip")
    runCommand(f"pip install -r requirements.txt")
    try:
        from briefcase.config import parse_config
    except ModuleNotFoundError:
        runCommand("python run.py install")
        return

    with open("pyproject.toml") as ff:
        _, appconfig = parse_config(ff, sys.platform, "")
    reqs = [f'"{r}"' for r in appconfig["mycartable"]["requires"]]
    runCommand(f"pip install {' '.join(reqs)}")


def cmd_install_qt(*args, **kwargs):
    if QT_PATH.exists():
        shutil.rmtree(QT_PATH)
    QT_PATH.mkdir(parents=True)
    runCommand(f"aqt install {QT_VERSION} linux desktop")


def cmd_make_qrc(*args, **kwargs):
    input = SRC / "qml.qrc"
    output = SRC / "mycartable" / "qrc.py"
    runCommand(f"pyrcc5 {input} -o {output}")


def cmd_dev(*args, **kwargs):
    cmd_make_qrc()
    runCommand(f"briefcase dev")


def cmd_qmlformat(*args, **kwargs):
    # qmlformat pas encore très stable donc on verifie nous même
    files = []
    if filedir := kwargs.get("input", None):
        files.append(Path(filedir))
    else:
        files = list(SRC.rglob("*.qml")) + list(
            (ROOT / "tests" / "qml_tests").rglob("*.qml")
        )
    excluded = [
        "TableauActions.qml",  # https://bugreports.qt.io/browse/QTBUG-86979
        "PageActions.qml",  # https://bugreports.qt.io/browse/QTBUG-86979
        "Buttons.qml",  # https://bugreports.qt.io/browse/QTBUG-86979
        "ImageSection.qml",
        "AnnotationText.qml",
        # "PageSections.qml",  # https://bugreports.qt.io/browse/QTBUG-86979
        # "PageRectangle.qml",  # https://bugreports.qt.io/browse/QTBUG-86979
        # "Legende.qml",
    ]
    errors = []
    for file in files:
        if file.name in excluded:
            print(f"!!!!! skipping {file.name} !!!!!!!")
            continue
        if not runCommand(f"qmlformat -i  {file}", exit=False):
            errors.append(file)
        for file in errors:
            print(f"error with file {file}")
            runCommand(f"qmlformat -V {file}", exit=False)

        if errors:
            sys.exit(1)


def cmd_run(*args, **kwargs):
    os.environ["MYCARTABLE_PROD"] = "True"

    no_input = "--no-input" if kwargs.get("no-input") else ""

    runCommand(f"briefcase run -u")
    # runCommand(f"briefcase run -u {no_input}")


def cmd_setup(*args, **kwargs):
    cmd_create_env(*args, *kwargs)
    cmd_install()
    cmd_install_qt()


def cmd_tag(*args, **kwargs):
    import toml
    import git

    repo = git.Repo(".")
    branch = repo.active_branch.name
    if branch != "master":
        raise SystemError("Un tag ne peut être créé que sur master")
    version = "v" + toml.load("pyproject.toml")["tool"]["briefcase"]["version"]

    runCommand(f"git add pyproject.toml")
    runCommand(f'git commit -m "version {version}"')
    repo.create_tag(version)
    runCommand(f"git push origin {version}")
    runCommand(f"git push")


def cmd_test_binary_as_dir(*args, **kwargs):
    runCommand("python scripts/test_build_dir.py", with_env=False)


def cmd_test_python(*args, **kwargs):
    capture = "-s --no-qt-log" if "capture" in args else ""
    test_path = ROOT / "tests" / "python"
    # f"python -m pytest -s -vvv -n {cpu_count()} {test_path}", sleep_time=0.001
    runCommand(
        f"python -m pytest -vv  --color=yes {capture} {test_path}", sleep_time=0.001
    )


def cmd_test_qml(*args, **kwargs):
    capture = "-s --no-qt-log" if "capture" in args else ""
    test_path = ROOT / "tests" / "qml"
    runCommand(
        f"python -m pytest -vv --color=yes {capture} {test_path} ", sleep_time=0.001
    )


def cmd_upgrade_qt(old, new, *args, **kwargs):
    files = [
        ROOT / ".github" / "workflows" / "test_and_build.yml",
        ROOT / "run.py",
        ROOT / "pyproject.toml",
    ]
    for file in files:
        file.write_text(file.read_text().replace(old, new))


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
    parser.add_argument("-ni", "--no-input")

    args = parser.parse_args()
    com = args.command
    arguments = args.args

    try:
        commands = build_commands()
        if com not in commands:
            print(f"commandes possible : {list(commands.keys())}")
            sys.exit(1)
        commands[com](*arguments, input=args.input)
    except KeyboardInterrupt:
        currentProccess.terminate()
        sys.exit(0)
