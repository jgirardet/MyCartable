import re
from dataclasses import dataclass
from typing import List

from PySide2.QtCore import Slot, Qt, QObject, QJsonDocument

import logging

LOG = logging.getLogger(__name__)


@dataclass
class Fragment:
    start: int
    end: int
    value: str

    def __len__(self):
        return len(self.value)


class TextEquation:

    FSP = "\u2000"  # espace comblant les espaces dans les fractions
    BARRE = "\u2015"  # barre de fraction
    MUL = "\u00D7"
    SIGNES = ["+", "-", MUL]
    SPACES = [" ", FSP]
    ARROWS = [Qt.Key_Right, Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Return]

    def __init__(self, lines: str, curseur: int, event):
        self.lines_string = lines
        self.lines = lines.split("\n")
        self.curseur = curseur
        self.event = event
        self.key = event["key"]
        self.text = event["text"]
        self.modifiers = event["modifiers"]
        self.line_active = self.lines_string[:curseur].count("\n")
        LOG.debug(
            f"curseur: {self.curseur}, line_active: {self.line_active}, line len: {len(self.lines[0])}\n"
            f"key: {self.key}, char: [{self.text}]"
        )

    def __call__(self):
        new_curseur = getattr(self, "dispatch_line" + str(self.line_active))()
        if new_curseur is None:
            new_curseur = self.curseur

        assert all(len(x) == len(self.lines[0]) for x in self.lines)
        new_string = self.format_lines()
        LOG.debug(
            "TextEquation nouvelle string : %s",
            "\n||"
            + new_string.replace(self.BARRE, "_")
            .replace(self.FSP, "¤")
            .replace("\n", "||\n||")
            .replace(" ", ".")
            + "||",
        )

        return new_string, new_curseur

    @staticmethod
    def debug_string_format(string):
        return (
            "\n||"
            + string.replace(TextEquation.BARRE, "_")
            .replace(TextEquation.FSP, "¤")
            .replace("\n", "||\n||")
            .replace(" ", ".")
            + "||"
        )

    @property
    def debut_line(self) -> List[int]:
        return [0, self.len + 1, self.len * 2 + 2]

    @property
    def debut_line_active(self) -> int:
        return self.debut_line[self.line_active]

    @property
    def line(self) -> str:
        """active ligne"""
        return self.lines[self.line_active]

    @property
    def len(self) -> int:
        return len(self.lines[self.line_active])

    def dispatch_line0(self):
        """ chaque dispatch renvoi un nouveau curseur"""
        if self.key == Qt.Key_Return:
            return self.do_return()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.text:
            return self.fraction_add_char(0)

    def dispatch_line1(self):
        if self.key == Qt.Key_Slash:
            return self.new_fraction()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.text:
            return self.line1_add_char()

    def dispatch_line2(self):
        if self.key == Qt.Key_Return:
            return self.do_return()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.text:
            return self.fraction_add_char(2)

    def dispatch_arrows(self):
        if self.key == Qt.Key_Down:
            return self.do_down()
        elif self.key == Qt.Key_Left:
            return self.do_left()
        elif self.key == Qt.Key_Right:
            return self.do_right()
        elif self.key == Qt.Key_Up:
            return self.do_up()

    def do_down(self):
        if self.line_active == 0:
            return self.do_return()
        elif self.line_active == 1:
            curseur = self.get_line_curseur()
            if curseur > 0 and self.line[curseur - 1] == self.BARRE:
                frag = self.get_stripped(curseur - 1, 2)
                return self.debut_line[2] + frag.start + len(frag)
            elif curseur < self.len and self.line[curseur] == self.BARRE:
                frag = self.get_stripped(curseur, 2)
                return self.debut_line[2] + frag.start + len(frag)
        return self.curseur

    def do_left(self):
        index = self.get_line_curseur() - 1
        if self.line_active == 1:
            while index >= 0:
                val = self.lines[self.line_active][index]
                if val not in [self.BARRE, self.FSP]:
                    return self.debut_line_active + index
                elif (
                    index > 1
                    and self.line[index] == self.BARRE
                    and self.line[index - 1] == " "
                ):
                    return self.debut_line_active + index
                index -= 1
        else:
            while index >= 1:
                val = self.line[index]
                if val not in self.SPACES:
                    return self.debut_line_active + index
                elif val in self.SPACES and self.line[index - 1] not in self.SPACES:
                    return self.debut_line_active + index
                index -= 1
        return self.debut_line_active

    def do_right(self):
        index = self.get_line_curseur()
        if self.line_active == 1:
            while index < self.len:
                val = self.line[index]
                if val not in [self.BARRE, self.FSP]:
                    return self.debut_line_active + index + 1
                elif val == self.BARRE and self.line[index + 1] == " ":
                    return self.debut_line_active + index + 1
                index += 1
            return self.debut_line_active + len(self.line.rstrip(" ").rstrip(self.FSP))
        else:
            while index < self.len - 1:
                val0 = self.line[index]
                val1 = self.line[index + 1]
                if val0 not in self.SPACES:
                    return self.debut_line_active + index + 1
                elif val0 in self.SPACES and val1 not in self.SPACES:
                    return self.debut_line_active + index + 1

                index += 1
            return self.debut_line_active + len(self.line.rstrip(" ").rstrip(self.FSP))

    def do_return(self):
        curseur = self.get_line_curseur()
        if self.line_active == 0:
            start, end = self.fraction_get_start_and_end(curseur)
            f2 = self.lines[2][start:end].rstrip(self.FSP)
            return self.debut_line[2] + start + len(f2)
        elif self.line_active == 2:
            _, end = self.fraction_get_start_and_end(curseur)
            appended = 0
            if end == self.len:
                self.append_at_end(" ")
                appended = 1
            return self.debut_line[1] + end + appended

    def do_up(self):
        curseur = self.get_line_curseur()
        if self.line_active == 1:
            if curseur > 0 and self.line[curseur - 1] == self.BARRE:
                frag = self.get_stripped(curseur - 1, 0)
                return self.debut_line[0] + frag.start + len(frag)
            elif curseur < self.len and self.line[curseur] == self.BARRE:
                frag = self.get_stripped(curseur, 0)
                return self.debut_line[0] + frag.start + len(frag)
        elif self.line_active == 2:
            frag = self.get_stripped(curseur, 0)
            return self.debut_line[0] + frag.start + len(frag)
        return self.curseur

    def append_at_end(self, char):
        for i in range(3):
            self.lines[i] = self.lines[i] + char

    def fraction_add_char(self, n):
        other = 0 if n == 2 else 2  # ligne opposée
        curseur = self.get_line_curseur()

        start, end = self.fraction_get_start_and_end(curseur)

        # creation du fragment et position dans fragment sans les faux espaces
        fragment_current = self.lines[n][start:end].strip(self.FSP)
        if fragment_current:
            f_curseur = (
                curseur
                - start
                - self.lines[n][start:end].rstrip(self.FSP).count(self.FSP)
            )
        else:
            f_curseur = 0

        # decoupage et formattage des fragments
        # fragment_current = fragment_current.strip(self.FSP)
        fragment_current = (
            fragment_current[:f_curseur] + self.text + fragment_current[f_curseur:]
        )
        fragment_other = self.lines[other][start:end].strip(self.FSP)
        len_frac = max(len(fragment_current), len(fragment_other))
        fragment_current = fragment_current.center(len_frac, self.FSP)
        fragment_other = fragment_other.center(len_frac, self.FSP)
        fragment1 = self.BARRE * len_frac

        # on refait les lignes
        self.lines[n] = self.lines[n][:start] + fragment_current + self.lines[n][end:]
        self.lines[1] = self.lines[1][:start] + fragment1 + self.lines[1][end:]
        self.lines[other] = (
            self.lines[other][:start] + fragment_other + self.lines[other][end:]
        )
        # curseur
        new_pos = (
            fragment_current.rstrip(self.FSP).count(self.FSP) + f_curseur + 1
        )  # car 1 char ajouté
        new_curseur = self.debut_line[n] + start + new_pos

        return new_curseur

    def fraction_get_start_and_end(self, line_curseur):
        if line_curseur > 0 and self.lines[1][line_curseur - 1] == self.BARRE:
            line_curseur -= 1  # corrige quand curseur en bout de ligne
        for item in re.finditer(rf"{self.BARRE}+|\s+|\S+", self.lines[1]):
            if item.start() <= line_curseur < item.end():
                return item.start(), item.end()

    def get_line_curseur(self):
        return self.curseur - self.debut_line_active

    def format_lines(self):
        string = "\n".join(self.lines)
        string = string.replace("*", self.MUL)
        return string

    def get_stripped(self, curseur, line):
        start, end = self.fraction_get_start_and_end(curseur)
        frag = self.lines[line][start:end].rstrip(self.FSP)
        return Fragment(start, end, frag)

    def line1_add_char(self):

        curseur = self.get_line_curseur()
        self.lines[0] = self.lines[0][:curseur] + " " + self.lines[0][curseur:]
        self.lines[1] = self.lines[1][:curseur] + self.text + self.lines[1][curseur:]
        self.lines[2] = self.lines[2][:curseur] + " " + self.lines[2][curseur:]
        return self.debut_line[1] + curseur + 1

    def new_fraction(self):
        curseur = self.get_line_curseur()
        start = self.lines[1][:curseur].rfind(" ") + 1  # renvoie -1 si trouve rien
        start = start if start >= 0 else 0  # pas d'espace trouvé avant
        end = self.lines[1][curseur:].find(" ")  # renvoie -1 si trouve rien
        end = end if end != -1 else len(self.lines[1])  # pas d'espace trouvé avant

        fragment = self.lines[1][start:end]

        self.lines[0] = self.lines[0][:start] + fragment + self.lines[0][end:]
        self.lines[1] = (
            self.lines[1][:start] + self.BARRE * len(fragment) + self.lines[1][end:]
        )
        self.lines[2] = (
            self.lines[2][:start] + self.FSP * len(fragment) + self.lines[2][end:]
        )

        return self.debut_line[2] + start
