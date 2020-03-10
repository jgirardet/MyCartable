from decimal import Decimal

import pytest
from PySide2.QtCore import Qt
from fixtures import check_super_init
from package.database.factory import f_additionSection
from package.operations.api import (
    match,
    convert_addition,
    create_operation,
    DecimalLitteral,
    convert_soustraction,
)
from package.operations.models import OperationModel, AdditionModel
from pony.orm import db_session


class TestDecimal:
    @pytest.mark.parametrize(
        "inp, value, v_int, v_dec, l_int, l_dec",
        [
            ("1", "1", Decimal(1), Decimal(0), 1, 0),
            ("12", "12", Decimal(12), Decimal(0), 2, 0),
            ("0.3", "0.3", Decimal(0), Decimal("0.3"), 1, 1),
            ("0,3", "0.3", Decimal(0), Decimal("0.3"), 1, 1),
            ("12,311", "12.311", Decimal(12), Decimal("0.311"), 2, 3),
            ("0.10", "0.10", Decimal(0), Decimal("0.10"), 1, 2),
        ],
    )
    def test_init(self, inp, value, v_int, v_dec, l_int, l_dec):
        a = DecimalLitteral(inp)
        assert a == Decimal(value)
        assert a.int == v_int
        assert a.dec == v_dec
        assert a.l_int == l_int
        assert a.l_dec == l_dec

    @pytest.mark.parametrize("value, res", [("1", True), ("1.1", False)])
    def test_is_int(self, value, res):
        a = DecimalLitteral(value)
        assert a.is_int() == res

    @pytest.mark.parametrize(
        "value, size, apres, res",
        [
            ("1", 3, 0, ["", "", "1"]),
            ("1", 4, 0, ["", "", "", "1"]),
            ("1", 4, 1, ["", "1", "", ""]),
            ("1", 8, 3, ["", "", "", "1", "", "", "", "",]),
            ("12", 3, 0, ["", "1", "2"]),
            ("1.1", 3, 0, ["1", ",", "1"]),
            ("1,1", 3, 0, ["1", ",", "1"]),
            ("211,2", 10, 4, ["", "", "2", "1", "1", ",", "2", "", "", ""]),
            ("11,20", 10, 4, ["", "", "", "1", "1", ",", "2", "0", "", ""]),
            ("0,20", 6, 3, ["", "0", ",", "2", "0", ""]),
        ],
    )
    def test_to_string_list_addition(self, value, size, apres, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_addition(size, apres_virgule=apres) == res

    @pytest.mark.parametrize(
        "value, size, ligne,  apres, res",
        [
            ("1", 2, 0, 0, ["", "", "1"]),
            ("1", 2, 1, 0, ["-", "1", "",]),
            ("11", 3, 0, 0, ["", "", "1", "", "1"]),
            ("111", 3, 0, 0, ["", "", "1", "", "1", "", "1"]),
            ("11", 3, 1, 0, ["-", "1", "", "1", ""]),
            ("111", 3, 1, 0, ["-", "1", "", "1", "", "1", ""]),
            ("3", 5, 1, 0, ["-", "", "", "3", ""])
            # ("1", 2, 1, 0, ["-", "1"]),
            # ("1", 5, 0, 1, ["", "1", ",", "", ""]),
            # ("1", 4, 0, ["", "", "", "1"]),
            # ("1", 5, 1, ["", "1", "", "", ""]),
            # ("1", 8, 3, ["", "1", "", "", "", "", "", "", ""]),
            # ("12", 4, 0, ["", "1", "", "2"]),
            # ("1.1", 5, 1, ["", "1", ",", "", "1"]),
            # ("1,12", 6, 0, ["", "1", ",", "", "1", "", "2"]),
            # (
            #     "211,2",
            #     15,
            #     4,
            #     ["", "2", "", "1", "", "1", ",", "", "2", "", "", "", "", "", "",],
            # ),
            # ("11,20", 13, 4, ["", "1", "", "1", ",", "", "2", "", "0", "", "", "", ""]),
            # ("0,20", 10, 3, ["", "", "0", ",", "", "2", "", "0", "", ""]),
        ],
    )
    def test_to_string_list_soustraction(self, value, size, ligne, apres, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_soustraction(size, ligne, apres_virgule=apres) == res


class TestOperation:
    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", ("+", ["1", "2"])),
            ("1.2+2.3", ("+", ["1.2", "2.3"])),
            ("1,2+2,3", ("+", ["1,2", "2,3"])),
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
            (["1", "2"], (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),
            (
                ["1,2", "2,3"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                        "+",
                        "2",
                        ",",
                        "3",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["1,2", "33,33", "444,444"],
                (
                    5,
                    8,
                    4,
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
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                        "",
                        "",
                        "+",
                        "",
                        "3",
                        "3",
                        ",",
                        "3",
                        "3",
                        "",
                        "+",
                        "4",
                        "4",
                        "4",
                        ",",
                        "4",
                        "4",
                        "4",
                        "",
                        "",
                        "",
                        "",
                        ",",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["1.2", "2.3"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                        "+",
                        "2",
                        ",",
                        "3",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["9", "8"],
                (4, 3, 0, ["", "", "", "", "", "9", "+", "", "8", "", "", ""]),
            ),
            (["1", "2", "3"], (5, 2, 0, ["", "", "", "1", "+", "2", "+", "3", "", ""])),
            (
                ["1", "2,1"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        "",
                        "",
                        "+",
                        "2",
                        ",",
                        "1",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["1", "25", "348", "4789"],
                (
                    6,
                    5,
                    0,
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
            (["2", "1"], (3, 3, 0, ["", "", "2", "-", "1", "", "", "", ""])),
            (
                ["22", "11"],
                (
                    3,
                    5,
                    0,
                    ["", "", "2", "", "2", "-", "1", "", "1", "", "", "", "", "", "",],
                ),
            ),
            (
                ["222", "111"],
                (
                    3,
                    7,
                    0,
                    [
                        "",
                        "",
                        "2",
                        "",
                        "2",
                        "",
                        "2",
                        "-",
                        "1",
                        "",
                        "1",
                        "",
                        "1",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["15", "3"],
                (
                    3,
                    5,
                    0,
                    ["", "", "1", "", "5", "-", "", "", "3", "", "", "", "", "", "",],
                ),
            ),
        ],
    )
    def test_convert_soustraction(self, string, res):
        assert convert_soustraction(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # addition
            (" 1+ 2 ", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # space
            ("1A2", None),  # no match
            ("2-1", (3, 3, 0, ["", "", "2", "-", "1", "", "", "", ""])),  # soustraction
        ],
    )
    def test_create_operations(self, string, res):
        assert create_operation(string) == res


@pytest.fixture
def to(ddbr):
    x = f_additionSection(string="9+8")
    from package.database_object import DatabaseObject

    OperationModel.ddb = DatabaseObject(ddbr)
    a = OperationModel()
    a.sectionId = x.id
    return a


@pytest.fixture
def ta(ddbr):
    x = f_additionSection(string="9+8")
    from package.database_object import DatabaseObject

    OperationModel.ddb = DatabaseObject(ddbr)
    a = AdditionModel()
    a.sectionId = x.id
    return a


class TestOperationModel:
    def test_base_init(self, qtmodeltester, qtbot, ddbr):
        from package.database_object import DatabaseObject

        OperationModel.ddb = DatabaseObject(ddbr)
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
        from package.database_object import DatabaseObject

        OperationModel.ddb = DatabaseObject(ddbr)
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
        assert op.virgule == 0

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

    def test_setData_changerecents(self, to, qtbot):

        with qtbot.waitSignal(to.ddb.recentsModelChanged):
            to.setData(to.index(11, 0), 5, Qt.EditRole)  # doit retourner True

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
        assert to.editables == {1, 10, 11}


class TestAdditionModel:
    @pytest.mark.parametrize(
        "index,res", [(1, 13), (2, 14), (13, 13), (14, 1), (15, 2),],
    )
    def test_automove_next(self, ta, index, res):
        a = AdditionModel()
        a.params = f_additionSection(string="254+141", td=True)
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        assert a.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res", [(23, 4), (4, 22), (22, 2), (2, 20), (20, 1), (1, 19)],
    )
    def test_automove_next_virgule(self, ta, index, res):
        a = AdditionModel()
        a.params = f_additionSection(string="2,54+14,1", td=True)
        # ['', '', '', '', '', '', '', '', '2', ',', '5', '4', '+', '1', '4', ',', '1', '', '', '', '', '', '', ''] 6x4
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
    def test_move_cursor(self, ta, index, key, res):
        x = f_additionSection(string="254+141")
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        ta.sectionId = x.id
        ta.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert ta.move_cursor(index, key) == res

    @pytest.mark.parametrize(
        "index,key,res",
        [
            (1, Qt.Key_Up, 99),
            (2, Qt.Key_Up, 99),
            (4, Qt.Key_Up, 99),
            (19, Qt.Key_Up, 1),
            (20, Qt.Key_Up, 2),
            (22, Qt.Key_Up, 4),
            (23, Qt.Key_Up, 4),
            (1, Qt.Key_Down, 19),
            (2, Qt.Key_Down, 20),
            (4, Qt.Key_Down, 22),
            (19, Qt.Key_Down, 99),
            (20, Qt.Key_Down, 99),
            (22, Qt.Key_Down, 99),
            (23, Qt.Key_Down, 99),
            (1, Qt.Key_Left, 99),
            (2, Qt.Key_Left, 1),
            (4, Qt.Key_Left, 2),
            (19, Qt.Key_Left, 99),
            (20, Qt.Key_Left, 19),
            (22, Qt.Key_Left, 20),
            (23, Qt.Key_Left, 22),
            (1, Qt.Key_Right, 2),
            (2, Qt.Key_Right, 4),
            (4, Qt.Key_Right, 99),
            (19, Qt.Key_Right, 20),
            (20, Qt.Key_Right, 22),
            (22, Qt.Key_Right, 23),
            (23, Qt.Key_Right, 99),
            (22, Qt.Key_X, 99),
        ],
    )
    def test_move_cursor_virgule(self, ta, index, key, res):
        x = f_additionSection(string="2,54+14,1")
        ta.sectionId = x.id
        ta.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert ta.move_cursor(index, key) == res

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
