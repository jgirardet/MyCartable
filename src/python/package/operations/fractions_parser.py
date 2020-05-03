from dataclasses import dataclass, field
from enum import Enum
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
    si: Signe
    v: Union[Terme, "Operation"]


@dataclass
class Operation:
    v: Union[Terme]
    ops: List[Operateur] = field(default=None)  # d'operateur


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
    n: Numerateur
    d: Denominateur


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
A partir d'ici on parcours le la "ligne" et on crée les string finales
Principe : on écrit sur 3 lignes à la fois
"""


class Niveau(Enum):
    haut = 0
    milieu = 1
    bas = 2


class EquationBuilder:
    def __init__(self, string=""):
        self.string = string

    def on_expression(self, el):
        el = el.v
        self.add_au_milieu("(")
        self.on_operation(el)
        self.add_au_milieu(")")

    def on_membre(self, el):
        el = el.v
        if isinstance(el, Terme):
            self.add_au_milieu(el.v)
        elif isinstance(el, Operation):
            self.on_operation(el)
        elif isinstance(el, Expression):
            self.on_expression(el)

    def on_operateur(self, el):
        self.add_au_milieu(el.si.v)
        self.add_au_milieu(el.v.v)

    def on_operation(self, el):
        self.add_au_milieu(el.v.v)
        for op in el.ops:
            self.on_operateur(op)

    def on_signe(self, el):
        if self.prev_is_space:
            self.add_au_milieu(el.v)

    @staticmethod
    def build_ast(string):
        return ligne.parse(string)

    @property
    def prev_is_space(self):
        try:
            return all(x[-1] == " " for x in self.listes)
        except IndexError:
            return False

    def add_au_milieu(self, v):
        self.h.append(" ")
        self.m.append(v)
        self.b.append(" ")

    def merge_listes(self):
        return "\n".join(("".join(x) for x in self.listes))

    def reset_class(self):
        self.h = []
        self.m = []
        self.b = []
        self.listes = [self.h, self.m, self.b]
        self.niveau = 1

    def __call__(self, string=None):
        if string:
            self.string = string
        self.reset_class()
        self.ast = self.build_ast(self.string)
        for el in self.ast:
            if isinstance(el, Signe):
                self.on_signe(el)
            elif isinstance(el, Membre):
                self.on_membre(el)
            if el != self.ast[-1]:
                self.add_au_milieu(" ")

        return self.merge_listes()


# def on_membre(mb):
#     if isinstance(mb, Terme):


#
# def build_result(string):
#     ast  = build_ast(string)
#     res = ["", "", ""]
#
