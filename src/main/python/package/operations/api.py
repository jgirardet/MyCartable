import itertools
import re
from decimal import Decimal


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

        return new

    def is_int(self):
        return not bool(self.l_dec)

    def to_string_list(self, size, apres_virgule=0):
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
                [signe] + num.to_string_list(n_col - 1, apres_virgule=n_apres_virgule,)
            )  # n_col-1 car signe prend une colonne
            num_index += 1
    return n_row, n_col, virgule, list(itertools.chain.from_iterable(res))


def create_operation(string):
    # strip space
    string = string.replace(" ", "")
    # match
    signe, numbers = match(string)

    if signe == "+":
        return convert_addition(numbers)
    else:
        return None
