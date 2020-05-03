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
    lhs: Union[Nombre, "Operation"]
    op: List[Operateur] = field(default=None)  # d'operateur
    brace: bool = field(default=False)


@dataclass
class Expression:
    v: object


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


@generate("signe + (nombre ou operation entre parenthese))")
def operateur():
    si = yield signe
    rhs = yield (nombre | operation)
    return Operateur(si, rhs)


@generate("nombre + 1 ou plusieurs opérateurs")
def operation():
    open_b = yield open_brace.optional()
    nb, liste = yield seq(nombre, operateur.many())
    # nb, liste = yield seq(nombre, operateur.many())
    if open_b:
        yield close_brace
    return Operation(nb, liste, bool(open_b))


numerateur = operation.map(Numerateur).desc("une operation")
denominateur = operation.map(Denominateur).desc("une operation")
fraction = (
    seq(numerateur << div, denominateur)
    .combine(Fraction)
    .desc("numerateur div denominateur")
)
membre = (fraction | operation).map(Membre).desc("operation ou fraction")
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
