import itertools
import re


def match(string):
    signe = None
    PATTERN = r"\d+([\+-/\*])\d+"
    pattern = re.compile(PATTERN)
    res = pattern.match(string)
    if res:
        signe = res.groups()[0]

    return signe, string.split(signe)


def convert_addition(numbers):
    m = len(str(sum(map(int, numbers)))) + 1  # nombre de colonne nécessaire
    n = len(numbers) + 2  # nombre de row
    res = []

    num_index = 0
    for x in range(n):
        if x == 0 or x == n - 1:
            res.append([""] * m)
        else:
            num = numbers[num_index]
            signe = "+" if num_index else ""  # pas de signe pour la premiere ligne
            o = m - len(num) - 1  # espaces à compléter
            res.append([signe] + [""] * o + list(num))
            num_index += 1

    # TODO: refaire l'algo à l'occasion
    return n, m, list(itertools.chain.from_iterable(res))


def create_operation(string):
    # strip space
    string = string.replace(" ", "")

    # match
    signe, numbers = match(string)
    if not signe:
        return None

    if signe == "+":
        return convert_addition(numbers)
