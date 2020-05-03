from dataclasses import dataclass, field
from typing import List, Union

from parsy import regex, string, seq, generate


@dataclass
class Nombre:
    value: str


@dataclass
class Signe:
    value: str


class Div:
    pass


class Space:
    pass


class OpenBrace:
    pass


class CloseBrace:
    pass


@dataclass
class Operateur:
    si: Signe
    rhs: Union[Nombre, "Operation"]


@dataclass
class Operation:
    lhs: Union[Nombre]
    op: List[Operateur] = field(default=None)  # d'operateur


@dataclass
class Expression:
    lhs: Union[Nombre, "Operation"]
    # si: Signe
    # rhs: Union[Nombre, "Operation"]


@dataclass
class Numerateur:
    v: Expression


@dataclass
class Denominateur:
    v: Expression


@dataclass
class Fraction:
    n: Numerateur  # operation
    d: Denominateur  # operation


@dataclass
class Membre:
    v: object  # nombren exp, frac


@dataclass
class Noeud:
    s: Signe
    m: Membre


@dataclass
class Ligne:
    f: Membre  # first
    n: List[Noeud] = field(default=None)  # mais le parser mettra [] si none


space = (
    regex(r"\s+").map(lambda x: " ").map(lambda x: Space).desc("1 ou plusieurs espaces")
)
signe = regex(r"[\+\-\*]").map(Signe).desc("signe: +,-,*")
div = string("/").map(lambda x: Div).desc("slash délimite les fractions")
open_brace = string("(").map(lambda x: OpenBrace)
close_brace = string(")").map(lambda x: CloseBrace)

nombre = regex(r"[0-9]+").map(Nombre).desc("des chiffres")
# operateur = seq(signe, (nombre | operation)).combine(Operateur).desc("signe + nombre")


@generate("operation entre parenthèse")
def expression():
    yield open_brace
    lhs = yield operation
    yield close_brace
    return Expression(lhs)  # , si, rhs)


@generate("signe + (nombre ou expression)")
def operateur():
    si = yield signe
    rhs = yield (nombre | expression)
    return Operateur(si, rhs)


@generate("nombre + 1 ou plusieurs opérateurs")
def operation():
    nb, liste = yield seq(nombre | expression, operateur.at_least(1))
    return Operation(nb, liste)


forme = (operation | nombre | expression).desc("operation ou nombre ou expression")
numerateur = forme.map(Numerateur).desc("une forme")
denominateur = forme.map(Denominateur).desc("denominateur")
fraction = (
    seq(numerateur << div, denominateur)
    .combine(Fraction)
    .desc("numerateur div denominateur")
)
membre = (fraction | forme).map(Membre).desc("operation ou fraction")
noeud = seq(signe << space, membre).combine(Noeud).desc("signe + space + membre")


@generate("membre seul ou membre + noeud")
def ligne():
    first = yield membre
    noeuds = yield (space.optional() >> noeud).many()
    print(noeuds)
    yield space.optional()
    return Ligne(first, noeuds)


class FractionParser:
    def read(self, string):
        self.string = string
        self.len = len(string)


res = ligne.parse("1-15/1-15+2 + 1/15 + 1-15+2")
