import pytest
from PySide2.QtCore import Qt
from fixtures import check_super_init
from package.database.factory import f_additionSection
from package.operations.api import match, convert_addition, create_operation
from package.operations.models import OperationModel, AdditionModel


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
    a = OperationModel()
    a.params = f_additionSection(string="9+8", td=True)
    return a


@pytest.fixture
def ta(ddbr):
    a = AdditionModel()
    a.params = f_additionSection(string="9+8", td=True)
    return a


class TestOperationModel:
    def test_base_init(self, to, qtmodeltester, qtbot):
        assert check_super_init(
            "package.list_models.QAbstractListModel", OperationModel
        )
        qtmodeltester.check(to)

        # signal tester par le fait que les valeurs sont updatées
        assert to.datas == ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
        assert to.rows == 4
        assert to.columns == 3
        assert to.cursor == 0

        with qtbot.waitSignal(to.cursorChanged):
            to.cursor = 1
        assert to.cursor == 1

    def test_autoMoveNext(self, to):
        to.auto_move_next = lambda x: x
        to.autoMoveNext(99)
        assert to.cursor == 99

    def test_ReadOnly(self, to):
        to.editables = [1, 6]
        assert to.readOnly(2)
        assert not to.readOnly(6)

    def test_data(self, to):
        # valid index
        assert to.data(to.index(5, 0), Qt.DisplayRole) == "9"
        # unvalid index
        assert to.data(to.index(99, 0), Qt.DisplayRole) is None
        # unvalid role
        assert to.data(to.index(5, 0), 999999) is None

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
        "string, res",
        [
            ("9+8", [1, 10, 11]),
            ("1+2", [7]),
            ("345+289", [1, 2, 13, 14, 15]),
            ("1+2+3", [9]),
        ],
    )
    def test_get_editables(self, string, res):
        a = AdditionModel()
        a.params = f_additionSection(string=string, td=True)
        assert a.editables == res

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
        ],
    )
    def test_move_cursor(self, index, key, res):
        a = AdditionModel()
        a.cursor = 99  # controle pas modif, 0 pourrait être faux
        a.params = f_additionSection(string="254+141", td=True)
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        assert a.move_cursor(index, key) == res
