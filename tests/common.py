import subprocess
from pathlib import Path

import pytest
from PyQt5.QtCore import QStandardPaths
from pony.orm import db_session, flush


def fn_reset_db(db):
    from mycartable.main import update_configuration

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

    root = Path(__file__).parents[1]
    python_dir = root / "src"

    # setup qrc
    orig = root / "src" / "qml.qrc"
    dest = python_dir / "mycartable" / "qrc.py"
    command = f"pyrcc5 {orig.absolute()} -o {dest.absolute()}"
    res = subprocess.run(command, cwd=root, shell=True, capture_output=True)
    if res.returncode != 0:
        pytest.exit(res.stdout.decode())

    import mycartable.qrc
