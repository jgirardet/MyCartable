import re
from dataclasses import dataclass
from typing import List, ClassVar

from PySide2.QtCore import Qt

from loguru import logger


@dataclass
class Fragment:
    start: int
    end: int
    value: str
    line: int
    RE_PARTS: ClassVar[re.Pattern] = re.compile(r"(\u2000*)(\S*)(\u2000*)")

    def __len__(self):
        return len(self.value)

    @property
    def parts(self):
        return self.RE_PARTS.search(self.value).groups()

    def sub(self, index, value):
        self.value = self.value[:index] + value + self.value[index + 1 :]


class TextEquation:

    FSP = "\u2000"  # espace comblant les espaces dans les fractions
    BARRE = "\u2015"  # barre de fraction
    MUL = "\u00D7"
    SIGNES = ["+", "-", MUL]
    SPACES = [" ", FSP]
    ARROWS = [Qt.Key_Right, Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Return]
    RE_FIND_FRACTION = re.compile(rf"{BARRE}+|\s+|\S+")

    def __init__(self, lines: str, curseur: int, event):
        self.lines_string = lines
        self.lines = lines.split("\n")
        self.curseur = curseur
        self.event = event
        self.key = event["key"]
        self.text = event["text"]
        self.modifiers = event["modifiers"]
        self.line_active = self.lines_string[:curseur].count("\n")
        logger.debug(
            f"curseur: {self.curseur}, line_active: {self.line_active}, line len: {len(self.lines[0])}\n"
            f"key: {self.key}, char: [{self.text}]"
        )

    def __call__(self):

        if not self.lines_string:
            if self.text and self.key != Qt.Key_Return:
                return f" \n{self.text}\n ", 3
            else:
                return "", 0

        new_curseur = getattr(self, "dispatch_line" + str(self.line_active))()
        if new_curseur is None:
            new_curseur = self.curseur

        assert all(len(x) == len(self.lines[0]) for x in self.lines), self.lines
        new_string = self.format_lines()
        log_string = (
            "\n||"
            + new_string.replace(self.BARRE, "_")
            .replace(self.FSP, "¤")
            .replace("\n", "||\n||")
            .replace(" ", ".")
            + "||"
        )
        logger.debug(f"TextEquation nouvelle string : {log_string}",)

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

    @line.setter
    def line(self, value):
        self.lines[self.line_active] = value

    @property
    def len(self) -> int:
        return len(self.lines[self.line_active])

    def dispatch_line0(self):
        """ chaque dispatch renvoi un nouveau curseur"""
        if self.key == Qt.Key_Return:
            return self.do_return()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.key == Qt.Key_Backspace:
            return self.do_backspace()
        elif self.key == Qt.Key_Space:
            return self.curseur
        elif self.text:  # pragma: no branch
            return self.fraction_add_char(0)

    def dispatch_line1(self):
        if self.key == Qt.Key_Slash:
            return self.new_fraction()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.key == Qt.Key_Backspace:
            return self.do_backspace()
        elif self.text:  # pragma: no branch
            return self.line1_add_char()

    def dispatch_line2(self):
        if self.key == Qt.Key_Return:
            return self.do_return()
        elif self.key in self.ARROWS:
            return self.dispatch_arrows()
        elif self.key == Qt.Key_Backspace:
            return self.do_backspace()
        elif self.key == Qt.Key_Space:
            return self.curseur
        elif self.text:  # pragma: no branch
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

    def do_backspace(self):
        if self.line_active == 1:
            index = self.get_line_curseur()
            if index > 0 and self.line[index - 1] != self.BARRE:
                for i in range(3):
                    self.lines[i] = self.lines[i][: index - 1] + self.lines[i][index:]
                return self.curseur - 2

        else:
            index = self.get_line_curseur()
            if index > 0 and self.line[index - 1] not in self.SPACES:
                frag = self.get_unstripped(index, self.line_active)
                f_index = index - frag.start  # index dans le fragment FSP inclus
                fsp_pre = len(frag.parts[0])  # FSP avant l'index
                nb_avant = (
                    f_index - fsp_pre - 1
                )  # nb char avant index (on enleve le deleté)
                frag.sub(f_index - 1, self.FSP)  # on remplace le delete par FSP
                membres = self.format_fraction(frag)
                new_fsp_pre = (
                    membres[self.line_active].rstrip(self.FSP).count(self.FSP)
                )  # nb FSP avant après format
                new_pos = new_fsp_pre + nb_avant  # nouvelle pos dans le fragement
                for i in range(3):
                    self.lines[i] = (
                        self.lines[i][: frag.start]
                        + membres[i]
                        + self.lines[i][frag.end :]
                    )
                if not any(membres):  # on efface la fraction
                    return self.debut_line[1] + frag.start
                else:
                    return self.debut_line_active + frag.start + new_pos
        return self.curseur

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
        elif self.line_active == 2:  # pragma: no branch
            _, end = self.fraction_get_start_and_end(curseur)
            appended = 0
            if end == self.len:
                # breakpoint()
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
        for item in self.RE_FIND_FRACTION.finditer(self.lines[1]):
            if item.start() <= line_curseur < item.end():
                return item.start(), item.end()

    def get_line_curseur(self):
        return self.curseur - self.debut_line_active

    def format_lines(self):
        string = "\n".join(self.lines)
        string = string.replace("*", self.MUL)
        return string

    @property
    def is_focusable(self):
        curseur = self.get_line_curseur()
        if self.line_active == 1:
            if (  # cas du clique au milieu d'une barre
                curseur > 0
                and curseur < self.len
                and self.line[curseur - 1] == self.BARRE
                and self.line[curseur] == self.BARRE
            ):
                return False
            else:
                return True
        else:
            # cas simple c'est déjà un caratère
            if curseur < self.len and self.line[curseur] not in self.SPACES:
                return True
            # on précise les choses dans les fractions
            res = self.fraction_get_start_and_end(curseur)
            # curseur pas dans fractions : ouste
            if res is None:
                return False
            else:
                start, end = res
                if all(x == self.FSP for x in self.line[start:end]):
                    return True
                elif curseur > 0 and self.line[curseur - 1] not in self.SPACES:
                    return True
                # elif ( # juste commenté, au cas ou ce soit util....
                #     curseur < self.len - 1
                #     and self.line[curseur + 1] not in self.SPACES
                #     and self.line[curseur] not in self.SPACES
                # ):
                #     breakpoint()
                #     return True
            return False

    def get_stripped(self, curseur, line):
        start, end = self.fraction_get_start_and_end(curseur)
        frag = self.lines[line][start:end].rstrip(self.FSP)
        return Fragment(start, end, frag, line)

    def get_unstripped(self, curseur, line):
        start, end = self.fraction_get_start_and_end(curseur)
        frag = self.lines[line][start:end]
        return Fragment(start, end, frag, line)

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

    def format_fraction(self, frag):
        # L'utiliser en modif, pas en ajout
        other = 2 if frag.line == 0 else 0
        fragment_current = frag.value.replace(self.FSP, "")
        fragment_other = self.lines[other][frag.start : frag.end].replace(self.FSP, "")
        len_frac = max(len(fragment_current), len(fragment_other))
        fragment_current = fragment_current.center(len_frac, self.FSP)
        fragment_other = fragment_other.center(len_frac, self.FSP)
        fragment1 = self.BARRE * len_frac

        if frag.line == 0:
            return fragment_current, fragment1, fragment_other
        else:
            return fragment_other, fragment1, fragment_current
