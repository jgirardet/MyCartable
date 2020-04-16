import functools
import itertools
import operator
import re
from decimal import Decimal, getcontext


def match(string):
    signe = None
    PATTERN = r"\d+[\.,]?\d*([\+-/\*])\d+"
    pattern = re.compile(PATTERN)
    res = pattern.match(string)
    if res:
        signe = res.groups()[0]

    return signe, string.split(signe)


class DecimalLitteral(Decimal):
    def __new__(cls, value, **kw):
        new = Decimal.__new__(cls, value.replace(",", "."), **kw)
        new.int = Decimal(int(new))
        new.dec = new - new.int
        new.string = value.replace(".", ",")
        new.len = len(new.string)
        new.l_int = len(new.int.as_tuple().digits)
        new.l_dec = len(new.dec.as_tuple().digits) if new.dec else 0
        new.l_chiffres = new.l_int + new.l_dec

        return new

    def is_int(self):
        return not bool(self.l_dec)

    def to_string_list_addition(self, size, apres_virgule=0):
        if apres_virgule == 0:
            space_after = 0
        else:
            if self.is_int():
                space_after = apres_virgule + 1
            elif apres_virgule <= self.l_dec:
                space_after = 0
            else:
                space_after = apres_virgule - self.l_dec
        avant = size - self.len - space_after
        return [""] * avant + list(self.string) + [""] * space_after

    def to_string_list_soustraction(self, size, ligne, apres_virgule=0):
        """
        Convertit un nombre en liste de taille `size`. On ne vérifie pas la validité des paramètres.
        :param size: taille de la liste. donnée par line_0 pour line_1. sans intéret pour line 0
        :param ligne: index 0 ou 1
        :param apres_virgule: nombre de chiffres après la virgule à considérer
        :return: liste de charactères
        """
        # size  = total comprenant avant, retenus, entier, virgule decimal
        # algo pas hyper joli mais simple à débugger.

        if apres_virgule == 0:
            if not ligne:
                corps = [""]
                for x in self.string:
                    corps.append("")
                    corps.append(x)
                    corps.append("")
                return corps
            else:
                corps = []
                for x in self.string:
                    corps.append("")
                    corps.append(x)
                    corps.append("")

                avant = []
                if len(corps) + 1 < size:  # le + 1 c pour le signe
                    avant = (size - (len(corps) + 1)) * [""]
                return ["-"] + avant + corps

        else:
            signe = ["-"] if ligne else [""]
            corps = []
            deja_apres_virg = 0
            virg_passee = False
            for x in self.string:
                if virg_passee:
                    deja_apres_virg += 1
                if x != ",":
                    corps.append("")
                corps.append(x)
                if x != ",":
                    corps.append("")
                else:
                    virg_passee = True

            apres = [","] if self.is_int() else []
            apres = apres + ["", "0", ""] * (apres_virgule - deja_apres_virg)
            corps = corps + apres
            avant = []
            if (len(corps) + 1) < size:  # le + 1 c pour le signe
                avant = (size - (len(corps) + 1)) * [""]
            return signe + avant + corps

    def to_string_list_multiplication(self, size):
        len_residuel = size - self.len
        return len_residuel * [""] + list(self.string)

    def to_string_list_division(self, size):
        temp = []
        for n, x in enumerate(self.string):
            if x.isdigit():
                temp += ["", x, ""]
            elif x == ",":
                prev_index = (n - 1) * 3 + 1
                temp[prev_index] = temp[prev_index] + ","

        return temp + [""] * (size - len(temp))


def convert_addition(numbers):
    addition_list = [DecimalLitteral(x) for x in numbers]
    n_col = len(sum(addition_list).to_eng_string()) + 1  # nombre de colonne nécessaire
    n_row = len(numbers) + 2  # nombre de row
    n_apres_virgule = max(a.l_dec for a in addition_list)  # nombre apres vigule
    virgule = n_col - n_apres_virgule - 1 if n_apres_virgule else 0
    res = []

    num_index = 0
    for x in range(n_row):
        if x == 0:
            res.append([""] * n_col)
        elif x == n_row - 1:
            res.append(
                [""] * virgule + [","] + [""] * (n_col - virgule - 1)
            ) if n_apres_virgule else res.append([""] * n_col)
        else:
            num = addition_list[num_index]
            signe = "+" if num_index else ""  # pas de signe pour la premiere ligne
            res.append(
                [signe]
                + num.to_string_list_addition(n_col - 1, apres_virgule=n_apres_virgule,)
            )  # n_col-1 car signe prend une colonne
            num_index += 1
    return n_row, n_col, virgule, list(itertools.chain.from_iterable(res))


def convert_soustraction(numbers):
    res = []
    work_list = [DecimalLitteral(x) for x in numbers]

    n_apres_virgule = max(a.l_dec for a in work_list)  # nombre apres vigule
    n_int = max(x.l_int for x in work_list)
    n_dec = max(x.l_dec for x in work_list)

    n_col = (
        1 + (n_int * 3) + bool(n_apres_virgule) + (n_dec * 3)
    )  # nombre de colonne nécessaire
    virgule = n_col - (n_dec * 3) - 1 if n_apres_virgule else 0

    res.append(work_list[0].to_string_list_soustraction(n_col, 0, n_apres_virgule))
    res.append(work_list[1].to_string_list_soustraction(n_col, 1, n_apres_virgule))
    last = [""] * n_col
    if virgule:
        last[virgule] = ","
    res.append(last)
    return 3, n_col, virgule, list(itertools.chain.from_iterable(res))


def convert_multiplication(numbers):
    work_list = [DecimalLitteral(x) for x in numbers]
    if work_list[0].len != work_list[1].len:
        ligne1 = min(work_list, key=operator.attrgetter("len"))  # membre 2
    else:
        ligne1 = min(work_list)

    if work_list[0] == work_list[1]:
        ligne0 = work_list[0]
    else:
        ligne0 = [i for i in work_list if i != ligne1][0]

    n_chiffres = ligne1.l_dec + ligne1.l_int
    virgule = int(any(x.l_dec for x in work_list))

    n_col = (
        len(functools.reduce(operator.mul, work_list).to_eng_string()) + 1
    )  # nombre de colonne nécessaire

    n_row = 4  # les 2 membres +  1row retenu + res

    if n_chiffres > 1:
        n_row = n_row + (n_chiffres * 2)  # les retenues du haut + n ligne d'addition

    res = []

    res.append([""] * n_col * n_chiffres)  # d'abord les row de retenu
    res.append(ligne0.to_string_list_multiplication(n_col))
    membre2 = ligne1.to_string_list_multiplication(n_col)
    membre2[0] = "x"
    res.append(membre2)
    res.append([""] * n_col)  # ligne resultat/ou permiere de l'addition

    if n_chiffres > 1:
        res.append(
            (["+"] + [""] * (n_col - 1)) * n_chiffres
        )  # ligne d'addition avec + (dont retenu)
        res.append([""] * n_col)  # resultat (sans le plus)

    return n_row, n_col, virgule, list(itertools.chain.from_iterable(res))


def convert_division(numbers):
    work_list = [DecimalLitteral(x) for x in numbers]
    datas = {}
    datas["dividende"] = work_list[0].to_eng_string()
    datas["diviseur"] = work_list[1].to_eng_string()

    context = getcontext()
    prec = 20
    context.prec = prec
    quotient = work_list[0] / work_list[1]
    len_quotient = len(quotient.as_tuple().digits)
    if len_quotient == prec:
        len_quotient = 8  # on fait une longueur max par défault

    n_row = 1 + (len_quotient * 2)
    n_col = (len_quotient + 1) * 3

    ligne0 = work_list[0].to_string_list_division(n_col)
    rab = [""] * (n_col * n_row - len(ligne0))
    datas["datas"] = ligne0 + rab

    virgule = 0

    return n_row, n_col, virgule, datas


def create_operation(string):
    # strip space
    string = string.replace(" ", "")
    # match
    signe, numbers = match(string)

    if signe == "+":
        return convert_addition(numbers)
    elif signe == "-":
        return convert_soustraction(numbers)
    elif signe == "*":
        return convert_multiplication(numbers)
    elif signe == "/":
        return convert_division(numbers)
    else:
        return None


def create_tableau(rows, columns):
    return rows, columns, [[""] * columns for x in range(rows)]
