import random

import pytest
from package.operations.fractions_parser import *
from parsy import ParseError

un = Terme("1")
deux = Terme("2")
quinze = Terme("15")
plus = Signe("+")
moins = Signe("-")
fois = Signe("*")
egale = Signe("=")
sp = Space()
moins_quinze = Operateur(moins, quinze)
plus_deux = Operateur(plus, deux)
fois_op_un_mois_quinze = Operateur(fois, Operation(un, [moins_quinze]))
op_un = Operation(un, [])
op_quinze = Operation(quinze, [])
op_un_moins_quinze = Operation(un, [moins_quinze])
op_un_moins_quinze_plus_deux = Operation(un, [moins_quinze, plus_deux])
# op_b_un_moins_quinze = Operation(un, [moins_quinze])
e_un_moins_quinze = Expression(op_un_moins_quinze)
e_un_moins_un_moins_quinze = Expression(
    Operation(un, [Operateur(moins, e_un_moins_quinze)])
)
moins_un_moins_quinze = Operateur(moins, e_un_moins_quinze)
op_un_moins_un_moins_quinze = Operation(un, [moins_un_moins_quinze])
n_un = Numerateur(un)
n_un_moins_quinze = Numerateur(op_un_moins_quinze)
d_quinze = Denominateur(quinze)
d_un_moins_quinze_plus_deux = Denominateur(op_un_moins_quinze_plus_deux)
f_un_sur_quinze = Fraction(n_un, d_quinze)
f_un_moins_qinze_sur_quinze = Fraction(n_un_moins_quinze, d_quinze)
f_un_sur_un_moins_quinze_plus_deux = Fraction(n_un, d_un_moins_quinze_plus_deux)
f_un_moins_quinze_sur_un_moins_quinze_plus_deux = Fraction(
    n_un_moins_quinze, d_un_moins_quinze_plus_deux
)
m_un = Membre(un)
m_quinze = Membre(quinze)
m_op_un_moins_quinze = Membre(op_un_moins_quinze)
m_op_un_moins_quinze_plus_deux = Membre(op_un_moins_quinze_plus_deux)
m_f_un_sur_quinze = Membre(f_un_sur_quinze)
m_f_un_moins_qinze_sur_quinze = Membre(f_un_moins_qinze_sur_quinze)
m_f_un_moins_quinze_sur_un_moins_quinze_plus_deux = Membre(
    f_un_moins_quinze_sur_un_moins_quinze_plus_deux
)
m_e_un_moins_quinze = Membre(e_un_moins_quinze)


@pytest.mark.parametrize(
    "parser, string, res",
    [
        (terme, "1", un),
        (terme, "0123456789", Terme("0123456789")),
        (terme, "a", Terme("a")),
        (terme, "A", Terme("A")),
        (space, "", None),
        (space, " ", sp),
        (space, "     ", sp),
        (signe, "+", plus),
        (signe, "-", moins),
        (signe, "*", fois),
        (signe, "=", egale),
        (div, "/", Div),
        (operateur, "-15", moins_quinze),
        (operateur, "-15", moins_quinze),
        (operateur, "*1-15", None),
        (operateur, "-(1-15)", moins_un_moins_quinze),
        (operation, "1", None),
        (operation, "1-15", op_un_moins_quinze),
        (operation, "1-15+2", op_un_moins_quinze_plus_deux),
        (operation, "1/15", None),
        (operation, "1-(1-15)", op_un_moins_un_moins_quinze),
        (operation, "(1-15)-15", Operation(e_un_moins_quinze, [moins_quinze]),),
        (
            operation,
            "(1-15)-(1-15)",
            Operation(e_un_moins_quinze, [Operateur(moins, e_un_moins_quinze)]),
        ),
        (expression, "(1-15)", e_un_moins_quinze),
        (expression, "(1-(1-15))", e_un_moins_un_moins_quinze,),
        (numerateur, "1", n_un),
        (numerateur, "1-15", n_un_moins_quinze),
        (numerateur, "1-15+2", Numerateur(op_un_moins_quinze_plus_deux)),
        (numerateur, "(1-15)", Numerateur(e_un_moins_quinze)),
        (numerateur, "(1-(1-15))", Numerateur(e_un_moins_un_moins_quinze)),
        (
            numerateur,
            "(1-15)-(1-15)",
            Numerateur(
                Operation(e_un_moins_quinze, [Operateur(moins, e_un_moins_quinze)])
            ),
        ),
        (denominateur, "15", d_quinze),
        (denominateur, "1-15+2", d_un_moins_quinze_plus_deux),
        (denominateur, "(1-15)", Denominateur(e_un_moins_quinze)),
        (denominateur, "(1-(1-15))", Denominateur(e_un_moins_un_moins_quinze)),
        (
            denominateur,
            "(1-15)-(1-15)",
            Denominateur(
                Operation(e_un_moins_quinze, [Operateur(moins, e_un_moins_quinze)])
            ),
        ),
        (fraction, "1/15", f_un_sur_quinze),
        (fraction, "1/1-15+2", f_un_sur_un_moins_quinze_plus_deux),
        (fraction, "1-15/15", f_un_moins_qinze_sur_quinze),
        (fraction, "1-15/1-15+2", f_un_moins_quinze_sur_un_moins_quinze_plus_deux),
        (fraction, "1-15/1-15+2", f_un_moins_quinze_sur_un_moins_quinze_plus_deux),
        (
            fraction,
            "(1-15)/(1-15)",
            Fraction(Numerateur(e_un_moins_quinze), Denominateur(e_un_moins_quinze)),
        ),
        (membre, "1", m_un),
        (membre, "15", m_quinze),
        (membre, "1-15", m_op_un_moins_quinze),
        (membre, "1-15+2", m_op_un_moins_quinze_plus_deux),
        (membre, "1/15", m_f_un_sur_quinze),
        (membre, "1-15/15", m_f_un_moins_qinze_sur_quinze),
        (membre, "1-15/1-15+2", m_f_un_moins_quinze_sur_un_moins_quinze_plus_deux),
        (membre, "(1-15)", m_e_un_moins_quinze),
        (ligne, "1", [m_un]),
        (ligne, "1 ", [m_un]),
        (ligne, " 1 ", [m_un]),
        (ligne, " 1", [m_un]),
        (ligne, "1 + 15", [m_un, plus, m_quinze]),
        (ligne, "1 + 15 ", [m_un, plus, m_quinze]),
        (ligne, " 1 + 15 ", [m_un, plus, m_quinze]),
        (ligne, "1 + 15 + 1", [m_un, plus, m_quinze, plus, m_un]),
        (ligne, "1-15", [m_op_un_moins_quinze]),
        (ligne, "1-15 + 1", [m_op_un_moins_quinze, plus, m_un]),
        (ligne, "1/15", [m_f_un_sur_quinze]),
        (ligne, "1/15 + 1", [m_f_un_sur_quinze, plus, m_un]),
        (ligne, "1 + 1/15", [m_un, plus, m_f_un_sur_quinze]),
        (
            ligne,
            "1-15/1-15+2 * 1/15 - 1-15+2",
            [
                m_f_un_moins_quinze_sur_un_moins_quinze_plus_deux,
                fois,
                m_f_un_sur_quinze,
                moins,
                m_op_un_moins_quinze_plus_deux,
            ],
        ),
        (ligne, "(1-15)", [m_e_un_moins_quinze]),
        (ligne, "1 - (1-15)", [m_un, moins, m_e_un_moins_quinze]),
        (ligne, "(1-15) - 1", [m_e_un_moins_quinze, moins, m_un]),
        (ligne, "(1-15) = 1/15", [m_e_un_moins_quinze, egale, m_f_un_sur_quinze]),
    ],
)
def test_parser(parser, string, res):
    msg = ""
    try:
        temp = parser.parse(string)
    except ParseError as err:
        temp = None
        msg = str(err)
    print(res)
    assert temp == res, msg


@pytest.mark.parametrize(
    "parser, string, res",
    [
        (ligne, "1", [m_un]),
        (ligne, "1 ", [m_un]),
        (ligne, " 1 ", [m_un]),
        (ligne, " 1", [m_un]),
        (ligne, "1 + 15", [m_un, plus, m_quinze]),
        (ligne, "1 + 15 ", [m_un, plus, m_quinze]),
        (ligne, " 1 + 15 ", [m_un, plus, m_quinze]),
        (ligne, "1 + 15 + 1", [m_un, plus, m_quinze, plus, m_un]),
        (ligne, "1-15", [m_op_un_moins_quinze]),
        (ligne, "1-15 + 1", [m_op_un_moins_quinze, plus, m_un]),
        (ligne, "1/15", [m_f_un_sur_quinze]),
        (ligne, "1/15 + 1", [m_f_un_sur_quinze, plus, m_un]),
        (ligne, "1 + 1/15", [m_un, plus, m_f_un_sur_quinze]),
        (
            ligne,
            "1-15/1-15+2 * 1/15 - 1-15+2",
            [
                m_f_un_moins_quinze_sur_un_moins_quinze_plus_deux,
                fois,
                m_f_un_sur_quinze,
                moins,
                m_op_un_moins_quinze_plus_deux,
            ],
        ),
        (ligne, "(1-15)", [m_e_un_moins_quinze]),
        (ligne, "1 - (1-15)", [m_un, moins, m_e_un_moins_quinze]),
        (ligne, "(1-15) - 1", [m_e_un_moins_quinze, moins, m_un]),
        (ligne, "(1-15) = 1/15", [m_e_un_moins_quinze, egale, m_f_un_sur_quinze]),
    ],
)
def test_parser_3_lines_to_one(parser, string, res):
    msg = ""
    try:
        temp = parser.parse(string)
    except ParseError as err:
        temp = None
        msg = str(err)
    print(res)
    assert temp == res, msg


@pytest.fixture()
def eb():

    eqbuild = EquationBuilder()
    eqbuild.reset_class()
    return eqbuild


class TestEquationBuilder:
    def test_build_ast(self, eb):
        assert eb.build_ast("1 + 1/15") == [m_un, plus, m_f_un_sur_quinze]

    # on test ici les utility

    @pytest.mark.parametrize("",[(),])
    def test_(self, ):
      
            
                
    def test_add(self, eb):
        eb.level = M
        eb.add("+")
        assert eb.listes == {H: [" "], M: ["+"], B: [" "]}
        eb.add("X", many=3 )
        assert eb.listes == {H: [" XXX"], M: ["+XXX"], B: [" "]}

        eb.level = H
        eb.add("1")
        assert eb.listes == {H: [" ", "1"], M: ["+"], B: [" "]}

    # def test_is_prev_space(self, eb):
    #     eb.add(" ")
    #     assert eb.prev_is_space
    #     eb.add("+")
    #     assert not eb.prev_is_space

    def test_merge_listes(self, eb):
        eb.add("+", M)
        eb.add("5", M)
        eb.add("2", M)
        assert eb.merge_listes() == "   \n+52\n   "

    def test_len(self, eb):
        for i in range(3):
            eb.add("4", random.randint(0, 3))
        assert all(len(v) == eb.len for v in eb.listes.values())

    def test_data(self, eb):
        eb("1+4")
        assert eb.merge_listes() == eb.data

    #
    # def test_move_fragment_up(self, eb):
    #     eb.listes = {M: ["1", " ", "1", "+", "2"], H: [" "] * 5, B: [" "] * 5}
    #     eb.debut_membre = 2
    #     eb.move_fragment_up()
    #     assert eb.listes == {
    #         H: [" ", " ", "1", "+", "2"],
    #         M: ["1", " ", "_", "_", "_"],
    #         B: [" "] * 5,
    #     }


@pytest.mark.parametrize(
    "string, res",
    [
        ("1", " \n1\n "),
        ("1 + 2", "     \n1 + 2\n     "),
        ("1 + 1+2", " " * 7 + "\n1 + 1+2\n" + " " * 7),
        ("1 * (3+4)", " " * 9 + "\n1 * (3+4)\n" + " " * 9),
        ("1/2", "1\n_\n2"),
    ],
)
def test_output(string, res):
    assert EquationBuilder(string)() == res



def test_from_3_to_one_line()