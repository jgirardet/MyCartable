from unittest.mock import MagicMock, call

import pytest
from PySide2.QtCore import Signal, QModelIndex, Qt
from package.database.factory import f_tableauSection
from package.operations.api import create_tableau
from package.page.tableau_section import TableauModel
from pony.orm import db_session


def test_create_tableau():
    r, c, d = create_tableau(2, 3)
    assert r == 2
    assert c == 3
    assert d == [["", "", ""], ["", "", ""]]
    assert id(d[0]) != id(d[1])


@pytest.fixture
def tt():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class MockTableau(TableauModel):
        def __call__(self, rows, columns):
            rows, columns, datas = create_tableau(rows, columns)
            self.params["rows"] = rows
            self.params["columns"] = columns
            self.params["datas"] = datas

    MockTableau.ddb = Dbo()
    a = MockTableau()
    return a


@pytest.fixture
def tt_db(dao):
    class TempTableau(TableauModel):
        ddb = dao

        def __call__(self, rows, columns):
            self.f_entry = f_tableauSection(rows, columns)
            self.sectionId = self.f_entry.id

    return TempTableau()


#
# class TestTableauModel:
#     def test_rowCount(self, tt):
#         tt(4, 8)
#         assert tt.rowCount() == 4
#
#     def test_columnCount(self, tt):
#         tt(4, 8)
#         assert tt.columnCount() == 8
#
#     def test_data_and_datas(self, tt):
#         tt(3, 4)
#         tt.params["datas"] = [[0, 1, 2, 3,], [4, 5, 6, 7,], [8, 9, 10, 11]]
#         assert tt.data(tt.index(0, 0), Qt.DisplayRole) == 0
#         assert tt.data(tt.index(0, 2), Qt.DisplayRole) == 2
#         assert tt.data(tt.index(1, 2), Qt.DisplayRole) == 6
#         assert tt.data(tt.index(2, 3), Qt.DisplayRole) == 11
#         assert tt.data(tt.index(9, 3), Qt.DisplayRole) == None
#         assert tt.data(tt.index(0, 9), Qt.DisplayRole) == None
#
#     def test_sectionId(self, tt_db, qtbot):
#         with qtbot.waitSignal(tt_db.sectionIdChanged):
#             tt_db(4, 5)
#
#     def test_custom_params_load(self, tt_db):
#         tt_db.custom_params_load = MagicMock()
#         tt_db(34, 34)
#         with db_session:
#             assert tt_db.params == tt_db.f_entry.to_dict()
#         assert tt_db.custom_params_load.call_args_list == [call()]
#
#     # def test_numBerOflines(self, tt):
#     #     tt(4, 5)
#     #     assert tt.numberOfLines == 4
#     #     tt.params["datas"][0][1] = "\n \n"
#     #     tt.params["datas"][0][2] = "\n \n \n"
#     #     tt.params["datas"][1][4] = "\n \n \n \n"
#     #     assert tt.numberOfLines == 11
#
#     def test_setData(self, tt_db):
#         tt_db(4, 5)
#         tt_db.setData()
