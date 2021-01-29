import itertools
from unittest.mock import patch, call

import pytest
from PyQt5.QtCore import Qt
from tests.python.fixtures import check_args, check_is_range
from mycartable.classeur import (
    OperationSection,
    AdditionSection,
    SoustractionSection,
    MultiplicationSection,
)
from mycartable.classeur.sections.operations.operation import DivisionSection

from pony.orm import db_session


@pytest.fixture
def to(fk, bridge):
    a = fk.f_operationSection("9+8")
    b = OperationSection.get(a.id, parent=bridge)
    return b


#
#
class TestOperationModel:
    def test_init(self, fk, bridge):
        a = fk.f_operationSection("9+8")
        b = OperationSection.get(a.id, parent=bridge)
        assert a.columns == b.columns == 3
        assert a.rows == b.rows == 4
        assert a.datas == b.datas == ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
        assert a.size == b.size == 12
        assert a.virgule == b.virgule == 0
        assert b.model
        assert b.model.cursor == 11
        assert b.model.operation is b

    def test_update_datas(self, to, ddbr):
        to.update_datas(to.size - 1, "6")
        res = ["", "", "", "", "", "9", "+", "", "8", "", "", "6"]
        assert to.datas == res
        with db_session:
            assert ddbr.OperationSection[to.id].datas == res

    def test_cursor(self, to, qtbot):
        with qtbot.waitSignal(to.model.cursorChanged):
            to.model.cursor = 1
        assert to.model.cursor == 1

    def test_cursor_no_update_and_no_emit_if_unchanged(self, to, qtbot):
        to.model.cursor = 1
        with qtbot.assertNotEmitted(to.model.cursorChanged):
            to.model.cursor = 1
        assert to.model.cursor == 1

    def test_autoMoveNext(self, to):
        to.model.autoMoveNext(99)
        assert to.model.cursor == 99

    def test_data(self, to):
        # valid index
        assert to.model.data(to.model.index(5, 0), Qt.DisplayRole) == "9"
        # unvalid index
        assert to.model.data(to.model.index(99, 0), Qt.DisplayRole) is None
        # unvalid role
        assert to.model.data(to.model.index(5, 0), 999999) is None

    def test_flags(self, to):
        assert int(to.model.flags(to.model.index(0, 0))) == 128 + 35
        assert to.model.flags(to.model.index(99, 99)) is None

    def test_setData(self, to):
        assert to.model.setData(
            to.model.index(11, 0), "5", Qt.EditRole
        )  # doit retourner True
        with db_session:
            assert to.datas[11] == "5"

        assert not to.model.setData(to.model.index(99, 0), "5", Qt.EditRole)
        assert not to.model.setData(to.model.index(11, 0), 8, Qt.DisplayRole)
        assert to.datas[11] == "5"  # pas de modif

    def test_setData_automovenext(self, to, qtbot):
        with patch(
            "mycartable.classeur.sections.operations.models.OperationModel.autoMoveNext"
        ):
            assert to.model.setData(
                to.model.index(11, 0), "5", Qt.EditRole
            )  # doit retourner True
            assert to.model.autoMoveNext.call_args_list == [call(11)]
            to.model.autoMoveNext.call_args_list = []

            assert to.model.setData(
                to.model.index(11, 0), "5,", Qt.EditRole
            )  # doit retourner True
            assert to.model.autoMoveNext.call_args_list == []  # pas de modif
            to.model.autoMoveNext.call_args_list = []

            assert to.model.setData(
                to.model.index(11, 0), "5,", Qt.EditRole, move=False
            )  # doit retourner True
            assert to.model.autoMoveNext.call_args_list == []  # pas de modif

    def test_isIResultline(self, to):
        assert to.model.isResultLine(99) is False

    def test_isRetenueline(self, to):
        assert to.model.isRetenueLine(99) is False

    def test_getInitialPosition(self, to):
        assert to.model.getInitialPosition() == 11

    def test_move_cursor(self, to):
        c = to.model.cursor
        to.model.moveCursor(13, 927)
        assert c == to.model.cursor

    def test_ReadOnly(self, to):
        to.model.editables = [1, 6]
        assert to.model.readOnly(2)
        assert not to.model.readOnly(6)

    def test_rowCount(self, to):
        assert to.model.rowCount() == 12

    def test_get_editables(self, to):
        assert to.model.editables == {}

    def test_isMiddleLinee(self, to):
        assert to.model.isMiddleLine(3)

    def test_isMembreLine(self, to):
        assert to.model.isMembreLine(3)


@pytest.fixture
def ta(fk, bridge):
    def wrapped(string):
        a = fk.f_additionSection(string)
        b = AdditionSection.get(a.id, parent=bridge)
        return b

    return wrapped


class TestAdditionModel:
    @pytest.mark.parametrize(
        "index,res",
        [
            (1, 13),
            (2, 14),
            (13, 13),
            (14, 1),
            (15, 2),
        ],
    )
    def test_automove_next(self, ta, index, res):
        t = ta("254+141")
        # ['', '', '', '', '', '2', '5', '4', '+', '1', '4', '1', '', '', '', ''] 4x4
        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res",
        [(23, 4), (4, 22), (22, 2), (2, 20), (20, 1), (1, 19)],
    )
    def test_automove_next_virgule(self, ta, index, res):
        t = ta("2,54+14,1")
        # ['', '', '', '', '', '', '', '', '2', ',', '5', '4', '+', '1', '4', ',', '1', '', '', '', '', '', '', ''] 6x4
        assert t.model.auto_move_next(index) == res

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
        t = ta("254+141")
        t.model.editables = {1, 2, 13, 14, 15}
        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, key) == res

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
        t = ta("2,54+14,1")
        t.model.editables = {1, 2, 4, 19, 20, 22, 23}
        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, key) == res

    def test_is_result_line(self, ta):
        t = ta("9+8")
        check_is_range(t, "isResultLine", range(9, 12))

    def test_is_retenue_line(self, ta):
        t = ta("9+8")
        check_is_range(t, "isRetenueLine", range(3))

    @pytest.mark.parametrize(
        "string, res",
        [
            ("9+8", {1, 10, 11}),
            ("1+2", {7}),
            ("345+289", {1, 2, 13, 14, 15}),
            ("1+2+3", {9}),
            ("1,1+1", {1, 13, 15}),
        ],
    )
    def test_get_editables(self, string, res, ta):
        t = ta(string)
        assert t.model.get_editables() == res


@pytest.fixture
def ts(fk, bridge):
    def wrapped(string):
        a = fk.f_soustractionSection(string)
        b = SoustractionSection.get(a.id, parent=bridge)
        return b

    return wrapped


class TestSoustractionModel:
    @pytest.mark.parametrize(
        "index,res",
        [(28, 25), (25, 22), (22, 22)],
    )
    def test_automove_next(self, ts, index, res):
        # '',  '', '2', '', '', '5', '', '', '4', '',
        # '-', '', '1', '', '', '4', '', '', '1', '',
        # '',  '', '',  '', '', '',  '', '', '',  '']
        t = ts("254-141")
        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res",
        [
            (49, 46),
            (46, 42),
            (42, 39),
            (39, 36),
            (36, 36),
        ],
    )
    def test_automove_next_virgule(self, ts, index, res):
        # '',  '', '4', '', '', '3', '', '', '2', '', ',' ,'', '5', '', '', '4', '', //16
        # '-', '', '3', '', '', '9', '', '', '1', '', ',' ,'', '4', '', '', '1', '', //33
        # '',  '', '' , '', '', '' , '', '', '' , '', ',', '', '',  '', '', '' , ''] //50
        t = ts("432,54-391,41")
        # ts.editables = {
        #     49,
        #     46,
        #     42,
        #     36,
        #     39,
        # }
        assert t.model.auto_move_next(index) == res

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
        t = ts(string)
        assert t.model.retenue_gauche == res
        assert all(t.model.isRetenueGauche(i) for i in res)
        assert not any(t.model.isRetenueGauche(i + 1) for i in res)

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
        t = ts(string)
        assert t.model.retenue_droite == res
        assert all(t.model.isRetenueDroite(i) for i in res)
        assert not any(t.model.isRetenueDroite(i + 1) for i in res)

    def test_is_result_line(self, ts):
        t = ts("34-22")
        check_is_range(t, "isResultLine", range(14, 22))
        # 3 * 7
        # ['', '', '3', '', '', '4', '', '-', '', '2', '', '', '2', '', '', '', '', '', '', '', '']

    def test_is_retenue_line(self, ts):
        t = ts("34-22")
        check_is_range(t, "isRetenueLine", range(0, 7))

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
        t = ts("432,54-391,41")
        # ts.editables = {36, 39, 42, 46, 49}
        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, key) == res

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
        t = ts("12-3,345")
        # ts.editables = {36, 39, 43, 46, 49}
        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, key) == res

    @pytest.mark.parametrize(
        "cur, r1, r2",
        [
            (28, 7, 16),
            (25, 4, 13),
        ],
    )
    def test_addRetenues(self, ts, cur, r1, r2):
        # '',  '', '2', '', '', '5', '', '', '4', '', //9
        # '-', '', '1', '', '', '4', '', '', '1', '', //19
        # '',  '', '',  '', '', '',  '', '', '',  ''] //29
        # class Sous(SoustractionModel):
        #     ddb = dao

        t = ts("254-141")
        t.model.cursor = cur
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""
        # add
        t.model.addRetenues()
        assert t.datas[r1] == "1"
        assert t.datas[r2] == "1"
        # remove
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""

    @pytest.mark.parametrize(
        "cur, r1, r2",
        [
            (49, 14, 30),
            (46, 11, 27),
            (43, 8, 23),
            (39, 4, 20),
        ],
    )
    def test_addRetenuesVirgule(self, cur, r1, r2, ts):
        # ' ', ' ', '1', ' ', '*', '2', ' ', ',', '*', '0', ' ', '*', '0', ' ', '*', '0', ' ', //16
        # '-', ' ', ' ', '*', ' ', '3', '*', ',', ' ', '3', '*', ' ', '4', '*', ' ', '5', ' ',//33
        # ' ', ' ', '*', ' ', ' ', '*', ' ', ',', ' ', '*', ' ', ' ', '*', ' ', ' ', '*', ' '//50

        t = ts("12-3,345")
        t.model.cursor = cur

        assert t.datas[r1] == ""
        assert t.datas[r2] == ""
        # add
        t.model.addRetenues()
        assert t.datas[r1] == "1"
        assert t.datas[r2] == "1"
        # remove
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(36, 1, 17)])
    def test_addRetenuesNedoitPas(self, cur, r1, r2, ts):

        t = ts("12-3,345")
        t.model.cursor = cur
        assert t.datas[r1] == ""
        assert t.datas[r2] == "-"
        # add
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == "-"

    def test_initial_position(self, ts):
        t = ts("123 - 99")
        assert t.model.getInitialPosition() == 28

    def test_lines(self, ts):
        t = ts("24-13")
        a = t.model
        # ['', '', '2', '', '', '4', '', '-', '', '1', '', '', '3', '', '', '', '', '', '', '', ''] 7 3
        assert a.line_0 == ["", "", "2", "", "", "4", ""]
        assert a.line_1 == [
            "-",
            "",
            "1",
            "",
            "",
            "3",
            "",
        ]
        assert a.line_2 == [""] * t.columns

    @pytest.mark.parametrize(
        "string, res",
        [
            ("9-8", {10}),
            ("22-2", {16, 19}),
            ("22-21", {16, 19}),
            ("345-28", {22, 25, 28}),
            ("345-285", {22, 25, 28}),
            ("2,2-1,1", {18, 22}),
        ],
    )
    def test_get_editables(self, string, res, ts):
        t = ts(string)
        assert t.model.get_editables() == res


@pytest.fixture
def tm(fk, bridge):
    def wrapped(string):
        a = fk.f_multiplicationSection(string)
        b = MultiplicationSection.get(a.id, parent=bridge)
        return b

    return wrapped


class TestMultiplicationModel:
    def test_getInitialPosition(self, tm):
        t = tm("23*77")
        assert t.model.getInitialPosition() == 24

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
        t = tm(numbers)
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
            assert t.model.isResultLine(i), f" {i} should return True"
        non_compris = set(range(0, t.size))
        non_compris = non_compris - compris
        for i in non_compris:
            assert not t.model.isResultLine(i), f" {i} should return False"

    def test_is_membre_line(self, tm):
        t = tm("23*77")
        check_is_range(t, "isMembreLine", range(10, 20))

    def test_is_line1(self, tm):
        t = tm("23*77")
        check_is_range(t, "isLine1", range(15, 20))

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
        t = tm(numbers)
        check_is_range(t, "isRetenueLine", compris)

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

        t = tm("251*148")
        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index,res",
        [
            (11, 1),
            (1, 10),
        ],
    )
    def test_automove_next2(self, tm, index, res):
        # '',  '',  '',
        # '',  '1', '2',
        # 'x', '',  '3',
        # '',  '',  ''
        t = tm("12*3")
        assert t.model.auto_move_next(index) == res

    #
    @pytest.mark.parametrize(
        "index,res",
        [(41, 18), (18, 40), (40, 17), (17, 39), (39, 38), (38, 48)]
        + [(48, 47), (47, 11), (11, 46), (46, 10), (10, 45), (45, 44), (44, 55)]
        + [(55, 54), (54, 53), (53, 4), (4, 52), (52, 3), (3, 51), (51, 50), (50, 69)]
        + [
            (69, 61),
            (61, 68),
            (68, 60),
            (60, 67),
            (67, 59),
            (59, 66),
        ]
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

        t = tm("1,48*25,1")
        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index, res",
        [(41, 18), (18, 40), (40, 17), (17, 39), (39, 38), (38, 48)]
        + [(48, 47), (47, 11), (11, 46), (46, 10), (10, 45), (45, 44), (44, 55)]
        + [(55, 54), (54, 53), (53, 4), (4, 52), (52, 3), (3, 51), (51, 50), (50, 69)]
        + [
            (69, 61),
            (61, 68),
            (68, 60),
            (60, 67),
            (67, 59),
            (59, 66),
        ]
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

        t = tm("25,1*1,48")
        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "index, res",
        [
            (2, 99),
            (3, 99),
            (9, 2),
            (10, 3),
            (16, 9),
            (17, 10),
            (36, 99),
        ]
        + [
            (37, 16),
            (38, 17),
            (40, 99),
            (41, 99),
            (43, 36),
            (44, 37),
            (45, 38),
        ]
        + [
            (47, 40),
            (48, 41),
            (50, 43),
            (51, 44),
            (52, 45),
            (54, 47),
            (55, 48),
        ]
        + [
            (57, 50),
            (58, 51),
            (59, 52),
            (61, 54),
            (62, 55),
            (64, 57),
            (65, 58),
        ]
        + [
            (66, 59),
            (68, 61),
            (69, 62),
            (71, 64),
            (72, 65),
            (73, 66),
            (74, 99),
        ],
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

        t = tm("25,1*1,48")
        t.model.editables = (
            {
                2,
                3,
                9,
                10,
                16,
                17,
                36,
                37,
                38,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                47,
                48,
                50,
                51,
                52,
                54,
                55,
                57,
                58,
                59,
                61,
                62,
                64,
            }
            | {
                65,
                66,
                68,
                69,
                71,
                72,
                73,
                74,
            }
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Up) == res

    @pytest.mark.parametrize(
        "index, res",
        [
            (2, 9),
            (3, 10),
            (9, 16),
            (10, 17),
            (16, 37),
            (17, 38),
            (36, 43),
        ]
        + [
            (37, 44),
            (38, 45),
            (40, 47),
            (41, 48),
            (43, 50),
            (44, 51),
            (45, 52),
        ]
        + [
            (47, 54),
            (48, 55),
            (50, 57),
            (51, 58),
            (52, 59),
            (54, 61),
            (55, 62),
        ]
        + [
            (57, 64),
            (58, 65),
            (59, 66),
            (61, 68),
            (62, 69),
            (64, 71),
            (65, 72),
        ]
        + [
            (66, 73),
            (68, 99),
            (69, 99),
            (71, 99),
            (72, 99),
            (73, 99),
            (74, 99),
        ],
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

        t = tm("25,1*1,48")
        t.model.editables = (
            {
                2,
                3,
                9,
                10,
                16,
                17,
                36,
                37,
                38,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                47,
                48,
                50,
                51,
                52,
                54,
                55,
                57,
                58,
                59,
                61,
                62,
                64,
            }
            | {
                65,
                66,
                68,
                69,
                71,
                72,
                73,
                74,
            }
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Down) == res

    #
    @pytest.mark.parametrize(
        "index, res",
        [
            (2, 3),
            (3, 99),
            (9, 10),
            (10, 99),
            (16, 17),
            (17, 99),
            (36, 37),
        ]
        + [
            (37, 38),
            (38, 40),
            (40, 41),
            (41, 99),
            (43, 44),
            (44, 45),
            (45, 47),
        ]
        + [
            (47, 48),
            (48, 99),
            (50, 51),
            (51, 52),
            (52, 54),
            (54, 55),
            (55, 99),
        ]
        + [
            (57, 58),
            (58, 59),
            (59, 61),
            (61, 62),
            (62, 99),
            (64, 65),
            (65, 66),
        ]
        + [
            (66, 68),
            (68, 69),
            (69, 99),
            (71, 72),
            (72, 73),
            (73, 74),
            (74, 99),
        ],
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

        t = tm("25,1*1,48")
        t.model.editables = (
            {
                2,
                3,
                9,
                10,
                16,
                17,
                36,
                37,
                38,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                47,
                48,
                50,
                51,
                52,
                54,
                55,
                57,
                58,
                59,
                61,
                62,
                64,
            }
            | {
                65,
                66,
                68,
                69,
                71,
                72,
                73,
                74,
            }
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Right) == res

    @pytest.mark.parametrize(
        "index, res",
        [
            (2, 99),
            (3, 2),
            (9, 99),
            (10, 9),
            (16, 99),
            (17, 16),
            (36, 99),
        ]
        + [
            (37, 36),
            (38, 37),
            (40, 38),
            (41, 40),
            (43, 99),
            (44, 43),
            (45, 44),
        ]
        + [
            (47, 45),
            (48, 47),
            (50, 99),
            (51, 50),
            (52, 51),
            (54, 52),
            (55, 54),
        ]
        + [
            (57, 99),
            (58, 57),
            (59, 58),
            (61, 59),
            (62, 61),
            (64, 99),
            (65, 64),
        ]
        + [
            (66, 65),
            (68, 66),
            (69, 68),
            (71, 99),
            (72, 71),
            (73, 72),
            (74, 73),
        ],
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

        t = tm("25,1*1,48")
        t.model.editables = (
            {
                2,
                3,
                9,
                10,
                16,
                17,
                36,
                37,
                38,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                47,
                48,
                50,
                51,
                52,
                54,
                55,
                57,
                58,
                59,
                61,
                62,
                64,
            }
            | {
                65,
                66,
                68,
                69,
                71,
                72,
                73,
                74,
            }
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Left) == res

    @pytest.mark.parametrize(
        "op, editables, res",
        [
            (
                "251*148",
                {
                    3,
                    4,
                    9,
                    10,
                    15,
                    16,
                    31,
                    32,
                    33,
                    34,
                    35,
                    37,
                    38,
                    39,
                    40,
                    41,
                    43,
                }
                | {
                    44,
                    45,
                    46,
                    47,
                    49,
                    50,
                    51,
                    52,
                    53,
                    55,
                    56,
                    57,
                    58,
                    59,
                },
                {31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47},
            ),
            (
                "2*3",
                {
                    7,
                },
                {7},
            ),
            (
                "8*7",
                {1, 10, 11},
                {10, 11},
            ),
            (
                "8*7",
                {1, 10, 11},
                {10, 11},
            ),
            (
                "25,1*1,48",
                {
                    3,
                    4,
                    10,
                    11,
                    17,
                    18,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    43,
                    44,
                    45,
                    46,
                    47,
                }
                | {
                    48,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    57,
                    58,
                    59,
                }
                | {
                    60,
                    61,
                    62,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                },
                {
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    43,
                    44,
                    45,
                    46,
                    47,
                }
                | {48, 50, 51, 52, 53, 54, 55},
            ),
        ],
    )
    def test_editables_index_middle(self, tm, op, editables, res):

        t = tm(op)
        t.model.editables = editables

        assert t.model.editables_index_middle == res

    @pytest.mark.parametrize(
        "index,y, x",
        [(35, 29, 23), (34, 29, 22), (33, 29, 21), (32, 29, 21)]
        + [
            (41, 28, -1),
            (40, 28, 23),
            (39, 28, 22),
            (38, 28, 21),
            (37, 28, 21),
        ]
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

        t = tm("251*148")
        t.model.editables = (
            {
                3,
                4,
                9,
                10,
                15,
                16,
                31,
                32,
            }
            | {
                33,
                34,
                35,
                37,
                38,
                39,
                40,
                41,
            }
            | {
                43,
                44,
                45,
                46,
                47,
                49,
                50,
                51,
                52,
                53,
                55,
                56,
                57,
                58,
                59,
            }
        )
        assert t.model.getHighlightedForCurrent(index) == (y, x)

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

        t = tm("25,1*1,48")
        t.model.editables = (
            {
                3,
                4,
                10,
                11,
                17,
                18,
                36,
                37,
                38,
                39,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                46,
                47,
                48,
                50,
                51,
                52,
                53,
                54,
                55,
                57,
            }
            | {
                58,
                59,
                60,
                61,
                62,
                64,
                65,
                66,
                67,
                68,
                69,
            }
        )
        assert t.model.getHighlightedForCurrent(index) == (y, x)

    def test_highLightProperty(self, tm, qtbot):
        t = tm("25,1*1,48")
        t.model.editables = (
            {
                3,
                4,
                10,
                11,
                17,
                18,
                36,
                37,
                38,
                39,
                40,
                41,
                43,
            }
            | {
                44,
                45,
                46,
                47,
                48,
                50,
                51,
                52,
                53,
                54,
                55,
                57,
            }
            | {
                58,
                59,
                60,
                61,
                62,
                64,
                65,
                66,
                67,
                68,
                69,
            }
        )

        with qtbot.waitSignal(t.model.highLightChanged):
            t.model.cursor = 46
        assert t.model.highLight == [33, 25]

    def test_highLightProperty_simple(self, tm, qtbot):
        t = tm("12*2")
        t.model.editables = {1, 10, 11}

        with qtbot.waitSignal(t.model.highLightChanged):
            t.model.cursor = 10
        assert t.model.highLight == [8, 4]
        with qtbot.waitSignal(t.model.highLightChanged):
            t.model.cursor = 11
        assert t.model.highLight == [8, 5]

    def test_get_initial_position(self, tm):
        t = tm(string="323*23")
        assert t.model.cursor == 24

    def test_properties(self, tm, fk):
        t = tm("12*34")
        a = t.model
        assert a.n_chiffres == 2
        assert a.line_0 == ["", "", "3", "4"]
        assert a.line_1 == ["x", "", "1", "2"]

        t.datas = [
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
            "2",
            "x",
            "",
            "3",
            "4",
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
            "",
            "f",
            "",
            "",
            "z",
        ]
        assert a.line_res == ["f", "", "", "z"]

    @pytest.mark.parametrize(
        "string, res",
        [
            ("2*1", {7}),
            ("2*5", {1, 10, 11}),
            ("22*5", {1, 2, 13, 14, 15}),
            (
                "22*55",
                {3, 8, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39},
            ),
            (
                "2,2*5,5",
                {3, 9} | set(range(25, 48)) - set(range(24, 48, 6)),
            ),
            (
                "325,12*99,153",
                set(
                    itertools.chain.from_iterable(
                        range(x, 60, 12) for x in [6, 7, 8, 10]
                    )
                )
                | set(range(84, 168)) - set(range(84, 168, 12)),
            ),
        ],
    )
    def test_get_editables(self, string, res, tm):
        x = tm(string=string)
        assert x.model.get_editables() == res


class TestDivisionSection:
    def test_properties(self, fk, qtbot, bridge):
        a = fk.f_divisionSection("123/2")
        b = DivisionSection.get(a.id, parent=bridge)
        assert a.dividende == "123"
        assert a.diviseur == "2"
        assert a.quotient == ""
        with qtbot.waitSignal(b.quotientChanged):
            b.quotient = "3"


@pytest.fixture
def td(fk, bridge):
    def wrapped(string):
        a = fk.f_divisionSection(string)
        b = DivisionSection.get(a.id, parent=bridge)
        return b

    return wrapped


class TestDivisionModel:
    def test_isDividendeLine(self, td):
        t = t = td("23/4")  # col = 12, rows = 7
        # check_args(t.model.isDividendeLine, int, bool)
        check_is_range(t, "isDividendeLine", range(12))

    def test_isMembreLine(self, td):
        t = td("23/4")
        check_is_range(
            t,
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
        t = td("264/11")
        check_is_range(
            t,
            "isRetenue",
            {11, 3, 6, 14, 21, 24, 29, 32},
        )
        check_is_range(
            t,
            "isRetenueGauche",
            {3, 6, 21, 24},
        )
        check_is_range(
            t,
            "isRetenueDroite",
            {11, 14, 29, 32},
        )

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
        t = td("264/11")
        t.model.editables = (
            {
                3,
                6,
            }
            | {
                10,
                11,
                13,
                14,
                16,
            }
            | {19, 21, 22, 24, 25}
            | {
                28,
                29,
                31,
                32,
                34,
            }
            | {37, 40, 43}
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Up) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 21), (6, 24)]
        + [(10, 19), (11, 29), (13, 22), (14, 32), (16, 25)]
        + [(19, 28), (21, 99), (22, 31), (24, 99), (25, 34)]
        + [
            (28, 37),
            (29, 99),
            (31, 40),
            (32, 99),
            (34, 43),
        ]
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
        t = td("264/11")
        t.model.editables = (
            {
                3,
                6,
            }
            | {
                10,
                11,
                13,
                14,
                16,
            }
            | {19, 21, 22, 24, 25}
            | {
                28,
                29,
                31,
                32,
                34,
            }
            | {37, 40, 43}
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Down) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 99), (6, 3)]
        + [(10, 6), (11, 10), (13, 11), (14, 13), (16, 14)]
        + [(19, 16), (21, 19), (22, 21), (24, 22), (25, 24)]
        + [
            (28, 25),
            (29, 28),
            (31, 29),
            (32, 31),
            (34, 32),
        ]
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
        t = td("264/11")
        t.model.editables = (
            {3, 6}
            | {
                10,
                11,
                13,
                14,
                16,
            }
            | {19, 21, 22, 24, 25}
            | {
                28,
                29,
                31,
                32,
                34,
            }
            | {37, 40, 43}
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Left) == res

    @pytest.mark.parametrize(
        "index, res",
        [(3, 6), (6, 10)]
        + [
            (10, 11),
            (11, 13),
            (13, 14),
            (14, 16),
            (16, 19),
        ]
        + [(19, 21), (21, 22), (22, 24), (24, 25), (25, 28)]
        + [
            (28, 29),
            (29, 31),
            (31, 32),
            (32, 34),
            (34, 37),
        ]
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
        t = td("264/11")
        t.model.editables = (
            {
                3,
                6,
            }
            | {
                10,
                11,
                13,
                14,
                16,
            }
            | {19, 21, 22, 24, 25}
            | {
                28,
                29,
                31,
                32,
                34,
            }
            | {37, 40, 43}
        )

        t.model.cursor = 99  # controle pas modif, 0 pourrait être faux
        assert t.model.move_cursor(index, Qt.Key_Right) == res

    def test_range_of_type_retenue_chiffre(self, td):
        t = td("264/11")
        t.model.editables = (
            {
                3,
                6,
            }
            | {10, 11, 13, 14, 16}
            | {19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34}
            | {37, 40, 43}
        )
        assert t.model.retenue_gauche == {3, 6, 21, 24}
        assert t.model.retenue_droite == {11, 14, 29, 32}
        assert t.model.regular_chiffre == {
            10,
            13,
            16,
            19,
            22,
            25,
            28,
            31,
            34,
            37,
            40,
            43,
        }

    @pytest.mark.parametrize(
        "index, res",
        [(3, 11), (6, 14), (21, 29), (24, 32)]  # retenue gauche
        + [(11, 22), (14, 25), (29, 40), (32, 43)]  # retenue droite
        + [
            (10, 22),
            (13, 10),
            (16, 13),
            (28, 43),
            (31, 28),
            (34, 31),
        ]  # chiffre imprs
        + [
            (19, 19),
            (22, 19),
            (25, 22),
            (37, 37),
            (40, 37),
            (43, 40),
        ],  # chiff pairs
    )
    def test_automove_next(self, td, index, res):
        #     # 'rows': 5, 'columns': 9, '
        #
        #     # '', 'X', '',  '*', 'Y', '', '*', 'Z',  '' //8
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 17
        #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
        #     # '',  '*', '*', '',  '*', '*', '', '*', '', // 35
        #     # '',  '*', '', '',   '*', '',  '', '*', '' , //44
        t = td("264/11")
        t.model.editables = (
            {
                3,
                6,
            }
            | {10, 11, 13, 14, 16, 17}
            | {18, 19, 21, 22, 24, 25}
            | {28, 29, 31, 32, 34, 35}
            | {37, 40, 43}
        )
        t.datas[13] = 5  # besoni d'une value pour move à la ligne
        t.datas[34] = 1  # besoni d'une value pour move à la ligne

        assert t.model.auto_move_next(index) == res

    @pytest.mark.parametrize(
        "cur, r1, r2", [(22, 3, 11), (25, 6, 14), (40, 21, 29), (43, 24, 32)]
    )
    def test_addRetenues(self, td, cur, r1, r2):
        t = td("264/11")
        t.model.cursor = cur
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""
        # add
        t.model.addRetenues()
        assert t.datas[r1] == "1"
        assert t.datas[r2] == "1"
        # remove
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(31, 12, 20)])
    def test_addRetenuesMemebreline(self, td, cur, r1, r2):
        t = td("264/11")
        t.model.cursor = cur
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""
        # add
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""

    @pytest.mark.parametrize("cur, r1, r2", [(19, 0, 8), (19, 0, 8)])
    def test_addRetenuesOuIlneDoitPasYenAvoir(self, td, cur, r1, r2):
        t = td("264/11")
        t.model.cursor = cur
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""
        # add
        t.model.addRetenues()
        assert t.datas[r1] == ""
        assert t.datas[r2] == ""

    def test_get_last_index_filled(self, td):
        t = td("1/2")
        assert t.model._get_last_index_filled(["", "3", "5", "", "", "4", ""]) == 5
        assert t.model._get_last_index_filled(["", "3", "5", "", "", "", ""]) == 2
        assert t.model._get_last_index_filled(["1", "", "", "", "", "", ""]) == 0
        assert t.model._get_last_index_filled(["", "", "", "", "", "", ""]) == 6
        assert t.model._get_last_index_filled(("", "", "", "", "", "", "")) == 6

    def test_goToResultLine(self, td):
        t = td("264/11")
        t.datas[16] = 9
        t.model.cursor = 13
        t.model.goToResultLine()
        assert t.model.cursor == 25
        t.datas[34] = 9
        t.model.cursor = 31
        t.model.goToResultLine()
        assert t.model.cursor == 43

    def test_goToabaisseLine(self, td):
        t = td("264/11")
        t.datas[22] = 1
        t.model.cursor = 19
        t.model.goToAbaisseLine()
        assert t.model.cursor == 25

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
    def test_getPosByQuotient(self, td, string, quotient, pos, res):
        t = td("264/11")
        # check_args(t.model.getPosByQuotient, None, int)
        t.model.cursor = pos
        t.quotient = quotient
        t.model.getPosByQuotient()
        assert t.model.cursor == res

    def test_Readonly(self, td):
        t = td("264/11")
        #     # ' ', '2', ' ', '*', '6', ' ', '*', '4', ' ' //8
        #     # ' ', '*', '*', ' ', '*', '*', ' ', '*', ' ', // 17
        #     # ' ', '*', ' ', '*', '*', ' ', '*', '*', ' ', // 26
        #     # ' ', '*', '*', ' ', '*', '*', ' ', '*', ' ', // 35
        #     # ' ', '*', ' ', ' ',  '*', ' ', ' ', '*', ' ' , //44
        assert t.model.editables == {34, 37, 40, 10, 43, 13, 16, 19, 22, 25, 28, 31}
        non_compris = set(range(0, t.size)) - t.model.editables
        check_is_range(t, "readOnly", non_compris)

    def test_isEditable(self, td):
        t = td("264/11")
        assert t.model.editables == {34, 37, 40, 10, 43, 13, 16, 19, 22, 25, 28, 31}
        check_is_range(t, "isEditable", t.model.editables)

    def test_is_ligne_dividende(self, td):
        t = td("264/11")
        check_is_range(t, "is_ligne_dividende", range(9))

    def test_is_ligne_last(self, td):
        t = td("264/11")
        check_is_range(t, "is_ligne_last", range(36, 45))

    @pytest.mark.parametrize(
        "string, res",
        [
            # ("5/4", set(range(84)) - {1}),
            (
                "264/11",
                {10, 13, 16, 19, 22, 25} | {28, 31, 34, 37, 40, 43},
            ),
        ],
    )
    def test_get_editables(self, string, res, td):
        t = td(string)
        assert t.model.get_editables() == res

    #     # 'rows': 5, 'columns': 9, '
    #
    #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 17
    #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 35
    #     # '', '*', '', '',   '*', '',  '', '*', '' , //44
