import pytest
from package.operations.fractions_parser import *
from parsy import ParseError

un = Nombre("1")
deux = Nombre("2")
quinze = Nombre("15")
plus = Signe("+")
moins = Signe("-")
fois = Signe("*")


@pytest.mark.parametrize(
    "parser, string, res",
    [
        (nombre, "1", un),
        (nombre, "0123456789", Nombre("0123456789")),
        (nombre, "a", None),
        (space, "", None),
        (space, " ", Space),
        (space, "     ", Space),
        (signe, "+", plus),
        (signe, "-", moins),
        (signe, "*", fois),
        (div, "/", Div),
        # (signe, "-+", None),
        # (membre, "+ 1", Membre(plus, Space, un)),
        # (membre, "- 15", Membre(moins, Space, quinze)),
        # (membre, "-15", None),
        (operateur, "-15", Operateur(moins, quinze)),
        (operation, "1-15", Operation(un, [Operateur(moins, quinze)])),
        (ligne, "1 + 15", None),
        # (operation, "1-15+1", [un, moins, quinze, plus, un]),
        # (operation, "1 - 15", [Nombre("1"), Space, Membre(moins, Space, quinze)]),
        # (operation, "1-15", None),
        # (
        #     operation,
        #     "1 - 15 + 2",
        #     [
        #         Nombre("1"),
        #         Space,
        #         Membre(moins, Space, quinze),
        #         Membre(moins, Space, deux),
        #     ],
        # ),
    ],
)
def test_parser(parser, string, res):
    msg = ""
    try:
        temp = parser.parse(string)
    except ParseError as err:
        temp = None
        msg = str(err)
    assert temp == res, msg


@pytest.fixture()
def f():
    return FractionParser()


class TestFractionParser:
    def test_read(self, f):
        f.read("pmojlihku")
        assert f.len == 9
        assert f.string == "pmojlihku"
