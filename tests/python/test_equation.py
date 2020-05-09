import textwrap

import pytest
from PySide2.QtCore import Qt
from package.operations.equation import TextEquation, Fragment

UN = """
||1¤............¤12...1234....||
||__.+.13.+.3.+.___.+.____.+.1||
||15............234...789¤....||"""
# 0123456789012345678901234567
#          10        20
# len 28
# touche : [0,1,2,15,16,17, 20 ,21,24, 31,
# 32,33,34,35,36,57,58,59,60,72,73,74,75,78,79,80,81

deux = """
||1¤.......2||
||__.+.1.+._||
||15.......2||"""
# 0123456789 # len = 10 fin =32


def format_fixture(val):
    return (
        val.lstrip("\n")
        .replace("|", "")
        .replace("¤", TextEquation.FSP)
        .replace(".", " ")
        .replace("_", TextEquation.BARRE)
    )


@pytest.fixture()
def un():
    return format_fixture(UN)


@pytest.fixture()
def e_un(un):
    return TextEquation(un, 31, {"key": Qt.Key_A, "text": "a", "modifiers": None})


@pytest.fixture()
def eq():
    def factory(
        string=deux, curseur=31, event={"key": Qt.Key_A, "text": "a", "modifiers": None}
    ) -> TextEquation:
        if string.startswith("\n||"):
            string = format_fixture(string)
        return TextEquation(string, curseur, event)

    return factory


class TestTextEquation:
    def test_init(self, e_un, un):
        assert e_un.lines_string == un
        assert e_un.lines == un.split("\n")
        assert e_un.event == {"key": Qt.Key_A, "text": "a", "modifiers": None}
        assert e_un.key == Qt.Key_A
        assert e_un.text == "a"
        assert e_un.modifiers == None
        assert e_un.line_active == 1

    def test_property(self, e_un):
        assert e_un.debut_line[0] == 0
        assert e_un.debut_line[1] == 29
        assert e_un.debut_line[2] == 58
        assert e_un.debut_line_active == 29
        assert e_un.line == e_un.lines[1]
        assert e_un.len == 28

    def test_append_at_end(self, eq):
        a = eq(string="1\n_\n2")
        backup = a.lines
        a.append_at_end(" ")
        assert a.format_lines() == "1 \n_ \n2 "

    @pytest.mark.parametrize(
        "curseur, res",
        [(0, 0), (3, 3), (9, 9), (10, 10),]
        + [(11, 0), (13, 2), (19, 8), (20, 9), (21, 10),]
        + [(22, 0), (24, 2), (29, 7), (31, 9), (32, 10),],
    )
    def test_get_line_curseur(self, eq, curseur, res):
        a = eq(curseur=curseur)
        assert a.get_line_curseur() == res

    @pytest.mark.parametrize(
        "cur, res",
        [
            (0, (0, 2)),
            (1, (0, 2)),
            (2, (0, 2)),
            (14, (14, 17)),
            (15, (14, 17)),
            (16, (14, 17)),
            (17, (14, 17)),
            (20, (20, 24)),
            (21, (20, 24)),
            (22, (20, 24)),
            (23, (20, 24)),
            (24, (20, 24)),
        ],
    )
    def test_fraction_get_start_and_end(self, eq, cur, res):
        a = eq(UN, curseur=cur)
        assert a.fraction_get_start_and_end(cur) == res

    def test_format_lines(self, eq):
        a = eq("1\n*\n2")
        assert a.format_lines() == f"1\n{TextEquation.MUL}\n2"

    @pytest.mark.parametrize(
        "cur, line, res",
        [
            (0, 0, (0, 2, "1")),
            (1, 0, (0, 2, "1")),
            (2, 0, (0, 2, "1")),
            (14, 0, (14, 17, f"{TextEquation.FSP}12")),
            (15, 0, (14, 17, f"{TextEquation.FSP}12")),
            (16, 0, (14, 17, f"{TextEquation.FSP}12")),
            (17, 0, (14, 17, f"{TextEquation.FSP}12")),
            (20, 0, (20, 24, "1234")),
            (21, 0, (20, 24, "1234")),
            (22, 0, (20, 24, "1234")),
            (23, 0, (20, 24, "1234")),
            (24, 0, (20, 24, "1234")),
        ]
        + [
            (0, 2, (0, 2, "15")),
            (1, 2, (0, 2, "15")),
            (2, 2, (0, 2, "15")),
            (14, 2, (14, 17, "234")),
            (15, 2, (14, 17, "234")),
            (16, 2, (14, 17, "234")),
            (17, 2, (14, 17, "234")),
            (20, 2, (20, 24, "789")),
            (21, 2, (20, 24, "789")),
            (22, 2, (20, 24, "789")),
            (23, 2, (20, 24, "789")),
            (24, 2, (20, 24, "789")),
        ],
    )
    def test_get_stripped(self, eq, cur, line, res):
        a = eq(UN)
        assert a.get_stripped(cur, line) == Fragment(*res)

    @pytest.mark.parametrize(
        "cur, key, text, res, res_c",
        [
            (
                0,
                Qt.Key_A,
                "a",
                """
||a1............¤12...1234....||
||__.+.13.+.3.+.___.+.____.+.1||
||15............234...789¤....||""",
                1,
            ),
            (
                1,
                Qt.Key_A,
                "a",
                """
||1a............¤12...1234....||
||__.+.13.+.3.+.___.+.____.+.1||
||15............234...789¤....||""",
                2,
            ),
            (
                15,
                Qt.Key_A,
                "a",
                """
||1¤............a12...1234....||
||__.+.13.+.3.+.___.+.____.+.1||
||15............234...789¤....||""",
                15,
            ),
            (
                16,
                Qt.Key_A,
                "a",
                """
||1¤............1a2...1234....||
||__.+.13.+.3.+.___.+.____.+.1||
||15............234...789¤....||""",
                16,
            ),
            (
                17,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............12a...1234....||
                    ||__.+.13.+.3.+.___.+.____.+.1||
                    ||15............234...789¤....||"""
                ),
                17,
            ),
            (
                20,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...a1234....||
                    ||__.+.13.+.3.+.___.+._____.+.1||
                    ||15............234...¤789¤....||"""
                ),
                21,
            ),
            (
                21,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1a234....||
                    ||__.+.13.+.3.+.___.+._____.+.1||
                    ||15............234...¤789¤....||"""
                ),
                22,
            ),
            (
                24,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234a....||
                    ||__.+.13.+.3.+.___.+._____.+.1||
                    ||15............234...¤789¤....||"""
                ),
                25,
            ),
            (
                31,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__a.+.13.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                33,
            ),
            (
                32,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__.a+.13.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                34,
            ),
            (
                33,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__.+a.13.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                35,
            ),
            (
                34,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__.+.a13.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                36,
            ),
            (
                35,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__.+.1a3.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                37,
            ),
            (
                36,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤.............¤12...1234....||
                    ||__.+.13a.+.3.+.___.+.____.+.1||
                    ||15.............234...789¤....||"""
                ),
                38,
            ),
            (
                57,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234.....||
                    ||__.+.13.+.3.+.___.+.____.+.1a||
                    ||15............234...789¤.....||"""
                ),
                59,
            ),
            (
                58,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||¤1¤............¤12...1234....||
                    ||___.+.13.+.3.+.___.+.____.+.1||
                    ||a15............234...789¤....||"""
                ),
                61,
            ),
            (
                59,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||¤1¤............¤12...1234....||
                    ||___.+.13.+.3.+.___.+.____.+.1||
                    ||1a5............234...789¤....||"""
                ),
                62,
            ),
            (
                60,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||¤1¤............¤12...1234....||
                    ||___.+.13.+.3.+.___.+.____.+.1||
                    ||15a............234...789¤....||"""
                ),
                63,
            ),
            (
                72,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12¤...1234....||
                    ||__.+.13.+.3.+.____.+.____.+.1||
                    ||15............a234...789¤....||"""
                ),
                75,
            ),
            (
                73,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12¤...1234....||
                    ||__.+.13.+.3.+.____.+.____.+.1||
                    ||15............2a34...789¤....||"""
                ),
                76,
            ),
            (
                74,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12¤...1234....||
                    ||__.+.13.+.3.+.____.+.____.+.1||
                    ||15............23a4...789¤....||"""
                ),
                77,
            ),
            (
                75,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12¤...1234....||
                    ||__.+.13.+.3.+.____.+.____.+.1||
                    ||15............234a...789¤....||"""
                ),
                78,
            ),
            (
                78,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234....||
                    ||__.+.13.+.3.+.___.+.____.+.1||
                    ||15............234...a789....||"""
                ),
                79,
            ),
            (
                79,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234....||
                    ||__.+.13.+.3.+.___.+.____.+.1||
                    ||15............234...7a89....||"""
                ),
                80,
            ),
            (
                80,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234....||
                    ||__.+.13.+.3.+.___.+.____.+.1||
                    ||15............234...78a9....||"""
                ),
                81,
            ),
            (
                81,
                Qt.Key_A,
                "a",
                textwrap.dedent(
                    """
                    ||1¤............¤12...1234....||
                    ||__.+.13.+.3.+.___.+.____.+.1||
                    ||15............234...789a....||"""
                ),
                82,
            ),
        ],
    )
    def test_call_UN_text_exist(self, eq, cur, key, text, res, res_c):
        a = eq(UN, cur, {"key": key, "text": text, "modifiers": None})
        res_string, res_cur = a()
        assert TextEquation.debug_string_format(res_string) == res
        assert res_cur == res_c

    @pytest.mark.parametrize(
        "cur, cur_res",
        [(0, 1), (1, 15), (2, 15), (15, 16), (16, 17), (17, 20), (21, 22), (24, 24)]
        + [
            (29, 31),
            (31, 32),
            (32, 33),
            (33, 34),
            (43, 46),
            (47, 48),
            (49, 53),
            (57, 57),
        ]
        + [(58, 59), (59, 60), (60, 72), (72, 73), (75, 78), (81, 81)],
    )
    def test_call_move_right(self, eq, cur, cur_res):
        _, new_cur = eq(UN, cur, {"key": Qt.Key_Right, "text": "", "modifiers": None})()
        assert new_cur == cur_res

    @pytest.mark.parametrize(
        "cur, cur_res",
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (15, 1),
            (16, 15),
            (17, 16),
            (21, 20),
            (20, 17),
            (24, 23),
        ]
        + [
            (29, 29),
            (31, 29),
            (32, 31),
            (33, 32),
            (43, 42),
            (46, 43),
            (47, 46),
            (49, 48),
            (53, 49),
            (57, 56),
        ]
        + [(58, 58), (59, 58), (60, 59), (72, 60), (75, 74), (78, 75), (81, 80)],
    )
    def test_call_move_left(self, eq, cur, cur_res):
        _, new_cur = eq(UN, cur, {"key": Qt.Key_Left, "text": "", "modifiers": None})()
        assert new_cur == cur_res

    @pytest.mark.parametrize(
        "cur, cur_res",
        [(0, 0), (24, 24),]
        + [
            (29, 1),
            (31, 1),
            (32, 32),
            (43, 17),
            (44, 17),
            (46, 17),
            (49, 24),
            (50, 24),
            (53, 24),
            (57, 57),
        ]
        + [
            (58, 1),
            (59, 1),
            (60, 1),
            (72, 17),
            (73, 17),
            (75, 17),
            (78, 24),
            (79, 24),
            (81, 24),
        ],
    )
    def test_call_move_up(self, eq, cur, cur_res):
        _, new_cur = eq(UN, cur, {"key": Qt.Key_Up, "text": "", "modifiers": None})()
        assert new_cur == cur_res

    @pytest.mark.parametrize(
        "cur, cur_res",
        [
            (0, 60),
            (1, 60),
            (2, 60),
            (15, 75),
            (16, 75),
            (17, 75),
            (20, 81),
            (21, 81),
            (24, 81),
        ]
        + [
            (29, 60),
            (31, 60),
            (32, 32),
            (43, 75),
            (44, 75),
            (46, 75),
            (49, 81),
            (50, 81),
            (53, 81),
            (57, 57),
        ]
        + [(58, 58), (81, 81),],
    )
    def test_call_move_down(self, eq, cur, cur_res):
        _, new_cur = eq(UN, cur, {"key": Qt.Key_Down, "text": "", "modifiers": None})()
        assert new_cur == cur_res

    @pytest.mark.parametrize(
        "cur, cur_res",
        [
            (0, 60),
            (1, 60),
            (2, 60),
            (15, 75),
            (16, 75),
            (17, 75),
            (20, 81),
            (21, 81),
            (24, 81),
        ]
        + [(29, 29), (44, 44), (57, 57),]
        + [
            (58, 31),
            (59, 31),
            (60, 31),
            (72, 46),
            (73, 46),
            (75, 46),
            (78, 53),
            (79, 53),
            (81, 53),
        ],
    )
    def test_call_move_return(self, eq, cur, cur_res):
        _, new_cur = eq(
            UN, cur, {"key": Qt.Key_Return, "text": "\n", "modifiers": None}
        )()
        assert new_cur == cur_res
