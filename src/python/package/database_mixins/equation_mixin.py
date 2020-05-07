import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QKeyEvent
from package.operations.fractions_parser import three_lines_converter, EquationBuilder
from pony.orm import db_session

import logging

LOG = logging.getLogger(__name__)


SIGNES = ["*", "+", "-"]


class EquationMixin:
    # @Slot(int, str, int, int, int, result="QVariantMap")
    # def updateEquation(self, sectionId, content, curseur, key, modifiers):
    #     lines = content.splitlines()

    def _line1_added(self, lines: List[str], curseur, key, modifiers):
        line0, line1, line2 = lines

        if key == Qt.Key_Slash:
            # on ne toucha pas à la ligne opposé pendant que pas fini de éditer

            # définition des fragments
            space_avant, cut_index = self._get_split_position_line1(
                line0, line1, curseur
            )
            print(space_avant, cut_index)
            line1_avant = line1[:space_avant] if space_avant else ""
            fragment = line1[space_avant:cut_index]
            line1_apres = line1[cut_index + 1 :]

            line0_avant = line0[:space_avant]
            line0_apres = line0[cut_index:]

            line2_avant = line0[:space_avant]
            line2_apres = line0[cut_index:]
            print(
                f":{line0_avant}:\n:{line0_apres}:\n:{line1_avant}:\n:{line1_apres}:\n:{line2_avant}:\n:{line2_apres}:"
            )
            # réassemlbage des fragments
            line0 = line0_avant + fragment + line0_apres
            line1 = line1_avant + "_" * len(fragment) + line1_apres
            line2 = line2_avant + " " * len(fragment) + line2_apres
            assert len(line0) == len(line1), f"{ len(line0)} {len(line1)}"
            assert len(line1) == len(line2), f"{ len(line1)} {len(line2)}"

            curseur = len(line0) + len(line1) + 2

        else:
            rel_curseur = curseur - len(line1) - 1  # position relative dans ligne
            rel_curseur = rel_curseur + 1 if rel_curseur >= 0 else 0
            print("rel_curseur ", rel_curseur)

            facteur = 1
            if len(line1) >= 3 and line1[-2] in SIGNES and line1[-3] == " ":
                line1 = line1[:-1] + " " + line1[-1]
                facteur = 2

            line0 = line0 + " " * facteur
            line2 = line2 + " " * facteur

            curseur = len(line0) + 1 + rel_curseur + (facteur - 1)
        return [line0, line1, line2], curseur

    def _line0_added(self, lines: List[str], curseur, key, modifiers):
        line0, line1, line2 = lines

        if key == Qt.Key_Space:
            curseur = len(line0) + len(line1) + 2 + int(len(line0) / 2)
        else:
            # on enleve 1 pour êtr sur de tomber dedans et curseur minimum = 1
            start, end = self._find_membre_by_cursor(line0, curseur - 1)

            # on complète les autres lignes
            line1 = line1[: end - 1] + "_" + line1[end - 1 :]
            line2 = line2[: end - 1] + " " + line2[end - 1 :]

            # line2 forcément < line0 donc on format ligne 2 en fonction de line0
            centered = line2[start:end].strip().center(end - start)
            line2 = line2[:start] + centered + line2[end:]
        return [line0, line1, line2], curseur

    def _transform_equation(
        self, content: str, curseur: int, key: int, modifiers: int = None
    ):
        ligne_active = self._get_cursor_line(content, curseur)
        # print(ligne_active)
        lines = content.splitlines()
        new_curseur = curseur
        # premier caractère
        if len(lines) == 2:
            lines = ["", lines[1], ""]

        if ligne_active == 1:
            new_lines, new_curseur = self._line1_added(lines, curseur, key, modifiers)
        elif ligne_active == 0:
            new_lines, new_curseur = self._line0_added(lines, curseur, key, modifiers)

        return ("\n".join(new_lines), new_curseur)

    @staticmethod
    def _get_cursor_line(string, cursor):
        return string[:cursor].count("\n")

    @staticmethod
    def _get_split_position_line1(line0, line1, curseur):
        """get les index du fragment  relatif à la ligne """
        rel = curseur - len(line0) - 2  # on enleve \n deline0  et / révement ajouté
        rel = rel if rel > 0 else 0
        space_avant = line1[:rel].rfind(" ") + 1  # renvoie -1 si trouve rien
        space_avant = space_avant if space_avant > 0 else 0  # pas d'espace trouvé avant
        # print(space_avant, rel)
        return space_avant, rel

    @staticmethod
    def _find_membre_by_cursor(line: str, cursor: int):
        for i in re.finditer(r"\S+|\s+", line):
            if i.start() <= cursor < i.end():
                return i.start(), i.end()

    # def
    #
    #     with db_session:
    #         item = self.db.EquationSection.get(id=sectionId)
    #         if not item:
    #             LOG.error(f"Aucune EquationSection avec if = {sectionId}")
    #             return {}
    #         item.set(content=rebuiled, curseur=curseur)
    #         res = item.to_dict()
    #         print("return update", res)
    #         return res
