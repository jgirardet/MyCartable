import re
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering
from typing import List, Union

from parsy import regex, string, seq, generate


@dataclass
class Terme:
    v: str


@dataclass
class Signe:
    v: str


class Div:
    pass


class Base:
    pass


@dataclass
class Space:
    pass


class OParenthese:
    pass


class FParenthese:
    pass


@dataclass
class Operateur:
    signe: Signe
    rhs: Union[Terme, "Operation", "Expression"]


@dataclass
class Operation:
    lhs: Union[Terme]
    operateurs: List[Operateur] = field(default=None)  # d'operateur


@dataclass
class Expression:
    v: Union[Terme, "Operation"]


@dataclass
class Numerateur:
    v: Union[Terme, Expression, Operation]


@dataclass
class Denominateur:
    v: Union[Terme, Expression, Operation]


@dataclass
class Fraction:
    numerateur: Numerateur
    denominateur: Denominateur


@dataclass
class Membre:
    v: Union[Terme, Expression, Operation, Fraction]


""" 
Les différents parseurs primitifs sont ici    
"""


space = regex(r"\s+").map(lambda x: Space()).desc("one or more space")
signe = regex(r"[\+\-\*=]").map(Signe).desc("un signe parmis +,-,*, =")
div = string("/").map(lambda x: Div).desc("/ délimiteur fraction")
o_parenthese = string("(").map(lambda x: OParenthese)
f_parenthese = string(")").map(lambda x: FParenthese)
terme = regex(r"[0-9a-zA-Z]+").map(Terme).desc("des chiffres")

"""
Parseurs avancés. sous forme de generate du fait de recursion
"""


@generate("operation entre parenthèse")
def expression():
    yield o_parenthese
    lhs = yield operation
    yield f_parenthese
    return Expression(lhs)  # , si, rhs)


@generate("signe + (terme ou expression)")
def operateur():
    si = yield signe
    rhs = yield (terme | expression)
    return Operateur(si, rhs)


@generate("terme + 1 ou plusieurs opérateurs")
def operation():
    nb, liste = yield seq(terme | expression, operateur.at_least(1))
    return Operation(nb, liste)


forme = (operation | terme | expression).desc("operation ou terme ou expression")
numerateur = forme.map(Numerateur).desc("une forme")
denominateur = forme.map(Denominateur).desc("denominateur")
fraction = (
    seq(numerateur << div, denominateur)
    .combine(Fraction)
    .desc("numerateur div denominateur")
)
membre = (fraction | forme).map(Membre).desc("forme ou fraction")


@generate("membre seul ou membre + noeud")
def ligne():
    yield space.optional()
    pl = (membre << space.optional()) | (signe << space)
    noeuds = yield pl.at_least(1)
    return noeuds


"""
    Zone three line converter
"""


class Level(Enum):
    haut = 1
    milieu = 0
    bas = -1


H = Level.haut
M = Level.milieu
B = Level.bas

NO_WHITE_SPACE = re.compile(r"\S+")
WHITE_SPACE_AND_CONTENT = re.compile(r"\S+|\s+")


def three_lines_converter(string: str):

    # on separe
    lines = string.splitlines()

    # on recupere chaque space et fragment
    indexes_milieu = list(WHITE_SPACE_AND_CONTENT.finditer(lines[1]))

    # on boucle et on ajoute num et denom  quand ___
    res = []
    for m in indexes_milieu:
        texte = m.group()
        if "_" in texte:
            res.append(lines[0][m.start() : m.end()].replace(" ", ""))
            res.append(texte)
            res.append(lines[2][m.start() : m.end()].replace(" ", ""))
        else:
            res.append(texte)

    # retourne la chaine remplaçant les ___ par /
    return re.sub(r"_+", "/", "".join(res))


"""
A partir d'ici on parcours le la "ligne" et on crée les string finales
Principe : on écrit sur 3 lignes à la fois
"""


class EquationBuilder:
    def __init__(self, string=""):
        self.string = string

    def on_expression(self, el):
        self.append(self.level, "(")
        if self.level == M:
            self.append_space()
        self.dispatch(el.v)
        self.append(self.level, ")")
        if self.level == M:
            self.append_space()

    def on_fraction(self, el):
        self.debut_fraction = self.len

        # numerateur
        self.level = H
        self.dispatch(el.numerateur.v)
        numerateur = self.listes[H][self.debut_fraction : len(self.listes[H])]

        # denominateur
        self.level = B
        self.dispatch(el.denominateur.v)
        denominateur = self.listes[B][self.debut_fraction : len(self.listes[B])]

        # finalize
        len_frac = max(len(numerateur), len(denominateur))
        self.append(H, numerateur.center(len_frac), self.debut_fraction)
        self.append(B, denominateur.center(len_frac), self.debut_fraction)
        self.append(M, "_" * len_frac, self.debut_fraction)

        # on repasse en mode standard
        self.level = M

    def on_membre(self, el):
        el = el.v
        self.debut_membre = self.len
        self.dispatch(el)

    def on_operateur(self, el):
        self.dispatch(el.signe)
        self.dispatch(el.rhs)

    def on_operation(self, el):
        self.dispatch(el.lhs)
        self.dispatch(el.operateurs)

    def on_terme(self, el):
        self.append(self.level, el.v)
        if self.level == M:
            self.append_space(nb=len(el.v))

    def on_signe(self, el):
        self.append(self.level, el.v)
        if self.level == M:
            self.append_space(nb=len(el.v))

    @staticmethod
    def build_ast(string):
        return ligne.parse(string)

    def append(self, level, value, start=None):
        level = level if level is not None else self.level
        self.listes[level] = self.listes[level][:start] + value

    def append_space(self, *, nb=1):
        self.append(H, " " * nb)
        self.append(B, " " * nb)

    def dispatch(self, el):
        if isinstance(el, Terme):
            self.on_terme(el)
        if isinstance(el, Signe):
            self.on_signe(el)
        elif isinstance(el, Operation):
            self.on_operation(el)
        elif isinstance(el, Operateur):
            self.on_operateur(el)
        elif isinstance(el, Expression):
            self.on_expression(el)
        elif isinstance(el, Fraction):
            self.on_fraction(el)
        elif isinstance(el, list):
            for sub_el in el:
                self.dispatch(sub_el)

    @property
    def len(self):
        return len(self.listes[M])

    def merge_listes(self):
        res = "\n".join((x for x in self.listes.values()))
        return res

    @property
    def data(self):
        return self.merge_listes()

    def reset_class(self):
        self.b = []
        self.listes = {H: "", M: "", B: ""}
        self.level = M
        self.debut_membre = None

    def __call__(self, string=None):
        if string:
            self.string = string
        self.reset_class()
        self.ast = self.build_ast(self.string)
        for n, el in enumerate(self.ast):
            if isinstance(el, Signe):
                self.on_signe(el)
            elif isinstance(el, Membre):
                self.on_membre(el)
            if n != len(self.ast) - 1:
                # on ajoute l'espace entre les membres
                self.append(M, " ")
                self.append_space()

        return self.data
