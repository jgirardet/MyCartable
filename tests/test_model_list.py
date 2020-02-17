import pytest
from package.list_models import PageModel
from datetime import datetime
from unittest.mock import MagicMock

from PySide2.QtCore import Qt, QModelIndex
from fixtures import check_super_init, compare, check_begin_end
from package.database.factory import f_page, b_page, b_section, f_section
from package.list_models import PageModel


@pytest.fixture
def pm(ddbr):
    a = PageModel()
    a._datas = [1, 2, 3, 4]
    return a


class TestPAgeModel:
    def test_base_init(self, qtbot, qtmodeltester):
        assert check_super_init("package.list_models.QAbstractListModel", PageModel)
        b = PageModel()
        assert b._datas == []

        a = PageModel()
        a._datas = [1, 2, 4]
        qtmodeltester.check(a)

    def test_data_role(self):
        a = PageModel()
        a._datas = [1, 2, 3, 4]
        # valid index
        assert a.data(a.index(1, 0), a.PageRole) == 2
        # invalid index
        assert a.data(a.index(99, 99), a.PageRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    def test_data(self):
        p = f_page()
        c = b_section(3, page=p.id, td=True)
        pm = PageModel()
        pm.slotReset(p.id)
        # valid index
        assert pm.data(pm.index(1, 0), pm.PageRole) == c[1]

    def test_flags(self):
        """pas compris comment tester"""

    def test_insertRows(self, pm):
        p = f_page()
        c = b_section(3, page=p.id, td=True)
        pm = PageModel()
        pm.slotReset(p.id)

        d = f_section(page=p.id, position=2)
        pm.insertRows(d.position, 1, QModelIndex())
        print(pm._datas)

        # décallage comme prévu
        assert pm._datas[0]["id"] == 1
        assert pm._datas[1]["id"] == 4
        assert pm._datas[2]["id"] == 2
        assert pm._datas[3]["id"] == 3

    def test_insertRow(self, pm):
        """cela test aussi insertion en dernière place
            et les defautls arguments.
        """
        p = f_page()
        c = b_section(3, page=p.id, td=True)
        pm = PageModel()
        pm.slotReset(p.id)
        d = f_section(page=p.id)
        assert pm.insertRow()  # on test le retour de insertRows

        # décallage comme prévu
        assert pm._datas[0]["id"] == 1
        assert pm._datas[1]["id"] == 2
        assert pm._datas[2]["id"] == 3
        assert pm._datas[3]["id"] == 4

    def test_insertRows_begin_end(self, pm):
        with check_begin_end(pm, "InsertRows"):
            pm.insertRows(0, 1, QModelIndex())

    def test_roles(self, pm):

        assert Qt.DisplayRole in pm.roleNames()
        assert PageModel.PageRole in pm.roleNames()
        assert pm.roleNames()[PageModel.PageRole] == b"page"

    def test_row_count(self, pm):
        assert pm.rowCount("parent") == 4

    def test_sloot_reset(self, pm):
        p = f_page()
        c = b_section(3, page=p.id, td=True)
        pm = PageModel()
        pm.slotReset(p.id)
        # update automagicaly called
        assert pm._datas == c

    def test_ResetModel_begin_end(self, pm):
        with check_begin_end(pm, "ResetModel"):
            pm.slotReset(0)

    def test_lastPostion(self, pm, qtbot):
        assert pm.lastPosition == 0
        with qtbot.waitSignal(pm.lastPositionChanged):
            pm.lastPosition = 2
        assert pm.lastPosition == 2

    def test_property_last_position(self, pm):
        p = f_page(lastViewed=2)
        b_section(3, page=p.id)
        pm.slotReset(p.id)
        assert pm.lastPosition == 2

    # def test_lastPosition(self, pm):
    #     p = f_page(lastViewed=2)
    #     s = f_section(page=p.id)
    #     s2 = f_section(page=p.id)
    #     assert pm.lastPosition == 0
    #     pm.slotReset(p.id)
    #     assert pm.lastPosition == 2
