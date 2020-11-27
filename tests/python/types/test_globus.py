from PySide2.QtCore import QObject
from mycartable.types import DTB
from mycartable.types.globus import Globus
from pony.orm import db_session


def test_init():
    assert issubclass(Globus, DTB)


def test_annee(qtbot):
    a = Globus()
    assert a.annee == 0
    with qtbot.waitSignal(a.anneeChanged):
        a.annee = 123
    assert a.annee == 123
    with db_session:
        assert a.db.Configuration.option("annee") == 123
