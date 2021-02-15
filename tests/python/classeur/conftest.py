from __future__ import annotations
import pytest
from mycartable.classeur import Page, Section
from pony.orm import db_session


@pytest.fixture()
def fsec(fk, bridge):
    def wrapped(genre, **kwargs):
        page = fk.f_page()
        f_genre = f"f_{genre[0].lower()+genre[1:]}"
        x = getattr(fk, f_genre)(page=page.id, **kwargs)
        p = Page.get(page.id, parent=bridge)
        return p.get_section(0)

    return wrapped


@pytest.fixture()
def sec_utils(qtbot, fk) -> TestSectionUtils:
    class TestSectionUtils:
        @staticmethod
        def test_set_property_undo_redo(sec, **props):
            signals = [getattr(sec, p + "Changed") for p in props]
            backups = {p: getattr(sec, p) for p in props}
            with qtbot.waitSignals(signals=signals):
                sec.set(props)
            with db_session:
                it = fk.db.FriseSection[sec.id]
                for k, v in props.items():
                    assert getattr(it, k) == v

            with qtbot.waitSignals(signals=signals):
                sec.undoStack.undo()
            with db_session:
                it = fk.db.FriseSection[sec.id]
                for k, v in props.items():
                    assert getattr(it, k) == backups[k]

            with qtbot.waitSignals(signals=signals):
                sec.undoStack.redo()
            with db_session:
                it = fk.db.FriseSection[sec.id]
                for k, v in props.items():
                    assert getattr(it, k) == v

    return TestSectionUtils


#
#
# class FSEC:
#     def __init__(self, fk, bridge):
#         self.fk = fk
#         self.p = fk.f_page()
#         self.page = Page(self.p.id, parent=bridge)
#
#     def __getattr__(self, item):
#         return getattr(getattr(self.fk))
#
#     def __call__(self, genre, **kwargs):
#         self.s = getattr(self.fk, genre)(**kwargs)
#         self.sec = Section.get(self.s.id, parent=self.page)
#         return self.sec
