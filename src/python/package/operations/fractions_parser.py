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

#
# class Matched:
#     def __init__(self, match_item, level):
#         self.m = match_item
#         self.l = level
#
#     def __lt__(self, other):
#         if self.m.start() < other.m.start():
#             return True
#         elif self.m.start() == other.m.start():
#             if self.l.value > other.l.value:
#                 print(self.l.value)
#                 return True
#         else:
#             False
#
#     def __repr__(self):
#         return (
#             f"Matched {self.l.name} {self.m.start()},{self.m.end()} : {self.m.group()}"
#         )


def three_lines_converter(string: str):
    # on separe
    lines = string.splitlines()
    lines[1] = re.sub(r"_+", "/", lines[1])

    # on match par ligne que l'on transforme en Matched pour les comparer
    # indexes_haut = [Matched(m, Level.haut) for m in NO_WHITE_SPACE.finditer(lines[0])]
    indexes_milieu = list(WHITE_SPACE_AND_CONTENT.finditer(lines[1]))
    ]
    # indexes_bas = [Matched(m, Level.bas) for m in NO_WHITE_SPACE.finditer(lines[2])]

    total = indexes_haut + indexes_bas + indexes_milieu

    # on ordonne par start() et par Level
    total.sort()

    # res = "".join((x.m.group() for x in total))

    res = []
    for m in indexes_milieu:
        texte = m.m.group()
        if "_" in texte:
            res.append(lines[0][m.m.start() : m.m.end()])
            res.append(texte)
            res.append(lines[2][m.m.start() : m.m.end()])
        else:
            res.append(texte)

    return "".join(res)

    return sorted(total)


"""
A partir d'ici on parcours le la "ligne" et on crée les string finales
Principe : on écrit sur 3 lignes à la fois
"""


class EquationBuilder:
    def __init__(self, string=""):
        self.string = string

    def on_expression(self, el):
        el = el.v
        self.add("(")
        self.on_operation(el)
        self.add(")")

    def on_fraction(self, el):
        self.debut_fraction = self.len
        # numerateur
        self.level = H
        self.dispatch(el.n.v)
        print(self.listes[H], "pares disp")
        numerateur = self.listes[H][self.debut_fraction : self.len + 1]
        print(numerateur, "num")

        # changement de niveau
        # self.move_fragment_up()

        print(self.listes)
        self.level = B
        # denominateur
        self.dispatch(el.d.v)
        denominateur = self.listes[B][self.debut_fraction : self.len + 1]
        print(denominateur)
        print(self.listes)

        # finalize
        len_frac = max(len(numerateur), len(denominateur))
        print(len_frac)
        self.add("_", level=M, many=len_frac, auto=False)

    def on_membre(self, el):
        el = el.v
        self.debut_membre = self.len
        self.dispatch(el)

    def on_operateur(self, el):
        self.add(el.si.v)
        self.add(el.v.v)

    def on_operation(self, el):
        self.add(el.v.v)
        for op in el.ops:
            self.on_operateur(op)

    def on_terme(self, el):
        self.add(el.v)

    def on_signe(self, el):
        # if self.prev_is_space:
        self.add(el.v)

    @staticmethod
    def build_ast(string):
        return ligne.parse(string)

    # @property
    # def prev_is_space(self):
    #     try:
    #         return all(x[-1] == " " for x in self.listes)
    #     except IndexError:
    #         return False

    def add(self, v, level=None, many=1, auto=True):
        level = level if level else self.level

        for i in range(many):
            if level == M:
                for i in Level:
                    if i == level:
                        self.listes[level].append(v)
                    elif auto:
                        self.listes[i].append(" ")
            elif level == H:
                self.listes[H].append(v)
            elif level == B:
                self.listes[B].append(v)

    def dispatch(self, el):
        if isinstance(el, Terme):
            self.on_terme(el)
        elif isinstance(el, Operation):
            self.on_operation(el)
        elif isinstance(el, Expression):
            self.on_expression(el)
        elif isinstance(el, Div):
            self.on_div()
        elif isinstance(el, Fraction):
            self.on_fraction(el)

    @property
    def len(self):
        return len(self.listes[M])

    def merge_listes(self):
        res = (
            "".join(self.listes[H])
            + "\n"
            + "".join(self.listes[M])
            + "\n"
            + "".join(self.listes[B])
        )
        return res

    @property
    def data(self):
        return self.merge_listes()

    # def move_fragment_up(self):
    #     fragment = self.listes[M][self.debut_membre : self.len]
    #     print(fragment)
    #     self.listes[H] = self.listes[H][: self.debut_membre] + fragment
    #     self.listes[M] = self.listes[M][: self.debut_membre] + ["_"] * len(fragment)

    def reset_class(self):
        self.b = []
        self.listes = {H: [], M: [], B: []}
        self.level = M
        self.debut_membre = None

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
                self.add(" ")

        return self.data


# def on_membre(mb):
#     if isinstance(mb, Terme):


#
# def build_result(string):
#     ast  = build_ast(string)
#     res = ["", "", ""]
#
