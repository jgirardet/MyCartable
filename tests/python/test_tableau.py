from unittest.mock import MagicMock, call

import pytest
from PySide2.QtCore import Signal, QModelIndex, Qt, QByteArray
from PySide2.QtGui import QColor
from package.database.factory import f_tableauSection

from package.page.tableau_section import TableauModel
from pony.orm import db_session


@pytest.fixture
def tt():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class MockTableau(TableauModel):
        def __call__(self, rows, columns):
            self.f_entry = f_tableauSection(lignes=rows, colonnes=columns)
            self.sectionId = self.f_entry.id

    MockTableau.ddb = Dbo()
    a = MockTableau()
    return a


@pytest.fixture(scope="function")
def tt34(dao):
    # class Dbo:
    #     recentsModelChanged = Signal()
    #     sectionIdChanged = Signal()

    class MockTableau(TableauModel):
        pass

    x = f_tableauSection(lignes=3, colonnes=4)
    MockTableau.ddb = dao
    a = MockTableau()
    a.sectionId = x.id
    return a


class TestTableauModel:
    def test_rowCount(self, tt):
        tt(4, 8)
        assert tt.rowCount() == 4

    def test_columnCount(self, tt):
        tt(4, 8)
        assert tt.columnCount() == 8

    def load_proxy(self, tt):
        tab = f_tableauSection(lignes=2, colonnes=5)
        tt.sectionId = tab.id
        assert self.proxy.id == tab.id
        assert self._rows == 2
        assert self._columns == 4

    def test_sectionId(self, tt, qtbot):
        with qtbot.waitSignal(tt.sectionIdChanged):
            tt.sectionId = 2

    def test_ne_rows(self, tt34):
        assert tt34.n_rows == tt34._rows

    def test_roleNames(self, tt):
        assert tt.roleNames() == {
            0: QByteArray(b"display"),
            1: QByteArray(b"decoration"),
            2: QByteArray(b"edit"),
            3: QByteArray(b"toolTip"),
            4: QByteArray(b"statusTip"),
            5: QByteArray(b"whatsThis"),
            Qt.ItemDataRole.BackgroundRole: QByteArray(b"background"),
            Qt.ItemDataRole.ForegroundRole: QByteArray(b"foreground"),
            tt.UnderlineRole: QByteArray(b"underline"),
        }

    def test_data_and_set_datas(self, tt34, ddbr, qtbot):

        # "standant display edit"
        assert tt34.data(tt34.index(0, 0), Qt.DisplayRole) == ""
        tt34.setData(tt34.index(0, 0), "aze", Qt.EditRole)
        assert tt34.data(tt34.index(0, 0), Qt.DisplayRole) == "aze"

        # "standant background  get set"
        assert tt34.data(tt34.index(0, 0), Qt.BackgroundRole) == "white"
        tt34.setData(tt34.index(0, 0), QColor("red"), Qt.BackgroundRole)
        assert tt34.data(tt34.index(0, 0), Qt.BackgroundRole) == QColor("red")

        # "standant foregroud  get set"
        assert tt34.data(tt34.index(0, 0), Qt.ForegroundRole) == "black"
        tt34.setData(tt34.index(0, 0), QColor("red"), Qt.ForegroundRole)
        assert tt34.data(tt34.index(0, 0), Qt.ForegroundRole) == QColor("red")

        # "standant unerline  get set"
        assert tt34.data(tt34.index(0, 0), tt34.UnderlineRole) == False
        tt34.setData(tt34.index(0, 0), True, tt34.UnderlineRole)
        assert tt34.data(tt34.index(0, 0), tt34.UnderlineRole) == True

        # "invalid index"
        assert tt34.data(tt34.index(99, 00), Qt.DisplayRole) == None

        # cell does not existes
        with db_session:
            ddbr.TableauCell[tt34.sectionId, 0, 0].delete()
        assert tt34.data(tt34.index(0, 0), Qt.DisplayRole) == None

        # signals
        with qtbot.waitSignal(tt34.dataChanged):
            tt34.setData(tt34.index(1, 0), "aze", Qt.EditRole)

        # idem pas de change
        with qtbot.assertNotEmitted(tt34.dataChanged):
            tt34.setData(tt34.index(0, 0), "aze", Qt.EditRole)


# def test_numBerOflines(self, tt):
#     tt(4, 5)
#     assert tt.numberOfLines == 4
#     tt.params["datas"][0][1] = "\n \n"
#     tt.params["datas"][0][2] = "\n \n \n"
#     tt.params["datas"][1][4] = "\n \n \n \n"
#     assert tt.numberOfLines == 11

# def test_setData(self, tt_db):
#     tt_db(4, 5)
#     tt_db.setData()
