import uuid
from decimal import Decimal
from unittest.mock import patch, call

import pytest
from PySide2.QtCore import Qt, Signal
from fixtures import check_super_init, check_args, check_is_range
from factory import (
    f_additionSection,
    f_soustractionSection,
    f_multiplicationSection,
    f_divisionSection,
)
from package.operations.api import (
    match,
    convert_addition,
    create_operation,
    DecimalLitteral,
    convert_soustraction,
    convert_multiplication,
    convert_division,
)
from package.operations.models import (
    OperationModel,
    AdditionModel,
    SoustractionModel,
    MultiplicationModel,
    DivisionModel,
)
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
            ("1", 2, 0, 0, ["", "", "1", ""]),
            ("11", 3, 0, 0, ["", "", "1", "", "", "1", "",]),
            ("111", 3, 0, 0, ["", "", "1", "", "", "1", "", "", "1", "",]),
            ("1", 2, 1, 0, ["-", "", "1", "",]),
            ("11", 3, 1, 0, ["-", "", "1", "", "", "1", ""]),
            ("111", 3, 1, 0, ["-", "", "1", "", "", "1", "", "", "1", ""]),
            ("3", 6, 1, 0, ["-", "", "", "", "3", ""]),
            ("1", 8, 0, 1, ["", "", "1", "", ",", "", "0", ""]),
            ("1,1", 3, 0, 1, ["", "", "1", "", ",", "", "1", ""]),
            (
                "11,11",
                3,
                0,
                1,
                ["", "", "1", "", "", "1", "", ",", "", "1", "", "", "1", ""],
            ),
            ("1,1", 8, 1, 1, ["-", "", "1", "", ",", "", "1", ""]),
            ("1,1", 11, 1, 2, ["-", "", "1", "", ",", "", "1", "", "", "0", ""]),
            ("1,1", 12, 1, 2, ["-", "", "", "1", "", ",", "", "1", "", "", "0", ""]),
            (
                "11,11",
                14,
                1,
                2,
                ["-", "", "1", "", "", "1", "", ",", "", "1", "", "", "1", ""],
            ),
            (
                "11,11",
                17,
                1,
                2,
                ["-", "", "", "", "", "1", "", "", "1",]
                + ["", ",", "", "1", "", "", "1", "",],
            ),
            (
                "11,11",
                17,
                1,
                3,
                ["-", "", "1", "", "", "1", "", ",", "",]
                + ["1", "", "", "1", "", "", "0", "",],
            ),
            ("0,20", 10, 0, 2, ["", "", "0", "", ",", "", "2", "", "", "0", ""]),
            ("0,20", 10, 1, 2, ["-", "", "0", "", ",", "", "2", "", "", "0", ""]),
            (
                "0,20",
                14,
                1,
                3,
                ["-", "", "0", "", ",", "", "2", "", "", "0", "", "", "0", ""],
            ),
            ("0,2", 10, 0, 2, ["", "", "0", "", ",", "", "2", "", "", "0", ""]),
            (
                "0,20",
                14,
                0,
                3,
                ["", "", "0", "", ",", "", "2", "", "", "0", "", "", "0", ""],
            ),
            ("20", 11, 0, 1, ["", "", "2", "", "", "0", "", ",", "", "0", ""]),
            ("20", 11, 1, 1, ["-", "", "2", "", "", "0", "", ",", "", "0", ""]),
        ],
    )
    def test_to_string_list_soustraction(self, value, size, ligne, apres, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_soustraction(size, ligne, apres_virgule=apres) == res

    @pytest.mark.parametrize(
        "value, size, res",
        [
            ("1", 3, ["", "", "1"]),
            ("1", 4, ["", "", "", "1"]),
            ("1", 4, ["", "", "", "1"]),
            ("1", 8, ["", "", "", "", "", "", "", "1",]),
            ("12", 3, ["", "1", "2"]),
            ("1.1", 3, ["1", ",", "1"]),
            ("1,1", 3, ["1", ",", "1"]),
            ("211,2", 10, ["", "", "", "", "", "2", "1", "1", ",", "2"]),
            ("11,20", 10, ["", "", "", "", "", "1", "1", ",", "2", "0"]),
            ("0,20", 6, ["", "", "0", ",", "2", "0"]),
        ],
    )
    def test_to_string_list_multiplication(self, value, size, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_multiplication(size) == res

    @pytest.mark.parametrize(
        "value, size, res",
        [
            ("1", 3, ["", "1", ""]),
            ("1", 9, ["", "1", ""] + [""] * 6),
            ("12", 9, ["", "1", "", "", "2", ""] + [""] * 3),
            ("1,2", 9, ["", "1,", "", "", "2", ""] + [""] * 3),
            (
                "211,2",
                20,
                ["", "2", "", "", "1", "", "", "1,", "", "", "2", ""] + [""] * 8,
            ),
        ],
    )
    def test_to_string_list_division(self, value, size, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_division(size) == res


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
                    ["", "", "", "", "", "1", ",", "2",]
                    + ["+", "2", ",", "3", "", "", ",", "",],
                ),
            ),
            (
                ["1,2", "33,33", "444,444"],
                (
                    5,
                    8,
                    4,
                    ["", "", "", "", "", "", "", "",]
                    + ["", "", "", "1", ",", "2", "", "",]
                    + ["+", "", "3", "3", ",", "3", "3", "",]
                    + ["+", "4", "4", "4", ",", "4", "4", "4",]
                    + ["", "", "", "", ",", "", "", "",],
                ),
            ),
            (
                ["1.2", "2.3"],
                (
                    4,
                    4,
                    2,
                    ["", "", "", "", "", "1", ",", "2",]
                    + ["+", "2", ",", "3", "", "", ",", "",],
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
                    ["", "", "", "", "", "1", "", "",]
                    + ["+", "2", ",", "1", "", "", ",", "",],
                ),
            ),
            (
                ["1", "25", "348", "4789"],
                (
                    6,
                    5,
                    0,
                    ["", "", "", "", "", "", "", "", "", "1",]
                    + ["+", "", "", "2", "5",]
                    + ["+", "", "3", "4", "8",]
                    + ["+", "4", "7", "8", "9",]
                    + ["", "", "", "", "",],
                ),
            ),
        ],
    )
    def test_convert_addition(self, string, res):
        assert convert_addition(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            (
                ["2", "1"],
                (3, 4, 0, ["", "", "2", "", "-", "", "1", "", "", "", "", ""]),
            ),
            (
                ["22", "11"],
                (
                    3,
                    7,
                    0,
                    [
                        "",
                        "",
                        "2",
                        "",
                        "",
                        "2",
                        "",
                        "-",
                        "",
                        "1",
                        "",
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
                ["222", "111"],
                (
                    3,
                    10,
                    0,
                    ["", "", "2", "", "", "2", "", "", "2", "",]
                    + ["-", "", "1", "", "", "1", "", "", "1",]
                    + ["", "", "", "", "", "", "", "", "", "", "",],
                ),
            ),
            (
                ["15", "3"],
                (
                    3,
                    7,
                    0,
                    ["", "", "1", "", "", "5", "", "-",]
                    + ["", "", "", "", "3",]
                    + ["", "", "", "", "", "", "", "",],
                ),
            ),
            (
                ["20", "0,2"],
                (
                    3,
                    11,
                    7,
                    ["", "", "2", "", "", "0", "", ",", "", "0", "",]
                    + ["-", "", "", "", "", "0", "", ",", "", "2", "",]
                    + ["", "", "", "", "", "", "", ",", "", "", "",],
                ),
            ),
            (
                ["2,2", "1,1"],
                (
                    3,
                    8,
                    4,
                    ["", "", "2", "", ",", "", "2", "",]
                    + ["-", "", "1", "", ",", "", "1", "",]
                    + ["", "", "", "", ",", "", "", "",],
                ),
            ),
        ],
    )
    def test_convert_soustraction(self, string, res):
        assert convert_soustraction(string) == res

    @pytest.mark.parametrize(
        "numbers, res",
        [
            (["2", "1"], (4, 2, 0, ["", "", "", "2", "x", "1", "", ""])),
            (
                ["6", "2"],
                (4, 3, 0, ["", "", "", "", "", "6", "x", "", "2", "", "", ""]),
            ),
            (
                ["6", "21"],
                (4, 4, 0, [""] * 4 + ["", "", "2", "1", "x", "", "", "6"] + [""] * 4),
            ),
            (
                ["21", "6"],
                (4, 4, 0, [""] * 4 + ["", "", "2", "1", "x", "", "", "6"] + [""] * 4),
            ),
            (
                ["331", "254"],  # res = 84074
                (
                    10,
                    6,
                    0,
                    [""] * 3 * 6
                    + ["", "", "", "3", "3", "1", "x", "", "", "2", "5", "4"]
                    + [""] * 1 * 6
                    + (["+"] + ([""] * 5)) * 3
                    + [""] * 1 * 6,
                ),
            ),
            (
                ["1,1", "5"],  #
                (
                    4,
                    4,
                    1,
                    [""] * 4
                    + ["", "1", ",", "1", "x", "", "", "5"]
                    + ["", "", "", "",],
                ),
            ),
            (
                ["5", "1,1"],  #
                (
                    4,
                    4,
                    1,
                    [""] * 4
                    + ["", "1", ",", "1", "x", "", "", "5"]
                    + ["", "", "", "",],
                ),
            ),
            (
                ["23,3", "5,1234"],  # 119,37522
                (
                    10,
                    10,
                    1,
                    [""] * 10 * 3
                    + [""] * 4
                    + list("5,1234")
                    + ["x"]
                    + [""] * 5
                    + list("23,3")
                    + [""] * 10  # permiere
                    + (["+"] + [""] * 9) * 3  # 2 autres + retenues
                    + [""] * 10,  # res
                ),
            ),
            (
                ["23", "23"],  # 119,37522
                (
                    8,
                    4,
                    0,
                    [""] * 4 * 2
                    + [""] * 2
                    + list("23")
                    + ["x"]
                    + [""]
                    + list("23")
                    + [""] * 4  # permiere
                    + (["+"] + [""] * 3) * 2  # 21autres + retenues
                    + [""] * 4,  # res
                ),
            ),
        ],
    )
    def test_convert_multiplication(self, numbers, res):
        assert convert_multiplication(numbers) == res

    @pytest.mark.parametrize(
        "numbers, res",
        [
            (
                ["23", "5"],  # base
                (
                    5,
                    9,
                    0,
                    {
                        "dividende": "23",
                        "diviseur": "5",
                        "datas": ["", "2", "", "", "3", ""] + [""] * 39,
                    },
                ),
            ),
            (
                ["5", "4"],  # base 1,25
                (
                    7,
                    12,
                    0,
                    {
                        "dividende": "5",
                        "diviseur": "4",
                        "datas": ["", "5"] + [""] * 82,
                    },
                ),
            ),
            (
                ["24,3", "3"],  # base
                (
                    5,
                    9,
                    0,
                    {
                        "dividende": "24.3",
                        "diviseur": "3",
                        "datas": ["", "2", "", "", "4,", "", "", "3", "",] + [""] * 36,
                    },
                ),
            ),
            (
                ["10", "3"],  # division infinite
                (
                    17,
                    27,
                    0,
                    {
                        "dividende": "10",
                        "diviseur": "3",
                        "datas": ["", "1", "", "", "0", ""] + [""] * 453,
                    },
                ),
            ),
            (
                ["3454367", "45"],  # 76763,711111grand nombre et division infinite
                (
                    17,
                    27,
                    0,
                    {
                        "dividende": "3454367",
                        "diviseur": "45",
                        "datas": ["", "3", "", "", "4", "", "", "5", "", "", "4", ""]
                        + ["", "3", "", "", "6", "", "", "7", ""]
                        + [""] * 438,
                    },
                ),
            ),
        ],
    )
    def test_convert_division(self, numbers, res):
        assert convert_division(numbers) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # addition
            (" 1+ 2 ", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # space
            ("1A2", None),  # no match
            (
                "2-1",
                (3, 4, 0, ["", "", "2", "", "-", "", "1", "", "", "", "", ""]),
            ),  # soustraction
            ("1*2", (4, 2, 0, ["", "", "", "2", "x", "1", "", ""])),  # mul
            (
                "2/1",
                (
                    3,
                    6,
                    0,
                    {
                        "dividende": "2",
                        "diviseur": "1",
                        "datas": ["", "2", "", "", "", ""] + [""] * 12,
                    },
                ),
            ),
        ],
    )
    def test_create_operations(self, string, res):
        assert create_operation(string) == res


@pytest.fixture
def to(dao):
    x = f_additionSection(string="9+8")
    OperationModel.ddb = dao
    a = OperationModel()
    a.sectionId = x.id
    return a


@pytest.fixture
def ta():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class Mock(AdditionModel):
        def __call__(self, string):
            rows, columns, virgule, datas = create_operation(string)
            self.params["rows"] = rows
            self.params["columns"] = columns
            self.params["virgule"] = virgule
            self.params["datas"] = datas
            self.params["size"] = self.rows * self.columns

    Mock.ddb = Dbo()
    a = Mock()
    return a


class TestOperationModel:
    def test_base_init(self, qtmodeltester, qtbot, ddbr, uim):
        from package.database_object import DatabaseObject

        OperationModel.ddb = DatabaseObject(ddbr, uim)
        op = OperationModel()

        assert check_super_init(
            "package.operations.models.QAbstractListModel", OperationModel
        )
        qtmodeltester.check(op)
        assert op.datas == []
        assert op.rows == 0
        assert op.columns == 0
        assert op.cursor == 0
        assert op._sectionId is None

    def test_load_params(self, ddbr, qtbot, uim):
        from package.database_object import DatabaseObject

        OperationModel.ddb = DatabaseObject(ddbr, uim)
        op = OperationModel()
        op.sectionId = str(uuid.uuid4())
        assert op.sectionId is None, "should not be set if not in databse"

        td = f_additionSection(string="9+8", td=True)

        with qtbot.waitSignal(op.sectionIdChanged):
            op.sectionId = td["id"]

        assert op.params == td
        assert op.datas == ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
        assert op.rows == 4
        assert op.columns == 3
        assert op.sectionId == td["id"]
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

    def test_flags(self):
        x = OperationModel()
        x.rowCount = lambda x: 1
        assert int(x.flags(x.index(0, 0))) == 128 + 35
        assert x.flags(x.index(99, 99)) is None

    def test_setData(self, to):
        assert to.setData(to.index(11, 0), "5", Qt.EditRole)  # doit retourner True
        with db_session:
            un = str(to.db.Section.select().first().id)
        with db_session:
            assert to.db.Section[un].datas[11] == "5"
            assert to.datas[11] == "5"

        assert not to.setData(to.index(99, 0), "5", Qt.EditRole)
        assert not to.setData(to.index(11, 0), 8, Qt.DisplayRole)
        with db_session:
            assert to.db.Section[un].datas[11] == "5"  # pas de modif

    def test_setData_changerecents(self, to, qtbot):
        with qtbot.waitSignal(to.ddb.recentsModelChanged):
            to.setData(to.index(11, 0), "5", Qt.EditRole)  # doit retourner True

    def test_setData_automovenext(self, to, qtbot):
        with patch("package.operations.models.OperationModel.autoMoveNext"):
            assert to.setData(to.index(11, 0), "5", Qt.EditRole)  # doit retourner True
            assert to.autoMoveNext.call_args_list == [call(11)]
            to.autoMoveNext.call_args_list = []

            assert to.setData(to.index(11, 0), "5,", Qt.EditRole)  # doit retourner True
            assert to.autoMoveNext.call_args_list == []  # pas de modif
            to.autoMoveNext.call_args_list = []

            assert to.setData(
                to.index(11, 0), "5,", Qt.EditRole, move=False
            )  # doit retourner True
            assert to.autoMoveNext.call_args_list == []  # pas de modif

    def test_isIResultline(self, to):
        assert to.isResultLine(99) is False

    def test_isRetenueline(self, to):
        assert to.isRetenueLine(99) is False

    def test_getInitialPosition(self, to):
        assert to.getInitialPosition() == 11

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

    def test_isMiddleLinee(self, ta):
        ta("9+8")
        check_is_range(ta, "isMiddleLine", range(3, 9))

    def test_isMembreLine(self, ta):
        ta("9+8")
        check_is_range(ta, "isMembreLine", range(3, 9))


class TestAdditionModel:
    @pytest.mark.parametrize(
        "index,res", [(1, 13), (2, 14), (13, 13), (14, 1), (15, 2),],
    )
    def test_automove_next(self, ta, index, res):
        # a = AdditionModel()
        ta("254+141")
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        assert ta.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res", [(23, 4), (4, 22), (22, 2), (2, 20), (20, 1), (1, 19)],
    )
    def test_automove_next_virgule(self, ta, index, res):
        ta("2,54+14,1")
        # ['', '', '', '', '', '', '', '', '2', ',', '5', '4', '+', '1', '4', ',', '1', '', '', '', '', '', '', ''] 6x4
        assert ta.auto_move_next(index) == res

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
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        ta("254+141")
        ta.editables = {1, 2, 13, 14, 15}
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
        ta("2,54+14,1")
        ta.editables = {1, 2, 4, 19, 20, 22, 23}
        ta.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert ta.move_cursor(index, key) == res

    def test_is_result_line(self, ta):
        ta("9+8")
        check_is_range(ta, "isResultLine", range(9, 12))

    def test_is_retenue_line(self, ta):
        ta("9+8")
        check_is_range(ta, "isRetenueLine", range(3))


@pytest.fixture
def ts():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class Mock(SoustractionModel):
        def __call__(self, string):
            rows, columns, virgule, datas = create_operation(string)
            self.params["rows"] = rows
            self.params["columns"] = columns
            self.params["virgule"] = virgule
            self.params["datas"] = datas
            self.params["size"] = self.rows * self.columns

    Mock.ddb = Dbo()
    a = Mock()
    return a


class TestSoustractionModel:
    @pytest.mark.parametrize(
        "index,res", [(28, 25), (25, 22), (22, 22)],
    )
    def test_automove_next(self, ts, index, res):
        # '',  '', '2', '', '', '5', '', '', '4', '',
        # '-', '', '1', '', '', '4', '', '', '1', '',
        # '',  '', '',  '', '', '',  '', '', '',  '']
        ts("254-141")
        ts.editables = {28, 25, 22}
        assert ts.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res", [(49, 46), (46, 42), (42, 39), (39, 36), (36, 36),],
    )
    def test_automove_next_virgule(self, ts, index, res):
        # '',  '', '4', '', '', '3', '', '', '2', '', ',' ,'', '5', '', '', '4', '', //16
        # '-', '', '3', '', '', '9', '', '', '1', '', ',' ,'', '4', '', '', '1', '', //33
        # '',  '', '' , '', '', '' , '', '', '' , '', ',', '', '',  '', '', '' , ''] //50
        ts("432,54-391,41")
        ts.editables = {
            49,
            46,
            42,
            36,
            39,
        }
        assert ts.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("4-3", set()),
            ("22-12", {4}),
            ("254-141", {4, 7}),
            ("432,54-391,41", {4, 7, 11, 14}),
        ],
    )
    def test_retenue_gaucheand_isRetenueGauche(self, ts, string, res):
        ts(string)
        assert ts.retenue_gauche == res
        assert all(ts.isRetenueGauche(i) for i in res)
        assert not any(ts.isRetenueGauche(i + 1) for i in res)

    @pytest.mark.parametrize(
        "string, res",
        [
            ("4-3", set()),
            ("22-12", {10}),
            ("254-141", {13, 16}),
            ("432,54-391,41", {20, 23, 26, 30}),
        ],
    )
    def test_retenue_droite_and_isRetenueDroite(self, ts, string, res):
        ts(string)
        assert ts.retenue_droite == res
        assert all(ts.isRetenueDroite(i) for i in res)
        assert not any(ts.isRetenueDroite(i + 1) for i in res)

    def test_is_result_line(self, ts):
        ts("34-22")
        check_is_range(ts, "isResultLine", range(14, 22))
        # 3 * 7
        # ['', '', '3', '', '', '4', '', '-', '', '2', '', '', '2', '', '', '', '', '', '', '', '']

    def test_is_retenue_line(self, ts):
        ts("34-22")
        check_is_range(ts, "isRetenueLine", range(0, 7))

    @pytest.mark.parametrize(
        "index,key, res",
        [
            (36, Qt.Key_Right, 39),
            (39, Qt.Key_Right, 42),
            (42, Qt.Key_Right, 46),
            (46, Qt.Key_Right, 49),
            (49, Qt.Key_Right, 99),
            (36, Qt.Key_Left, 99),
            (39, Qt.Key_Left, 36),
            (42, Qt.Key_Left, 39),
            (46, Qt.Key_Left, 42),
            (49, Qt.Key_Left, 46),
        ],
    )
    def test_movecursor(self, ts, index, key, res):
        # '',  '', '4', '', '*', '3', '', '*', '2', '', ',' ,'*', '5', '', '*', '4', '', //16
        # '-', '', '3', '*', '', '9', '*', '', '1', '*', ',' ,'', '4', '*', '', '1', '', //33
        # '',  '', '*' , '', '', '*' , '', '', '*' , '', ',', '', '*',  '', '', '*' , ''] //50
        ts("432,54-391,41")
        ts.editables = {36, 39, 42, 46, 49}
        ts.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert ts.move_cursor(index, key) == res

    @pytest.mark.parametrize(
        "index,key, res",
        [
            (36, Qt.Key_Right, 39),
            (39, Qt.Key_Right, 43),
            (43, Qt.Key_Right, 46),
            (46, Qt.Key_Right, 49),
            (49, Qt.Key_Right, 99),
            (36, Qt.Key_Left, 99),
            (39, Qt.Key_Left, 36),
            (43, Qt.Key_Left, 39),
            (46, Qt.Key_Left, 43),
            (49, Qt.Key_Left, 46),
            (49, Qt.Key_Up, 49),
            (49, Qt.Key_Down, 49),
        ],
    )
    def test_movecursor2(self, ts, index, key, res):
        # '',  '', '1', '', '*', '2', '', ',',  '*', '',  '', '*', '',  '', '*', '',  '', //16
        # '-', '', '',  '*', '', '3', '*', ',', '', '3', '*', '', '4', '*', '', '5', '',//33
        # '',  '', '*',  '', '', '*',  '', ',', '', '*',  '', '', '*',  '', '', '*',  ''//50
        ts("12-3,345")
        ts.editables = {36, 39, 43, 46, 49}
        ts.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert ts.move_cursor(index, key) == res

    @pytest.mark.parametrize("cur, r1, r2", [(28, 7, 16), (25, 4, 13),])
    def test_addRetenues(self, cur, r1, r2, dao):
        # '',  '', '2', '', '', '5', '', '', '4', '', //9
        # '-', '', '1', '', '', '4', '', '', '1', '', //19
        # '',  '', '',  '', '', '',  '', '', '',  ''] //29
        class Sous(SoustractionModel):
            ddb = dao

        tss = f_soustractionSection("254-141")
        mod = Sous()
        mod.sectionId = tss.id
        mod.cursor = cur
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == ""
        # add
        mod.addRetenues()
        assert mod.datas[r1] == "1"
        assert mod.datas[r2] == "1"
        # remove
        mod.addRetenues()
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == ""

    @pytest.mark.parametrize(
        "cur, r1, r2", [(49, 14, 30), (46, 11, 27), (43, 8, 23), (39, 4, 20),]
    )
    def test_addRetenuesVirgule(self, cur, r1, r2, dao):
        # ' ', ' ', '1', ' ', '*', '2', ' ', ',', '*', '0', ' ', '*', '0', ' ', '*', '0', ' ', //16
        # '-', ' ', ' ', '*', ' ', '3', '*', ',', ' ', '3', '*', ' ', '4', '*', ' ', '5', ' ',//33
        # ' ', ' ', '*', ' ', ' ', '*', ' ', ',', ' ', '*', ' ', ' ', '*', ' ', ' ', '*', ' '//50
        class Sous(SoustractionModel):
            ddb = dao

        tss = f_soustractionSection("12-3,345")
        mod = Sous()
        mod.sectionId = tss.id
        mod.cursor = cur
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == ""
        # add
        mod.addRetenues()
        assert mod.datas[r1] == "1"
        assert mod.datas[r2] == "1"
        # remove
        mod.addRetenues()
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(36, 1, 17)])
    def test_addRetenuesNedoitPas(self, cur, r1, r2, dao):
        class Sous(SoustractionModel):
            ddb = dao

        tss = f_soustractionSection("12-3,345")
        mod = Sous()
        mod.sectionId = tss.id
        mod.cursor = cur
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == "-"
        # add
        mod.addRetenues()
        assert mod.datas[r1] == ""
        assert mod.datas[r2] == "-"

    def test_initial_position(self, ts):
        ts("123 - 99")
        assert ts.getInitialPosition() == 28


@pytest.fixture
def tm():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class Mock(MultiplicationModel):
        def __call__(self, string):
            rows, columns, virgule, datas = create_operation(string)
            self.params["rows"] = rows
            self.params["columns"] = columns
            self.params["virgule"] = virgule
            self.params["datas"] = datas
            self.params["size"] = len(self.params["datas"])
            self.n_chiffres = int((self.rows - 4) / 2) or 1

    Mock.ddb = Dbo()
    a = Mock()
    return a


class TestMultiplicationModel:
    def test_getInitialPosition(self, tm):
        tm("23*77")
        assert tm.getInitialPosition() == 24

    @pytest.mark.parametrize(
        "numbers, compris",
        [
            ("2*1", {6, 7}),
            ("23*77", {35, 36, 37, 38, 39}),
            ("2,3*7,7", set(range(42, 48))),
            ("251*148", set(range(54, 60))),
        ],
    )
    def test_is_result_line(self, tm, numbers, compris):
        tm(numbers)
        # '', '', '', '', '', '',
        # '', '', '', '', '', '',
        # '', '', '', '2', ',', '3',
        # 'x', '', '', '7', ',', '7',
        # '', '', '', '', '', '',
        # '', '', '', '', '', '',
        # '', '', '', '', '', '',
        # '', '', '', '', '', '',
        # '', '', '', '', '', '']

        for i in compris:
            assert tm.isResultLine(i), f" {i} should return True"
        non_compris = set(range(0, tm.size))
        non_compris = non_compris - compris
        for i in non_compris:
            assert not tm.isResultLine(i), f" {i} should return False"

    def test_is_membre_line(self, tm):
        tm("23*77")
        check_is_range(tm, "isMembreLine", range(10, 20))

    def test_is_line1(self, tm):
        tm("23*77")
        check_is_range(tm, "isLine1", range(15, 20))

    @pytest.mark.parametrize(
        "numbers, compris",
        [
            ("2*1", {0, 1}),
            ("23*77", set(range(10)) | set(range(30, 35))),
            ("2,3*7,7", set(range(12)) | set(range(36, 42))),
            ("251*148", set(range(18)) | set(range(48, 54))),
        ],
    )
    def test_is_retenue_line(self, tm, numbers, compris):
        tm(numbers)
        check_is_range(tm, "isRetenueLine", compris)

    @pytest.mark.parametrize(
        "index,res",
        [(35, 16), (16, 34), (34, 15), (15, 33), (33, 32), (32, 41)]
        + [(41, 40), (40, 10), (10, 39), (39, 9), (9, 38), (38, 37), (37, 47)]
        + [(47, 46), (46, 45), (45, 4), (4, 44), (44, 3), (3, 43), (43, 59)]
        + [(59, 52), (52, 58), (58, 51), (51, 57), (57, 50), (50, 56), (56, 49)]
        + [(49, 55), (55, 55)],
    )
    def test_automove_next(self, tm, index, res):
        # 10 rows, 6 columns
        # '', '', '',  's',  'q', '', //5
        # '', '', '',  'k',  'i', '', //11
        # '', '', '',  'd',  'b', '', //17
        # '', '', '',  '2',  '5', '1', //23
        # 'x','', '',  '1',  '4', '8', //29
        # '', '', 'f', 'e',  'c', 'a', //35
        # '', 'm', 'l', 'j', 'h', 'g', //41
        # '', 't', 'r', 'p', 'o', 'n', //47
        # '', 'b', 'z', 'x', 'v', '', //53
        # '', 'c', 'a', 'y', 'w', 'u' //59

        tm("251*148")
        assert tm.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res", [(11, 1), (1, 10),],
    )
    def test_automove_next2(self, tm, index, res):
        # '',  '',  '',
        # '',  '1', '2',
        # 'x', '',  '3',
        # '',  '',  ''
        tm("12*3")
        assert tm.auto_move_next(index) == res

    #
    @pytest.mark.parametrize(
        "index,res",
        [(41, 18), (18, 40), (40, 17), (17, 39), (39, 38), (38, 48)]
        + [(48, 47), (47, 11), (11, 46), (46, 10), (10, 45), (45, 44), (44, 55)]
        + [(55, 54), (54, 53), (53, 4), (4, 52), (52, 3), (3, 51), (51, 50), (50, 69)]
        + [(69, 61), (61, 68), (68, 60), (60, 67), (67, 59), (59, 66),]
        + [(66, 58), (58, 65), (65, 57), (57, 64), (64, 64)],
    )
    def test_automove_next_virgule(self, tm, index, res):
        # 10  rows, 7 columns, size 77
        # '',  '',  '',  's', 'q', '',  '', //6
        # '',  '',  '',  'k', 'i', '',  '', //13
        # '',  '',  '',  'd', 'b', '',  '', //20
        # '',  '',  '',  '2', '5', ',', '1', //27
        # 'x', '',  '',  '1', ',', '4', '8', //34
        # '',  '',  '',  'f', 'e', 'c', 'a', //41
        # '',  '',  'm', 'l', 'j', 'h', 'g', //48
        # '',  'u', 't', 'r', 'p', 'o', 'n', //55
        # '',  'e', 'c', 'a', 'y', 'w', '', //62
        # '',  'f', 'd', 'b', 'z', 'x', 'v', //69
        # '',  '',  '',  '',  '',  '',  '', //76

        tm("1,48*25,1")
        assert tm.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index, res",
        [(41, 18), (18, 40), (40, 17), (17, 39), (39, 38), (38, 48)]
        + [(48, 47), (47, 11), (11, 46), (46, 10), (10, 45), (45, 44), (44, 55)]
        + [(55, 54), (54, 53), (53, 4), (4, 52), (52, 3), (3, 51), (51, 50), (50, 69)]
        + [(69, 61), (61, 68), (68, 60), (60, 67), (67, 59), (59, 66),]
        + [(66, 58), (58, 65), (65, 57), (57, 64), (64, 64)],
    )
    def test_automovenext_virgule2(self, tm, index, res):
        # 10 rows, 7 columns, virgule 4, size 77
        # '',  '',  '',  's', 'q', '', '', //6
        # '',  '',  '',  'k', 'i', '', '', //13
        # '',  '',  '',  'd', 'b', '', '', //20
        # '',  '',  '',  '2', '5', ',', '1', //27
        # 'x', '',  '',  '1', ',', '4', '8', //34
        # '',  '',  '',  'f', 'e', 'c', 'a', //41
        # '',  '',  'm', 'l', 'j', 'h', 'g', //48
        # '',  'u', 't', 'r', 'p', 'o', 'n', //55
        # '',  'e', 'c', 'a', 'y', 'w', '',  //62
        # '',  'f', 'd', 'b', 'z', 'x', 'v', //69
        # '',  '',  '',  '',  '',  '',  '', //76

        tm("25,1*1,48")
        assert tm.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index, res",
        [(2, 99), (3, 99), (9, 2), (10, 3), (16, 9), (17, 10), (36, 99),]
        + [(37, 16), (38, 17), (40, 99), (41, 99), (43, 36), (44, 37), (45, 38),]
        + [(47, 40), (48, 41), (50, 43), (51, 44), (52, 45), (54, 47), (55, 48),]
        + [(57, 50), (58, 51), (59, 52), (61, 54), (62, 55), (64, 57), (65, 58),]
        + [(66, 59), (68, 61), (69, 62), (71, 64), (72, 65), (73, 66), (74, 99),],
    )
    def test_movecursor_keyup(self, tm, index, res):
        # 10 rows, 7 columns, virgule 4, size 70
        # ' ', ' ', ' ', 's', ' ', ' ', ' ',//6
        # ' ', ' ', 'm', 'k', ' ', ' ', ' ',//13
        # ' ', ' ', 'e', 'c', ' ', ' ', ' ',//20
        # ' ', ' ', '2', '5', ',', '1', ' ',//27
        # 'x', ' ', ' ', '1', ',', '4', '8',//34
        # ' ', 'g', 'f', 'd', ' ', 'b', 'a',//41
        # ' ', 'n', 'l', 'j', ' ', 'i', 'h',//48
        # ' ', 't', 'r', 'q', ' ', 'p', 'o',//55
        # ' ', 'b', 'z', 'x', '', 'v', ' ',//62
        # ' ', 'c', 'a', 'y', '', 'w', 'u',//69
        # ' ', ' ', ' ', ' ', 'd', ' ', ' ' ,//76

        tm("25,1*1,48")
        tm.editables = (
            {2, 3, 9, 10, 16, 17, 36, 37, 38, 40, 41, 43,}
            | {44, 45, 47, 48, 50, 51, 52, 54, 55, 57, 58, 59, 61, 62, 64,}
            | {65, 66, 68, 69, 71, 72, 73, 74,}
        )

        tm.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert tm.move_cursor(index, Qt.Key_Up) == res

    @pytest.mark.parametrize(
        "index, res",
        [(2, 9), (3, 10), (9, 16), (10, 17), (16, 37), (17, 38), (36, 43),]
        + [(37, 44), (38, 45), (40, 47), (41, 48), (43, 50), (44, 51), (45, 52),]
        + [(47, 54), (48, 55), (50, 57), (51, 58), (52, 59), (54, 61), (55, 62),]
        + [(57, 64), (58, 65), (59, 66), (61, 68), (62, 69), (64, 71), (65, 72),]
        + [(66, 73), (68, 99), (69, 99), (71, 99), (72, 99), (73, 99), (74, 99),],
    )
    def test_movecursor_down(self, tm, index, res):
        # 10 rows, 7 columns, virgule 4, size 70
        # ' ', ' ', ' ', 's', ' ', ' ', ' ',//6
        # ' ', ' ', 'm', 'k', ' ', ' ', ' ',//13
        # ' ', ' ', 'e', 'c', ' ', ' ', ' ',//20
        # ' ', ' ', '2', '5', ',', '1', ' ',//27
        # 'x', ' ', ' ', '1', ',', '4', '8',//34
        # ' ', 'g', 'f', 'd', ' ', 'b', 'a',//41
        # ' ', 'n', 'l', 'j', ' ', 'i', 'h',//48
        # ' ', 't', 'r', 'q', ' ', 'p', 'o',//55
        # ' ', 'b', 'z', 'x', '', 'v', ' ',//62
        # ' ', 'c', 'a', 'y', '', 'w', 'u',//69
        # ' ', ' ', ' ', ' ', 'd', ' ', ' ' ,//76

        tm("25,1*1,48")
        tm.editables = (
            {2, 3, 9, 10, 16, 17, 36, 37, 38, 40, 41, 43,}
            | {44, 45, 47, 48, 50, 51, 52, 54, 55, 57, 58, 59, 61, 62, 64,}
            | {65, 66, 68, 69, 71, 72, 73, 74,}
        )

        tm.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert tm.move_cursor(index, Qt.Key_Down) == res

    #
    @pytest.mark.parametrize(
        "index, res",
        [(2, 3), (3, 99), (9, 10), (10, 99), (16, 17), (17, 99), (36, 37),]
        + [(37, 38), (38, 40), (40, 41), (41, 99), (43, 44), (44, 45), (45, 47),]
        + [(47, 48), (48, 99), (50, 51), (51, 52), (52, 54), (54, 55), (55, 99),]
        + [(57, 58), (58, 59), (59, 61), (61, 62), (62, 99), (64, 65), (65, 66),]
        + [(66, 68), (68, 69), (69, 99), (71, 72), (72, 73), (73, 74), (74, 99),],
    )
    def test_movecursor_right(self, tm, index, res):
        # 10 rows, 7 columns, virgule 4, size 70
        # ' ', ' ', ' ', 's', ' ', ' ', ' ',//6
        # ' ', ' ', 'm', 'k', ' ', ' ', ' ',//13
        # ' ', ' ', 'e', 'c', ' ', ' ', ' ',//20
        # ' ', ' ', '2', '5', ',', '1', ' ',//27
        # 'x', ' ', ' ', '1', ',', '4', '8',//34
        # ' ', 'g', 'f', 'd', ' ', 'b', 'a',//41
        # ' ', 'n', 'l', 'j', ' ', 'i', 'h',//48
        # ' ', 't', 'r', 'q', ' ', 'p', 'o',//55
        # ' ', 'b', 'z', 'x', '', 'v', ' ',//62
        # ' ', 'c', 'a', 'y', '', 'w', 'u',//69
        # ' ', ' ', ' ', ' ', 'd', ' ', ' ' ,//76

        tm("25,1*1,48")
        tm.editables = (
            {2, 3, 9, 10, 16, 17, 36, 37, 38, 40, 41, 43,}
            | {44, 45, 47, 48, 50, 51, 52, 54, 55, 57, 58, 59, 61, 62, 64,}
            | {65, 66, 68, 69, 71, 72, 73, 74,}
        )

        tm.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert tm.move_cursor(index, Qt.Key_Right) == res

    @pytest.mark.parametrize(
        "index, res",
        [(2, 99), (3, 2), (9, 99), (10, 9), (16, 99), (17, 16), (36, 99),]
        + [(37, 36), (38, 37), (40, 38), (41, 40), (43, 99), (44, 43), (45, 44),]
        + [(47, 45), (48, 47), (50, 99), (51, 50), (52, 51), (54, 52), (55, 54),]
        + [(57, 99), (58, 57), (59, 58), (61, 59), (62, 61), (64, 99), (65, 64),]
        + [(66, 65), (68, 66), (69, 68), (71, 99), (72, 71), (73, 72), (74, 73),],
    )
    def test_movecursor_left(self, tm, index, res):
        # 10 rows, 7 columns, virgule 4, size 70
        # ' ', ' ', ' ', 's', ' ', ' ', ' ',//6
        # ' ', ' ', 'm', 'k', ' ', ' ', ' ',//13
        # ' ', ' ', 'e', 'c', ' ', ' ', ' ',//20
        # ' ', ' ', '2', '5', ',', '1', ' ',//27
        # 'x', ' ', ' ', '1', ',', '4', '8',//34
        # ' ', 'g', 'f', 'd', ' ', 'b', 'a',//41
        # ' ', 'n', 'l', 'j', ' ', 'i', 'h',//48
        # ' ', 't', 'r', 'q', ' ', 'p', 'o',//55
        # ' ', 'b', 'z', 'x', '', 'v', ' ',//62
        # ' ', 'c', 'a', 'y', '', 'w', 'u',//69
        # ' ', ' ', ' ', ' ', 'd', ' ', ' ' ,//76

        tm("25,1*1,48")
        tm.editables = (
            {2, 3, 9, 10, 16, 17, 36, 37, 38, 40, 41, 43,}
            | {44, 45, 47, 48, 50, 51, 52, 54, 55, 57, 58, 59, 61, 62, 64,}
            | {65, 66, 68, 69, 71, 72, 73, 74,}
        )

        tm.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert tm.move_cursor(index, Qt.Key_Left) == res

    @pytest.mark.parametrize(
        "op, editables, res",
        [
            (
                "251*148",
                {3, 4, 9, 10, 15, 16, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 43,}
                | {44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57, 58, 59,},
                {31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47},
            ),
            ("2*3", {7,}, {7},),
            ("8*7", {1, 10, 11}, {10, 11},),
            ("8*7", {1, 10, 11}, {10, 11},),
            (
                "25,1*1,48",
                {3, 4, 10, 11, 17, 18, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47,}
                | {48, 50, 51, 52, 53, 54, 55, 57, 58, 59,}
                | {60, 61, 62, 64, 65, 66, 67, 68, 69,},
                {36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47,}
                | {48, 50, 51, 52, 53, 54, 55},
            ),
        ],
    )
    def test_editables_index_middle(self, tm, op, editables, res):

        tm(op)
        tm.editables = editables

        assert tm.editables_index_middle == res

    @pytest.mark.parametrize(
        "index,y, x",
        [(35, 29, 23), (34, 29, 22), (33, 29, 21), (32, 29, 21)]
        + [(41, 28, -1), (40, 28, 23), (39, 28, 22), (38, 28, 21), (37, 28, 21),]
        + [(47, 27, -1), (46, 27, -1), (45, 27, 23), (44, 27, 22), (43, 27, 21)]
        + [(4, -1, -1), (52, -1, -1), (58, -1, -1)],  # "non concernés"
    )
    def test_get_Highlighted(self, tm, index, y, x):
        # 10 rows, 6 columns
        # '', '', '',  's',  'q', '', //5
        # '', '', '',  'k',  'i', '', //11
        # '', '', '',  'd',  'b', '', //17
        # '', '', '',  '2',  '5', '1', //23
        # 'x','', '',  '1',  '4', '8', //29
        # '', '', 'f', 'e',  'c', 'a', //35
        # '', 'm', 'l', 'j', 'h', 'g', //41
        # '', 't', 'r', 'p', 'o', 'n', //47
        # '', 'b', 'z', 'x', 'v', '', //53
        # '', 'c', 'a', 'y', 'w', 'u' //59

        tm("251*148")
        tm.editables = (
            {3, 4, 9, 10, 15, 16, 31, 32,}
            | {33, 34, 35, 37, 38, 39, 40, 41,}
            | {43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57, 58, 59,}
        )
        assert tm.getHighlightedForCurrent(index) == (y, x)

    @pytest.mark.parametrize(
        "index,y, x",
        [
            (41, 34, 27),
            (40, 34, 25),
            (39, 34, 24),
            (38, 34, 24),
            (37, 34, 24),
            (36, 34, 24),
            (48, 33, -1),
            (47, 33, 27),
            (46, 33, 25),
            (45, 33, 24),
            (43, 33, 24),
            (55, 31, -1),
            (54, 31, -1),
            (53, 31, 27),
            (52, 31, 25),
            (51, 31, 24),
            (50, 31, 24),
        ]
        + [(4, -1, -1), (58, -1, -1), (64, -1, -1)],  # "non concernés"
    )
    def test_get_HighlightedVirgule(self, tm, index, y, x):
        # 10 rows, 7 columns, virgule 4, size 70
        # ' ', ' ', ' ', ' ', ' ', ' ', ' ',//6
        # ' ', ' ', ' ', ' ', ' ', ' ', ' ',//13
        # ' ', ' ', ' ', ' ', ' ', ' ', ' ',//20
        # ' ', ' ', ' ', '2', '5', ',', '1',//27
        # 'x', ' ', ' ', '1', ',', '4', '8',//34
        # ' ', ' ', ' ', ' ', ' ', ' ', ' ',//41
        # '+', ' ', ' ', ' ', ' ', ' ', ' ',//48
        # '+', ' ', ' ', ' ', ' ', ' ', ' ',/55
        # '+', ' ', ' ', ' ', ' ', ' ', ' ',//62
        # ' ', ' ', ' ', ' ', ' ', ' ', ' ',//69

        tm("25,1*1,48")
        tm.editables = (
            {3, 4, 10, 11, 17, 18, 36, 37, 38, 39, 40, 41, 43,}
            | {44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 57,}
            | {58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69,}
        )
        assert tm.getHighlightedForCurrent(index) == (y, x)

    def test_highLightProperty(self, tm, qtbot):
        tm("25,1*1,48")
        tm.editables = (
            {3, 4, 10, 11, 17, 18, 36, 37, 38, 39, 40, 41, 43,}
            | {44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 57,}
            | {58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69,}
        )

        with qtbot.waitSignal(tm.highLightChanged):
            tm.cursor = 46
        assert tm.highLight == [33, 25]

    def test_highLightProperty_simple(self, tm, qtbot):
        tm("12*2")
        tm.editables = {1, 10, 11}

        with qtbot.waitSignal(tm.highLightChanged):
            tm.cursor = 10
        assert tm.highLight == [8, 4]
        with qtbot.waitSignal(tm.highLightChanged):
            tm.cursor = 11
        assert tm.highLight == [8, 5]

    def test_custom_params_load(self, dao):
        class MultiplicationModel2(MultiplicationModel):
            ddb = dao

        a = MultiplicationModel2()
        # a.ddb = dao
        x = f_multiplicationSection()
        a.sectionId = x.id
        with db_session:
            assert a.n_chiffres == x.n_chiffres

    def test_get_initial_position(self, dao):
        class MultiplicationModel2(MultiplicationModel):
            ddb = dao

        a = MultiplicationModel2()
        x = f_multiplicationSection(string="323*23")
        a.sectionId = x.id
        assert a.cursor == 24


@pytest.fixture
def td():
    class Dbo:
        recentsModelChanged = Signal()
        sectionIdChanged = Signal()

    class Mock(DivisionModel):
        def __call__(self, string):
            rows, columns, virgule, datas = create_operation(string)
            self.params["rows"] = rows
            self.params["columns"] = columns
            self.params["virgule"] = virgule
            self.params["datas"] = datas["datas"]
            self.params["dividende"] = datas["dividende"]
            self.params["diviseur"] = datas["diviseur"]
            self.params["size"] = rows * columns  # len(datas)
            self._dividende, self._diviseur = [Decimal(x) for x in string.split("/")]
            self._quotient = ""

    Mock.ddb = Dbo()
    a = Mock()
    return a


@pytest.fixture
def divMod(dao):
    class Temp(DivisionModel):
        ddb = dao

        def __call__(self, string):
            self.f_entry = f_divisionSection(string=string)
            self.sectionId = self.f_entry.id

    return Temp()


class TestDivisionModel:
    def test_custom_params_load(self, divMod):
        divMod("345/23,5")
        assert divMod._dividende == 345
        assert divMod._diviseur == 23.5
        assert divMod._quotient == divMod.f_entry.quotient

    def test_isDividendeLine(self, td):
        check_args(td.isDividendeLine, int, bool)
        td("23/4")  # col = 12, rows = 7
        check_is_range(td, "isDividendeLine", range(12))

    def test_isMembreLine(self, td):
        td("23/4")
        check_is_range(
            td,
            "isMembreLine",
            set(range(12, 24)) | set(range(36, 48)) | set(range(60, 72)),
        )

    def test_isRetenue(self, td):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        check_is_range(
            td, "isRetenue", {11, 3, 6, 14, 21, 24, 29, 32},
        )
        check_is_range(
            td, "isRetenueGauche", {3, 6, 21, 24},
        )
        check_is_range(
            td, "isRetenueDroite", {11, 14, 29, 32},
        )

    def test_diviseur_dividende(self, divMod):
        divMod._diviseur = 1
        assert divMod.diviseur == 1
        divMod._dividende = 2
        assert divMod.dividende == 2

    @pytest.mark.parametrize(
        "index, res",
        [(3, 99), (6, 99)]
        + [(10, 99), (11, 99), (13, 99), (14, 99), (16, 99)]
        + [(19, 10), (21, 3), (22, 13), (24, 6), (25, 16)]
        + [(28, 19), (29, 11), (31, 22), (32, 14), (34, 25)]
        + [(37, 28), (40, 31), (43, 34)],
    )
    def test_move_cursor_up(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        td.editables = (
            {3, 6,}
            | {10, 11, 13, 14, 16,}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34,}
            | {37, 40, 43}
        )

        td.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert td.move_cursor(index, Qt.Key_Up) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 21), (6, 24)]
        + [(10, 19), (11, 29), (13, 22), (14, 32), (16, 25)]
        + [(19, 28), (21, 99), (22, 31), (24, 99), (25, 34)]
        + [(28, 37), (29, 99), (31, 40), (32, 99), (34, 43),]
        + [(37, 99), (40, 99), (43, 99)],
    )
    def test_move_cursor_down(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '*', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        td.editables = (
            {3, 6,}
            | {10, 11, 13, 14, 16,}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34,}
            | {37, 40, 43}
        )

        td.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert td.move_cursor(index, Qt.Key_Down) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 99), (6, 3)]
        + [(10, 6), (11, 10), (13, 11), (14, 13), (16, 14)]
        + [(19, 16), (21, 19), (22, 21), (24, 22), (25, 24)]
        + [(28, 25), (29, 28), (31, 29), (32, 31), (34, 32),]
        + [(37, 34), (40, 37), (43, 40)],
    )
    def test_move_cursor_left(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        td.editables = (
            {3, 6}
            | {10, 11, 13, 14, 16,}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34,}
            | {37, 40, 43}
        )

        td.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert td.move_cursor(index, Qt.Key_Left) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 6), (6, 10)]
        + [(10, 11), (11, 13), (13, 14), (14, 16), (16, 19),]
        + [(19, 21), (21, 22), (22, 24), (24, 25), (25, 28)]
        + [(28, 29), (29, 31), (31, 32), (32, 34), (34, 37),]
        + [(37, 40), (40, 43), (43, 99)],
    )
    def test_move_cursor_right(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        td.editables = (
            {3, 6,}
            | {10, 11, 13, 14, 16,}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34,}
            | {37, 40, 43}
        )

        td.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert td.move_cursor(index, Qt.Key_Right) == res

    def test_range_of_type_retenue_chiffre(self, td):
        td("264/11")
        td.editables = (
            {3, 6,}
            | {10, 11, 13, 14, 16}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34}
            | {37, 40, 43}
        )
        assert td.retenue_gauche == {3, 6, 21, 24}
        assert td.retenue_droite == {11, 14, 29, 32}
        assert td.regular_chiffre == {10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43}

    @pytest.mark.parametrize(
        "index, res",
        [(3, 11), (6, 14), (21, 29), (24, 32)]  # retenue gauche
        + [(11, 22), (14, 25), (29, 40), (32, 43)]  # retenue droite
        + [(10, 22), (13, 10), (16, 13), (28, 43), (31, 28), (34, 31),]  # chiffre imprs
        + [(19, 19), (22, 19), (25, 22), (37, 37), (40, 37), (43, 40),],  # chiff pairs
    )
    def test_automove_next(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z',  '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        td("264/11")
        td.editables = (
            {3, 6,}
            | {10, 11, 13, 14, 16, 17}
            | {18, 19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34, 35}
            | {37, 40, 43}
        )
        td.params["datas"][13] = 5  # besoni d'une value pour move à la ligne
        td.params["datas"][34] = 1  # besoni d'une value pour move à la ligne

        assert td.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "cur, r1, r2", [(22, 3, 11), (25, 6, 14), (40, 21, 29), (43, 24, 32)]
    )
    def test_addRetenues(self, divMod, cur, r1, r2):
        divMod("264/11")
        divMod.cursor = cur
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""
        # add
        divMod.addRetenues()
        assert divMod.datas[r1] == "1"
        assert divMod.datas[r2] == "1"
        # remove
        divMod.addRetenues()
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(31, 12, 20)])
    def test_addRetenuesMemebreline(self, divMod, cur, r1, r2):
        divMod("264/11")
        divMod.cursor = cur
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""
        # add
        divMod.addRetenues()
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(19, 0, 8), (19, 0, 8)])
    def test_addRetenuesOuIlneDoitPasYenAvoir(self, divMod, cur, r1, r2):
        divMod("264/11")
        divMod.cursor = cur
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""
        # add
        divMod.addRetenues()
        assert divMod.datas[r1] == ""
        assert divMod.datas[r2] == ""

    def test_get_last_index_filled(self, td):
        assert td._get_last_index_filled(["", "3", "5", "", "", "4", ""]) == 5
        assert td._get_last_index_filled(["", "3", "5", "", "", "", ""]) == 2
        assert td._get_last_index_filled(["1", "", "", "", "", "", ""]) == 0
        assert td._get_last_index_filled(["", "", "", "", "", "", ""]) == 6
        assert td._get_last_index_filled(("", "", "", "", "", "", "")) == 6

    def test_goToResultLine(self, td):
        td("264/11")
        td.params["datas"][16] = 9
        td.cursor = 13
        td.goToResultLine()
        assert td.cursor == 25
        td.params["datas"][34] = 9
        td.cursor = 31
        td.goToResultLine()
        assert td.cursor == 43

    def test_goToabaisseLine(self, td):
        td("264/11")
        td.params["datas"][22] = 1
        td.cursor = 19
        td.goToAbaisseLine()
        assert td.cursor == 25

    @pytest.mark.parametrize(
        "string, quotient, pos, res",
        [
            ("264/11", "", 99, 16),
            ("264/11", "1", 99, 16),
            ("264/1", "", 99, 16),
            ("264/1", "1", 99, 16),
            ("264/11", "11", 19, 31),
        ],
    )
    def test_getPosByQuotient(self, divMod, string, quotient, pos, res):
        check_args(divMod.getPosByQuotient, None, int)
        divMod("264/11")
        divMod.cursor = pos
        divMod.quotient = quotient
        divMod.getPosByQuotient()
        assert divMod.cursor == res

    def test_Readonly(self, divMod):
        divMod("264/11")
        #     # ' ', '2', ' ', '*', '6', ' ', '*', '4', ' ' //8
        #     # ' ', '*', '*', ' ', '*', '*', ' ', '*', ' ', // 17
        #     # ' ', '*', ' ', '*', '*', ' ', '*', '*', ' ', // 26
        #     # ' ', '*', '*', ' ', '*', '*', ' ', '*', ' ', // 35
        #     # ' ', '*', ' ', ' ',  '*', ' ', ' ', '*', ' ' , //44
        assert divMod.editables == {34, 37, 40, 10, 43, 13, 16, 19, 22, 25, 28, 31}
        non_compris = set(range(0, divMod.size)) - divMod.editables
        check_is_range(divMod, "readOnly", non_compris)

    def test_isEditable(self, divMod):
        divMod("264/11")
        assert divMod.editables == {34, 37, 40, 10, 43, 13, 16, 19, 22, 25, 28, 31}
        check_is_range(divMod, "isEditable", divMod.editables)
