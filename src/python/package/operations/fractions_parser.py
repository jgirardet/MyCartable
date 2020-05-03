from dataclasses import dataclass
from parsy import regex, string, seq


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


@dataclass
class Operateur:
    signe: Signe
    nombre: Nombre


@dataclass
class Operation:
    lhs: Nombre
    op: list  # d'operateur


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
    e: Space
    m: Membre


space = (
    regex(r"\s+").map(lambda x: " ").map(lambda x: Space).desc("1 ou plusieurs espaces")
)
signe = regex(r"[\+\-\*]").map(Signe).desc("signe: +,-,*")
div = string("/").map(lambda x: Div).desc("slash délimite les fractions")

nombre = regex(r"[0-9]+").map(Nombre).desc("des chiffres")
operateur = seq(signe, nombre).combine(Operateur).desc("signe + nombre")
operation = (
    seq(nombre, operateur.at_least(0))
    .combine(Operation)
    .desc("nombre + 1 ou plusieurs opérateurs")
)
expression = (nombre | operation).map(Expression).desc("nombre ou operation")
numerateur = expression.map(Numerateur).desc("une expression")
denominateur = expression.map(Denominateur).desc("une expression")
fraction = (
    seq(numerateur, Div, denominateur)
    .combine(Fraction)
    .desc("numerateur div denominateur")
)
membre = (
    (nombre | expression | fraction).map(Membre).desc("nombre, expression ou fraction")
)
noeud = seq(signe, space, membre).combine(Noeud).desc("signe + space + membre")
ligne = seq(membre, space, noeud.at_least(0)).desc("membre + 1 ou plusieurs noeuds")
#
# operateur = nombre | .map(Operateur).desc("nombre ou fraction")
# membre = seq(signe, space, operateur).combine(Membre).desc("signe + espace + nombre")
# operation = seq(nombre, space, membre)


class FractionParser:
    def read(self, string):
        self.string = string
        self.len = len(string)
