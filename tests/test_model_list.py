from package.list_models import BaseListModel
from datetime import datetime
from unittest.mock import MagicMock

from PySide2.QtCore import Qt, QModelIndex
from fixtures import check_super_init, compare, check_begin_end
from package.database.factory import f_page, b_page
from package.list_models import BaseListModel, RecentsModel


class BaseTest(BaseListModel):
    def populate(self):
        self._datas = [1, 2, 3, 4]


class TestBaseModel:
    def test_base_init(self, qtbot, qtmodeltester):
        assert check_super_init("package.list_models.QAbstractListModel", BaseListModel)
        b = BaseListModel()
        assert b._datas is None

        a = BaseListModel()
        a._datas = [1, 2, 4]
        qtmodeltester.check(a)

    def test_update_datas(self, ddbr):
        a = BaseTest()
        a._datas = ["Rien", "de", "bon"]
        a.update_datas()
        # update automagicaly called
        assert a._datas == [1, 2, 3, 4]

        # no populate go to the main model
        pages = [f_page().to_dict() for p in range(3)]
        a.db = ddbr.Page
        a.populate = lambda: None
        a.update_datas()
        assert compare(a._datas, pages)

    def test_row_cont(self):
        a = BaseTest()
        # row  count is alwauyscalled in real
        # datas should be populate if not in rowcount
        assert a.rowCount("parent") == 4

        # called when data not none
        assert a.rowCount("parent") == 4

    def test_data(self):
        a = BaseTest()
        # valid index
        assert a.data(a.index(1, 0), a.PageRole) == 2
        # invalid index
        assert a.data(a.index(99, 99), a.PageRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None


class TestRecentsModel:
    def test_checker(self, qtmodeltester):
        a = RecentsModel()
        a.update_datas()
        qtmodeltester.check(a)

    def test_populate(self, ddbr):
        a = b_page(5, True, created=datetime.now())
        b = RecentsModel()
        b.db = ddbr.Page
        b.update_datas()

        assert compare(b._datas, a)

    def test_modelreset(self):
        a = RecentsModel()
        a._datas = [1, 2, 3]
        with check_begin_end(a, "RestModel"):
            a.slotResetModel()
            assert a._datas is None
