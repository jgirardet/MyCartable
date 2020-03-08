import pytest
from PySide2.QtCore import Qt
from fixtures import check_super_init
from package.database.factory import f_additionSection
from package.operations.api import match, convert_addition, create_operation
from package.operations.models import OperationModel, AdditionModel
from pony.orm import db_session


class TestAddition:
    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", ("+", ["1", "2"])),
            ("1+2+3", ("+", ["1", "2", "3"])),
            ("111+2222+33333", ("+", ["111", "2222", "33333"])),
            ("111-2222-33333", ("-", ["111", "2222", "33333"])),
            ("111*2222*33333", ("*", ["111", "2222", "33333"])),
            ("111/2222/33333", ("/", ["111", "2222", "33333"])),
        ],
    )
    def test_match(self, string, res):
        assert match(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            (["1", "2"], (4, 2, ["", "", "", "1", "+", "2", "", ""])),
            (["9", "8"], (4, 3, ["", "", "", "", "", "9", "+", "", "8", "", "", ""])),
            (["1", "2", "3"], (5, 2, ["", "", "", "1", "+", "2", "+", "3", "", ""])),
            (
                ["1", "25", "348", "4789"],
                (
                    6,
                    5,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        "+",
                        "",
                        "",
                        "2",
                        "5",
                        "+",
                        "",
                        "3",
                        "4",
                        "8",
                        "+",
                        "4",
                        "7",
                        "8",
                        "9",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
        ],
    )
    def test_convert_addition(self, string, res):
        assert convert_addition(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", (4, 2, ["", "", "", "1", "+", "2", "", ""])),  # normal
            (" 1+ 2 ", (4, 2, ["", "", "", "1", "+", "2", "", ""])),  # space
            ("1A2", None),  # no match
            ("9+8", (4, 3, ["", "", "", "", "", "9", "+", "", "8", "", "", ""])),
        ],
    )
    def test_create_operations(self, string, res):
        assert create_operation(string) == res


@pytest.fixture
def to(ddbr):
    x = f_additionSection(string="9+8")
    a = OperationModel()
    a.sectionId = x.id
    return a


@pytest.fixture
def ta(ddbr):
    x = f_additionSection(string="9+8")
    a = AdditionModel()
    a.sectionId = x.id
    return a


class TestOperationModel:
    def test_base_init(self, qtmodeltester, qtbot):
        op = OperationModel()

        assert check_super_init(
            "package.list_models.QAbstractListModel", OperationModel
        )
        qtmodeltester.check(op)
        assert op.datas == []
        assert op.rows == 0
        assert op.columns == 0
        assert op.cursor == 0
        assert op._sectionId is None

    def test_load_params(self, ddbr, qtbot):
        op = OperationModel()
        op.sectionId = 1
        assert op.sectionId is None

        td = f_additionSection(string="9+8", td=True)

        with qtbot.waitSignal(op.sectionIdChanged):
            op.sectionId = 1

        assert op.params == td
        assert op.datas == ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
        assert op.rows == 4
        assert op.columns == 3
        assert op.sectionId == 1

    def test_cursor(self, to, qtbot):

        with qtbot.waitSignal(to.cursorChanged):
            to.cursor = 1
        assert to.cursor == 1

    def test_cursor_no_update_and_no_emit_if_unchanged(self, to, qtbot):

        to.cursor = 1
        with qtbot.assertNotEmitted(to.cursorChanged):
            to.cursor = 1
        assert to.cursor == 1

    def test_autoMoveNext(self, to):
        to.autoMoveNext(99)
        assert to.cursor == 99

    def test_data(self, to):
        # valid index
        assert to.data(to.index(5, 0), Qt.DisplayRole) == "9"
        # unvalid index
        assert to.data(to.index(99, 0), Qt.DisplayRole) is None
        # unvalid role
        assert to.data(to.index(5, 0), 999999) is None

    def test_flags(self, to):
        to.flags(to.index(99, 99)) == Qt.ItemIsDropEnabled

    def test_setData(self, to):
        assert to.setData(to.index(11, 0), 5, Qt.EditRole)  # doit retourner True
        with db_session:
            assert to.db.Section[1].datas[11] == 5
            assert to.datas[11] == 5

        assert not to.setData(to.index(99, 0), 5, Qt.EditRole)
        assert not to.setData(to.index(11, 0), 8, Qt.DisplayRole)
        with db_session:
            assert to.db.Section[1].datas[11] == 5  # pas de modif

    def test_isIResultline(self, to):
        assert to.isResultLine(99) is False

    def test_isRetenueline(self, to):
        assert to.isRetenueLine(99) is False

    def test_move_cursor(self, to):
        c = to.cursor
        to.moveCursor(13, 927)
        assert c == to.cursor

    def test_ReadOnly(self, to):
        to.editables = [1, 6]
        assert to.readOnly(2)
        assert not to.readOnly(6)

    def test_rowCount(self, to):
        assert to.rowCount() == 12

    def test_get_editables(self, to):
        assert to.editables == []


class TestadditionModel:
    @pytest.mark.parametrize(
        "index,res", [(1, 13), (2, 14), (13, 13), (14, 1), (15, 2),],
    )
    def test_automove_text(self, ta, index, res):
        a = AdditionModel()
        a.params = f_additionSection(string="254+141", td=True)
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        assert a.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,key,res",
        [
            (1, Qt.Key_Up, 99),
            (2, Qt.Key_Up, 99),
            (13, Qt.Key_Up, 1),
            (14, Qt.Key_Up, 2),
            (15, Qt.Key_Up, 2),
            (1, Qt.Key_Down, 13),
            (2, Qt.Key_Down, 14),
            (13, Qt.Key_Down, 99),
            (14, Qt.Key_Down, 99),
            (15, Qt.Key_Down, 99),
            (1, Qt.Key_Left, 99),
            (2, Qt.Key_Left, 1),
            (13, Qt.Key_Left, 99),
            (14, Qt.Key_Left, 13),
            (15, Qt.Key_Left, 14),
            (1, Qt.Key_Right, 2),
            (2, Qt.Key_Right, 99),
            (13, Qt.Key_Right, 14),
            (14, Qt.Key_Right, 15),
            (15, Qt.Key_Right, 99),
            (15, Qt.Key_X, 99),
        ],
    )
    def test_move_cursor(self, index, key, res):
        x = f_additionSection(string="254+141")
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        a = AdditionModel()
        a.sectionId = x.id
        a.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert a.move_cursor(index, key) == res

    def test_isMiddleLinee(self, ta):
        for i in range(3, 9):
            assert ta.isMiddleLine(i)
        for i in range(0, 3):
            assert not ta.isMiddleLine(i)
        for i in range(9, 12):
            assert not ta.isMiddleLine(i)

    def test_is_result_line(self, ta):
        for i in range(9, 12):
            assert ta.isResultLine(i)
        for i in range(0, 9):
            assert not ta.isResultLine(i)

    def test_is_retenue_line(self, ta):
        for i in range(0, 3):
            assert ta.isRetenueLine(i)
        for i in range(3, 12):
            assert not ta.isRetenueLine(i)
