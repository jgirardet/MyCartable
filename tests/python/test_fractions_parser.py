import pytest
from package.operations.fractions_parser import *
from parsy import ParseError

un = Nombre("1")
deux = Nombre("2")
quinze = Nombre("15")
plus = Signe("+")
moins = Signe("-")
fois = Signe("*")
egale = Signe("=")
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
nd_plus_un = Noeud(plus, m_un)
nd_plus_quinze = Noeud(plus, m_quinze)
nd_plus_un_moins_quinze = Noeud(plus, m_op_un_moins_quinze)
nd_plus_un_moins_quinze_plus_deux = Noeud(plus, m_op_un_moins_quinze_plus_deux)
nd_plus_un_sur_quinze = Noeud(plus, m_f_un_sur_quinze)
nd_un_moins_quinze_sur_un_moins_quinze_plus_deux = Noeud(
    plus, m_f_un_moins_quinze_sur_un_moins_quinze_plus_deux
)
nd_plus_e_un_moins_quinze = Noeud(plus, m_e_un_moins_quinze)


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
        # (noeud, "+ 1", nd_plus_un),
        # (noeud, "+ 15", nd_plus_quinze),
        # (noeud, "+ 1-15", nd_plus_un_moins_quinze),
        # (noeud, "+ 1-15+2", nd_plus_un_moins_quinze_plus_deux),
        # (noeud, "+ 1/15", nd_plus_un_sur_quinze),
        # (noeud, "+ 1-15/1-15+2", nd_un_moins_quinze_sur_un_moins_quinze_plus_deux,),
        # (noeud, "+ (1-15)", nd_plus_e_un_moins_quinze,),
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


@pytest.fixture()
def f():
    return FractionParser()


class TestFractionParser:
    def test_read(self, f):
        f.read("pmojlihku")
        assert f.len == 9
        assert f.string == "pmojlihku"
