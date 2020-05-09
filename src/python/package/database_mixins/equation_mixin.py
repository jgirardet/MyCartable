import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from PySide2.QtCore import Slot, Qt, QObject, QJsonDocument
from PySide2.QtGui import QKeyEvent
from package.operations.fractions_parser import three_lines_converter, EquationBuilder
from pony.orm import db_session

import logging

LOG = logging.getLogger(__name__)


# X = "\u2000"


class EquationMixin:
    @Slot(int, str, int, str, int, result="QVariantMap")
    def updateEquation(self, sectionId, content, curseur, event, modifiers):
        event = json.loads(event)
        new_lines, new_curseur = TextEquation(content, curseur, event, modifiers)()
        return {"content": new_lines, "curseur": new_curseur}


class TextEquation:

    FSP = "\u2000"  # espace comblant les espaces dans les fractions
    BARRE = "\u2015"  # barre de fraction
    MUL = "\u00D7"
    SIGNES = ["+", "-", MUL]
    SPACES = [" ", FSP]

    def __init__(self, lines: str, curseur: int, event, modifiers):
        self.lines_string = lines
        self.lines = lines.split("\n")
        self.curseur = curseur
        self.event = event
        self.key = event["key"]
        self.char = event["text"]
        self.mofifiers = event["modifiers"]
        self.line_active = self.lines_string[:curseur].count("\n")
        LOG.debug(
            f"curseur: {self.curseur}, line_active: {self.line_active}, line len: {len(self.lines[0])}\n"
            f"key: {self.key}, char: [{self.char}]"
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

    @property
    def debug_string(self):
        return (
            "\n||"
            + self.format_lines()
            .replace(self.BARRE, "_")
            .replace(self.FSP, "¤")
            .replace("\n", "||\n||")
            .replace(" ", ".")
            + "||"
        )

    @property
    def debut_line0(self):
        return len(self.lines[0]) * 0

    @property
    def debut_line1(self):
        return len(self.lines[0]) * 1 + 1

    @property
    def debut_line2(self):
        return len(self.lines[0]) * 2 + 2

    def dispatch_line0(self):
        """ chaque dispatch renvoi un nouveau curseur"""
        if self.key == Qt.Key_Return:
            return self.do_return()

        elif self.char:
            return self.fraction_add_char(0)

    def dispatch_line1(self):
        if self.key == Qt.Key_Slash:
            return self.new_fraction()
        elif self.key == Qt.Key_Left:
            return self.do_left()
        elif self.key == Qt.Key_Right:
            return self.do_right()

        elif self.char:
            return self.line1_add_char()

    def dispatch_line2(self):
        if self.key == Qt.Key_Return:
            return self.do_return()
        elif self.char:
            return self.fraction_add_char(2)

    def do_left(self):
        index = self.get_line_curseur() - 1
        while index >= 0:
            val = self.lines[self.line_active][index]
            if val not in [self.BARRE, self.FSP]:
                return getattr(self, "debut_line" + str(self.line_active)) + index
            index -= 1
        return self.curseur

    def do_right(self):
        index = self.get_line_curseur() + 1
        while index < len(self.lines[self.line_active]):
            val = self.lines[self.line_active][index]
            if val not in [self.BARRE, self.FSP]:
                return getattr(self, "debut_line" + str(self.line_active)) + index
            index += 1
        return getattr(self, "debut_line" + str(self.line_active)) + len(
            self.lines[self.line_active]
        )

    def do_return(self):
        curseur = self.get_line_curseur()
        num = self.line_active
        if self.line_active == 0:
            start, end = self.fraction_get_start_and_end(curseur)
            f2 = self.lines[2][start:end].rstrip(self.FSP)
            return self.debut_line2 + start + len(f2)
        elif self.line_active == 2:
            _, end = self.fraction_get_start_and_end(curseur)
            return self.debut_line1 + end

        """QUE FAIRe POURe ALLER DANS LA FRACTION"""
        # elif self.line_active == 1:
        #     if self.lines[1][curseur - 1] == self.BARRE:
        #         _, end = self.fraction_get_start_and_end(curseur - 1)
        #         return
        #     elif curseur < len(self.lines[1]) - 2 and self.lines[1][curseur + 1]:
        #         pass

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
            fragment_current[:f_curseur] + self.char + fragment_current[f_curseur:]
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
        new_curseur = getattr(self, "debut_line" + str(n)) + start + new_pos

        return new_curseur

    def fraction_get_start_and_end(self, line_curseur):
        if line_curseur > 0 and self.lines[1][line_curseur - 1] == self.BARRE:
            line_curseur -= 1  # corrige quand curseur en bout de ligne
        for item in re.finditer(rf"{self.BARRE}+|\s+|\S+", self.lines[1]):
            if item.start() <= line_curseur < item.end():
                return item.start(), item.end()

    def get_line_curseur(self):
        return self.curseur - getattr(self, "debut_line" + str(self.line_active))

    def format_lines(self):
        string = "\n".join(self.lines)
        string = string.replace("*", self.MUL)
        return string

    def line1_add_char(self):

        curseur = self.get_line_curseur()
        self.lines[0] = self.lines[0][:curseur] + " " + self.lines[0][curseur:]
        self.lines[1] = self.lines[1][:curseur] + self.char + self.lines[1][curseur:]
        self.lines[2] = self.lines[2][:curseur] + " " + self.lines[2][curseur:]

        # on ajoute un espace systématique à la fin
        if (
            len(self.lines[1]) >= 2
            and self.lines[1][-1] in self.SIGNES
            and self.lines[1][-2] == " "
        ):
            for i in range(3):
                self.lines[i] = self.lines[i] + " "
            curseur += 1

        return self.debut_line1 + curseur + 1

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

        return self.debut_line2 + start
