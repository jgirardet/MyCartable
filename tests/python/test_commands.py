from mycartable.commands import BaseCommand


def test_init():

    a = BaseCommand(bla="ble")
    assert a.params == {"bla": "ble"}


def test_redo_et_undo_text():
    class Redo(BaseCommand):
        def redo_command(self):
            self.undo_text = "iii"

    r = Redo()
    r.redo()
    assert r.text() == "iii"


def test_undot():
    class Undo(BaseCommand):
        def undo_command(self):
            self.aa = "aa"

    a = Undo()
    a.undo()
    assert a.aa == "aa"
