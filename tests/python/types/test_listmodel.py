from unittest.mock import MagicMock, call

import pytest
from PySide2.QtCore import QModelIndex, Qt, QByteArray
from mycartable.types.dtb import DTB
from mycartable.types.listmodel import DtbListModel


@pytest.fixture()
def lm():
    class LM(DtbListModel):
        _data = ["a"]

        def rowCount(self, parent=QModelIndex()):
            return len(self._data)

    return LM()


def test_init(lm):
    assert isinstance(lm._dtb, DTB)


def test_reset(qtbot):
    class LM(DtbListModel):
        _data = ["a"]

        def rowCount(self, parent=QModelIndex()):
            return len(self._data)

        _reset = MagicMock()
        _after_reset = MagicMock()

    l = LM()
    assert l._reset.called
    assert l._after_reset.called
    with qtbot.waitSignals([l.modelAboutToBeReset, l.modelReset]):
        l.reset()


def test_flags(lm):
    assert int(lm.flags(lm.index(0, 0))) == 128 + 35
    assert lm.flags(lm.index(99, 99)) is None


def test_roleNames(lm):
    Bla = Qt.UserRole + 1
    lm._roleNames = lambda: {Bla: QByteArray(b"bla")}
    assert Qt.DisplayRole in lm.roleNames()
    assert Bla in lm.roleNames()
    assert lm.roleNames()[Bla] == QByteArray(b"bla")


def test_insertRows(lm, qtbot):
    lm._insertRows = MagicMock()

    def params(index, debut, fin):
        assert index.row() == -1
        assert index.column() == -1
        assert debut == 3
        assert fin == 5
        return True

    with qtbot.waitSignals(
        [lm.rowsAboutToBeInserted, lm.rowsInserted],
        check_params_cbs=[params, lambda x, y, z: True],
    ):
        assert lm.insertRows(3, 2)
    assert lm._insertRows.called
    assert lm._insertRows.call_args == call(3, 2)


def test_removeRows(lm, qtbot):
    lm._removeRows = MagicMock()

    def params(index, debut, fin):
        assert index.row() == -1
        assert index.column() == -1
        assert debut == 3
        assert fin == 5
        return True

    with qtbot.waitSignals(
        [lm.rowsAboutToBeRemoved, lm.rowsRemoved],
        check_params_cbs=[params, lambda x, y, z: True],
    ):
        assert lm.removeRows(3, 2)
    assert lm._removeRows.called
    assert lm._removeRows.call_args == call(3, 2)


def test_moveRows(lm, qtbot):
    lm._data = [0, 1, 2, 3, 4, 5, 6]
    lm._moveRows = MagicMock()
    a = QModelIndex()
    b = QModelIndex()

    def params(*args):
        assert args == (a, 1, 3, b, 5)
        return True

    with qtbot.waitSignals(
        [lm.rowsAboutToBeMoved, lm.rowsMoved],
        check_params_cbs=[params, lambda v, w, x, y, z: True],
    ):
        assert lm.moveRows(a, 1, 2, b, 5)
    assert lm._moveRows.called
    assert lm._moveRows.call_args == call(1, 2, 5)


def test_move_row_false(lm):
    lm._data = [1, 2, 3]
    assert not lm.moveRows(QModelIndex(), 1, 1, QModelIndex, 1)  # srouce = dest
    assert not lm.moveRows(QModelIndex(), 1, 1, QModelIndex, 2)  # srouce + 1 = dest
    assert not lm.moveRows(QModelIndex(), 1, 1, QModelIndex, 4)  # dest > count + 1
    assert not lm.moveRows(QModelIndex(), 2, 1, QModelIndex, 2)  # srouce > count - 1


@pytest.mark.parametrize(
    "method, general, inp, res",
    [
        ("insertRow", "insertRows", [2], [2, 0]),
        ("append", "insertRows", [], [3, 0]),
        ("removeRow", "removeRows", [2], [2, 0, QModelIndex()]),
        ("remove", "removeRows", [2], [2, 0, QModelIndex()]),
        ("moveRow", "moveRows", [1, 3], [QModelIndex(), 1, 0, QModelIndex(), 3]),
    ],
)
def test_shortcuts(method, general, inp, res, lm):
    lm._data = [1, 2, 3]  # pour rowcount
    setattr(lm, general, MagicMock())
    getattr(lm, method)(*inp)
    assert getattr(lm, general).call_args == call(*res)
