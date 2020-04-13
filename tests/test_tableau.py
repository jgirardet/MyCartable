import pytest
from PySide2.QtCore import Signal, QModelIndex, Qt
from package.operations.api import create_tableau
from package.page.tableau_section import TableauModel


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


#
# @pytest.fixture
# def tt_db(dao):
#     class TempTableau(TableauModel):
#         ddb = dao
#
#         def __call__(self,rows, columns):
#             self.f_entry = f_tableau(rows, columns)
#             print(self.f_entry)
#             self.sectionId = self.f_entry.id
#             print(self.sectionId)
#
#     return TempTableau()
#
class TestTableauModel:
    def test_rowCount(self, tt):
        tt(4, 8)
        assert tt.rowCount() == 4

    def test_columnCount(self, tt):
        tt(4, 8)
        assert tt.columnCount() == 8

    def test_data_and_datas(self, tt):
        tt(3, 4)
        tt.params["datas"] = [[0, 1, 2, 3,], [4, 5, 6, 7,], [8, 9, 10, 11]]
        assert tt.data(tt.index(0, 0), Qt.DisplayRole) == 0
        assert tt.data(tt.index(0, 2), Qt.DisplayRole) == 2
        assert tt.data(tt.index(1, 2), Qt.DisplayRole) == 6
        assert tt.data(tt.index(2, 3), Qt.DisplayRole) == 11
        assert tt.data(tt.index(9, 3), Qt.DisplayRole) == None
        assert tt.data(tt.index(0, 9), Qt.DisplayRole) == None
