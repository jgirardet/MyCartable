import subprocess
import sys
from pathlib import Path

from PySide2.QtCore import QStandardPaths
from pony.orm import db_session, flush


def fn_reset_db(db):
    with db_session:
        for entity in db.entities.values():
            for e in entity.select():
                try:
                    e.delete()
                    flush()
                except:
                    continue


def setup_session():
    QStandardPaths.setTestModeEnabled(True)


    #modify path
    root = Path(__file__).parents[1]
    python_dir = root / "src" / "mycartable"
    sys.path.append(str(python_dir))

    #setup qrc
    orig = root / "src" / "qml.qrc"
    dest = python_dir / "package" / "qrc.py"
    command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    subprocess.run(command, cwd=root, shell=True)

    #import qrc
    from package import qrc