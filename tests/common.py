import subprocess
import sys
from pathlib import Path

import pytest
from PySide2.QtCore import QStandardPaths
from mycartable.main import update_configuration
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
        update_configuration(db)


def setup_session():
    QStandardPaths.setTestModeEnabled(True)

    # modify path
    root = Path(__file__).parents[1]
    python_dir = root / "src"
    sys.path.append(str(python_dir))
    python_dir = root / "src" / "mycartable"
    sys.path.append(str(python_dir))

    # setup qrc
    orig = root / "src" / "qml.qrc"
    dest = python_dir / "qrc.py"
    command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    res = subprocess.run(command, cwd=root, shell=True, capture_output=True)
    if res.returncode != 0:
        pytest.exit(res.stdout.decode())
