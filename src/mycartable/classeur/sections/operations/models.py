import functools
import operator

from PySide2.QtCore import (
    Qt,
    QModelIndex,
    Signal,
    Property,
    QAbstractItemModel,
    QAbstractListModel,
    Slot,
    QObject,
)

from pony.orm import db_session, make_proxy
from functools import cached_property


class OperationModel(QAbstractListModel):

    cursorChanged = Signal()
    paramsChanged = Signal()

    def __init__(self, parent: "Operation" = None):
        super().__init__(parent)
        self._cursor = 0
        self.editables = self.get_editables() or {}
        self.custom_params_load()
        self.cursor = self.getInitialPosition()

    """
    Pure Python code
    """

    # @Slot()
    def getInitialPosition(self):
        pos = self.get_initial_position()
        a = pos if pos is not None else self.operation.size - 1
        return a

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.operation.datas[index.row()]
            return value

    def flags(self, index):
        if not index.isValid():
            return
        return super().flags(index) | Qt.ItemIsEditable

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.operation.size

    def setData(self, index, value, role, move=True) -> bool:
        if index.isValid() and role == Qt.EditRole:
            self.operation.update_datas(index.row(), value)
            self.dataChanged.emit(index, index)
            if move and "," not in value:
                self.autoMoveNext(index.row())
            return True
        return False

    def get_editables(self):
        return {}

    """
    Qt Property
    """

    @Property(QObject, constant=True)
    def operation(self):
        return self.parent()

    @Property(int, notify=cursorChanged)
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor_set(self, value: int):
        if value != self._cursor:
            self._cursor = value
            self.cursorChanged.emit()

    """
    Qt SLot
    """

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    @Slot(int, int)
    def moveCursor(self, index, key):
        res = self.move_cursor(index, key)
        if res != index:  # pragma: no branch
            self.cursor = res

    @Slot(int, result=bool)
    def readOnly(self, value):
        return value not in self.editables

    @Slot(int, result=bool)
    def isMiddleLine(self, index):
        return not self.isResultLine(index) and not self.isRetenueLine(index)

    @Slot(int, result=bool)
    def isMembreLine(self, index):
        return self.isMiddleLine(index)

    @Slot(int, result=bool)
    def isResultLine(self, index):
        return self.is_result_line(index)

    @Slot(int, result=bool)
    def isRetenueLine(self, index):
        return self.is_retenue_line(index)

    # fonction overidable par subclass

    def auto_move_next(self, position):
        return position

    def custom_params_load(self):
        pass

    def get_initial_position(self):
        return None

    def is_result_line(self, index):
        return False

    def is_retenue_line(self, index):
        return False

    def move_cursor(self, index, key):
        return self.cursor


# TODO : get colomn from index and get row from index


class AdditionModel(OperationModel):
    def auto_move_next(self, position):
        if (
            position == self.rowCount() - self.operation.columns + 1
        ):  # début de ligne résultat
            return position
        elif position > self.operation.columns:  # reste ligne résutlat
            diff = self.rowCount() - position
            new = int(self.operation.columns - diff - 1)
            if new == self.operation.virgule:
                new -= 1  # saute la virgule dans les retenues
        else:  # le haut
            new = self.operation.columns * (self.operation.rows - 1) + position
        return new

    def get_editables(self):
        first_line = {x for x in range(1, self.operation.columns - 1)}
        last_line = {
            x
            for x in range(
                self.operation.size - self.operation.columns + 1, self.operation.size
            )
        }
        res = first_line | last_line
        if self.operation.virgule:
            virgule_ll = (
                self.operation.size - self.operation.columns + self.operation.virgule
            )
            res = res - {self.operation.virgule, virgule_ll}

        return res

    def is_result_line(self, index):
        return index >= self.rowCount() - self.operation.columns

    def is_retenue_line(self, index):
        return 0 <= index and index < self.operation.columns

    def move_cursor(self, index, key):
        new = self.cursor
        if key == Qt.Key_Up:
            temp = index - self.operation.columns * (self.operation.rows - 1)
            if temp == self.operation.columns - 1:
                new = temp - 1
            elif temp > 0:
                new = temp
        elif key == Qt.Key_Down:
            temp = index + self.operation.columns * (self.operation.rows - 1)
            if temp <= self.rowCount():
                new = temp
        elif key == Qt.Key_Left:
            if index - 1 in self.editables:
                new = index - 1
            elif index - 2 in self.editables:
                new = index - 2
        elif key == Qt.Key_Right:
            if index + 1 in self.editables:
                new = index + 1
            elif index + 2 in self.editables:
                new = index + 2

        return new


class SoustractionModel(OperationModel):
    def get_initial_position(self):
        return self.operation.size - 2

    def auto_move_next(self, position):
        factor = 0
        if (
            (position - 3) % self.operation.columns
            < self.operation.virgule
            < position % self.operation.columns
        ):
            factor = 1
        return (
            position - 3 - factor
            if position - 3 - factor in self.editables
            else position
        )

    @Slot(int, result=bool)
    def isRetenueGauche(self, index):
        return index in self.retenue_gauche

    @Slot(int, result=bool)
    def isRetenueDroite(self, index):
        return index in self.retenue_droite

    @Slot()
    def addRetenues(self):
        r1 = self.cursor - (self.operation.columns * 2) - 1
        r2 = self.cursor - self.operation.columns - 2
        if self.operation.datas[r2] == ",":
            r2 -= 1
        if r1 not in self.retenue_gauche or r2 not in self.retenue_droite:
            return

        res = "" if self.operation.datas[r1] == "1" else "1"
        self.setData(self.index(r1), res, Qt.EditRole, move=False)
        self.setData(self.index(r2), res, Qt.EditRole, move=False)

    def is_result_line(self, index):
        return index >= self.operation.columns * 2

    def is_retenue_line(self, index):
        """retenu == fistr line"""
        return 0 <= index and index < self.operation.columns

    @cached_property
    def retenue_gauche(self):
        res = set()
        i = 4
        while i < self.operation.columns:

            # si on dépasse la virgule on ajoute 1, 1 seul fois
            if self.operation.datas[i] == ",":
                i += 1
            res.add(i)
            i += 3
        return res

    @cached_property
    def retenue_droite(self):
        res = set()
        i = 3 + self.operation.columns
        while i < self.operation.columns * 2 - 1:

            # si on dépasse la virgule on ajoute 1, 1 seul fois
            if self.operation.datas[i - 2] == ",":
                i += 1
            res.add(i)
            i += 3

        return res

    def move_cursor(self, index, key):
        new = self.cursor
        if key == Qt.Key_Right:
            temp = index + 3
            if temp in self.editables:
                new = temp
            elif index % self.operation.columns >= self.operation.columns - 4:
                pass
            elif temp + 1 in self.editables:  # pragma: no branch
                new = temp + 1
        elif key == Qt.Key_Left:
            temp = index - 3
            if temp in self.editables:
                new = temp
            # elif self.operation.datas[temp].isdigit() or self.operation.datas[temp] == ",":
            #     new = temp - 1
            elif self.operation.datas[temp + 1] == ",":
                new = temp - 1
        elif key == Qt.Key_Up:
            new = index
        elif key == Qt.Key_Down:  # pragma: no branch
            new = index
        return new

    @property
    def line_0(self):
        return self.operation.datas[0 : self.operation.columns]

    @property
    def line_1(self):
        return self.operation.datas[self.operation.columns : self.operation.columns * 2]

    @property
    def line_2(self):
        return self.operation.datas[self.operation.columns * 2 :]

    def get_editables(self):
        res = set()

        def aide(res, debut, limite):
            i = debut
            while i < limite:
                res.add(i)
                i += 3

        if not self.operation.virgule:
            if len(self.line_0) == len(self.line_1) == 4:
                return {10}
            aide(
                res, self.operation.columns * 2 + 2, self.operation.size
            )  # troisieme ligne

        else:
            i = self.operation.columns * 2 + 2
            flag = True
            while i < self.operation.size:
                if i >= self.operation.virgule + (self.operation.columns * 2) and flag:
                    i += 1
                    flag = False
                    continue
                res.add(i)
                i += 3
        return res


class MultiplicationModel(OperationModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursorChanged.connect(self.highLightChanged)

    def get_initial_position(self):
        return self.i_line_1.stop + self.operation.columns - 1

    def is_result_line(self, index):
        return (
            self.operation.size - self.operation.columns <= index < self.operation.size
        )

    def is_retenue_line(self, index):
        """retenu première lignes et  appres addition"""
        if self.operation.rows == 4:  # 1 chiffre en bas
            if index < self.operation.columns:  # premire ligne
                return True
        else:
            if index < self.operation.columns * self.n_chiffres:  # premieres lignes
                return True
            elif (
                (self.n_chiffres * 2 + 2) * self.operation.columns
                <= index
                < (self.n_chiffres * 2 + 2) * self.operation.columns
                + self.operation.columns
            ):
                return True
        return False

    def move_cursor(self, index, key):
        new = self.cursor

        if key == Qt.Key_Up:
            while index > 0:
                index = index - self.operation.columns
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Down:
            while index < self.operation.size:
                index = index + self.operation.columns
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Right:
            while index % self.operation.columns < self.operation.columns - 1:
                index += 1
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Left:  # pragma: no branch
            while index % self.operation.columns:
                index -= 1
                if index in self.editables:
                    new = index
                    break

        return new

    def auto_move_next(self, position):
        """
        x: index du chiffre ligne0
        y: index du chiffre ligne1
        i_case: index de la ligne en cours
        res: résultat
        """
        res = position
        i_case = position % self.operation.columns

        # ordre result/middle est important pour le cas ouligne1 a 1 chiffre

        if self.isResultLine(position):
            if self.n_chiffres == 1:  # cas ou mambre 2 a 1 seul chiffre
                if (
                    position - 1 != self.operation.size - self.operation.columns
                ):  # pragma: no branch
                    temp = self._if_middle_line(position)
                    if temp is not None:  # pragma: no branch
                        res = temp

            else:
                # tant que pas l'avant dernier
                if i_case > 1:
                    res = position - self.operation.columns - 1

        elif self.isMiddleLine(position):
            temp = self._if_middle_line(position)
            # je sais pas si_if_middle_peut_etre_none
            if temp is not None:  # pragma: no branch
                res = temp

        elif self.isRetenueLine(position):  # pragma: no branch
            # pourrait être else mais moins explicit, d'où le pragama
            if position < self.operation.columns * self.n_chiffres:  # retenu du haut.
                y = self.n_chiffres - (position // self.operation.columns) - 1
                x = (
                    self.operation.columns - i_case - 1
                )  # une colonne de retenu correspond toujorus au même x
                if i_case <= self.i_retenue_virgule:
                    x -= 1
                res = self._get_middle(y, x)

            else:  # retenu du bas
                res = position + self.operation.columns

        return res

    # move_cursor/automove next
    def _get_retenue(self, y, x):
        rev_y = self.n_chiffres - y
        start = (
            rev_y * self.operation.columns - 1
        )  # en fin de ligne de la bonne ligne de retenu
        res = start - x - 1  # -1 car la retenu décale d'une colonne
        new_i_case = res % self.operation.columns
        if new_i_case <= self.i_retenue_virgule:
            res -= 1
        return res

    def _get_middle(self, y, x):
        start = self.i_line_1.stop + (self.operation.columns * y)
        new_i_case = self.operation.columns - 1 - y - x
        res = start + new_i_case
        return res

    def get_next_line(self, y):
        bonus = 0
        # cas où on saute la ligne de la retenue
        if y == self.n_chiffres - 1:
            bonus += 1
        return self.operation.columns * (self.n_chiffres + 2 + y + bonus + 2) - 1

    def _if_middle_line(self, position):
        i_case = position % self.operation.columns
        if self.n_chiffres == 1:
            y = 0
        else:
            y = (position - self.i_line_1.stop) // self.operation.columns
        x = self.operation.columns - i_case - y - 1

        # cas du point de décalge
        if x < 0:
            temp = position - 1
            return temp
        # cas du l'avant dernier à gauche qui sera toujorus un retour à la ligne
        elif i_case == 1:
            return self.get_next_line(y)

        # cas où on va vers la retenu
        elif x < self.len_ligne0 - 1:  # pas de retenu pour le dernier de line0
            return self._get_retenue(y, x)

        # cas pré fin de ligne
        elif x == self.len_ligne0 - 1:
            return position - 1

        # cas fin de ligne
        elif x > self.len_ligne0 - 1:  # pragma: no branch
            return self.get_next_line(y)

    # private utils property / methods
    @cached_property
    def i_line_0(self):
        start = self.n_chiffres * self.operation.columns
        return slice(start, start + self.operation.columns)

    @cached_property
    def i_line_1(self):
        start = self.i_line_0.stop
        return slice(start, start + self.operation.columns)

    @cached_property
    def editables_index_middle(self):
        """index d'op sans les retenues"""

        pre_list = (
            set(
                range(
                    self.i_line_1.stop,
                    self.i_line_1.stop + self.operation.columns * self.n_chiffres,
                )
            )
            if self.n_chiffres > 1
            else set(
                range(self.operation.size - self.operation.columns, self.operation.size)
            )
        )
        return pre_list & self.editables

    @cached_property
    def i_retenue_virgule(self):
        try:
            return self.operation.datas[self.i_line_0].index(",")
        except ValueError:
            return 0  # virgule ne peut jamais avoir index 0

    @cached_property
    def len_ligne0(self):
        line1 = self.operation.datas[self.i_line_0]
        for n, i in enumerate(line1):  # pragma: no branch
            if i == "":
                pass
            elif i.isdigit():  # pragma: no branch
                self._len_ligne0 = self.operation.columns - n
                if "," in line1:
                    self._len_ligne0 -= 1
                return self._len_ligne0

    @cached_property
    def i_line0_vigule(self):
        return self.i_retenue_virgule

    @cached_property
    def i_line1_virgule(self):
        try:
            return self.operation.datas[self.i_line_1].index(",")
        except ValueError:
            return 0  # virgule ne peut jamais avoir index 0

    def isMembreLine(self, index):
        return self.i_line_0.start <= index < self.i_line_1.stop

    @functools.lru_cache()
    def getHighlightedForCurrent(self, index):
        """retour x et y correspondant aux membres à hightlight vu index en oours"""
        # cas non concernés:

        if index not in self.editables_index_middle:
            return -1, -1

        i_case = index % self.operation.columns
        if self.n_chiffres == 1:
            return (self.operation.columns * 3) - 1, index - (
                2 * self.operation.columns
            )
        else:
            y = (index - self.i_line_1.stop) // self.operation.columns
        x = self.operation.columns - i_case - y - 1
        if x < 0:  # cas des 0 de décalage
            index_x = -1
        else:  # reste
            index_x = self.i_line_0.stop - 1 - x

            if i_case <= self.i_line0_vigule:
                index_x -= 1
            # pour les fins de ligne trouver le + dernier de ligne0
            while not self.operation.datas[index_x].isdigit():
                index_x += 1

        index_y = self.i_line_1.stop - 1 - y
        if self.operation.columns - y - 1 <= self.i_line1_virgule:
            index_y -= 1

        return index_y, index_x

    # slot / Property  en plus

    @Slot(int, result=bool)
    def isLine1(self, index):
        return self.i_line_1.start <= index < self.i_line_1.stop

    highLightChanged = Signal()

    @Property("QVariantList", notify=highLightChanged)
    def highLight(self):
        return list(self.getHighlightedForCurrent(self.cursor))

    @cached_property
    def n_chiffres(self):
        return int((self.operation.rows - 4) / 2) or 1

    @property
    def line_0(self):
        start = self.n_chiffres * self.operation.columns
        return self.operation.datas[start : start + self.operation.columns]

    @property
    def line_1(self):
        start = (1 + self.n_chiffres) * self.operation.columns
        return self.operation.datas[start : start + self.operation.columns]

    @property
    def line_res_index(self):
        return self.operation.size - self.operation.columns, self.operation.size

    @property
    def line_res(self):
        start, stop = self.line_res_index
        return self.operation.datas[start:stop]

    def get_editables(self):
        res = set()
        if self.n_chiffres == 1:
            # pass
            start, stop = self.line_res_index
            res = set(range(start + 1, stop)) | set(
                range(1, self.operation.columns - 1)
            )
        else:
            # d'abord les retenues via les même index que ligne0 - le dernier
            indexes = [n for n, x in enumerate(self.line_0) if x.isdigit()][:-1]
            for i in range(self.n_chiffres):
                k = self.operation.columns * i
                for j in indexes:
                    res.add(k + j)

            # ensuite on faite tout le reste
            reste = set(
                range(
                    self.operation.columns * (self.n_chiffres + 2), self.operation.size
                )
            )

            # on enleve la collone des signe
            colonne_signe = set(range(0, self.operation.size, self.operation.columns))
            reste = reste - colonne_signe

            res = res | reste

        return res


class DivisionModel(OperationModel):

    # todo: self.quotientChanged.connect(self.ddb.recentsModelChanged)

    def move_cursor(self, index, key):
        temp = index
        if key == Qt.Key_Up:
            while temp >= self.operation.columns:
                temp -= self.operation.columns
                if temp in self.editables:
                    return temp
        elif key == Qt.Key_Down:
            while temp < self.operation.size:
                temp += self.operation.columns
                if temp in self.editables:
                    return temp
        elif key == Qt.Key_Right:
            while temp < self.operation.size:
                temp += 1
                if temp in self.editables:
                    return temp
        elif key == Qt.Key_Left:  # pragma: no branch
            while temp > 0:
                temp -= 1
                if temp in self.editables:
                    return temp
        return self.cursor

    def auto_move_next(self, position):
        res = position

        if res in self.retenue_gauche:  # va à la retenue droit du bas
            res = res + self.operation.columns - 1
        elif res in self.retenue_droite:  # va au chiffre d'avant du bas
            res = res + self.operation.columns + 2
        elif res in self.regular_chiffre:  # pragma: no branch
            row = int(position / self.operation.columns)
            if bool(row & 1):  # impair : on va faire le chiffre de gauche
                debut_ligne = row * self.operation.columns
                temp = res - 3
                if temp >= debut_ligne:
                    res = temp
                else:
                    # on va à la ligne, aligné sous plus grand index
                    res = self.go_to_end_line_result(debut_ligne)
            else:  # va aussi au chiffre de gauche mais calcul différent
                if (
                    position % self.operation.columns >= 4
                ):  # on shunt la premiere colone
                    # res -= 2 * self.operation.columns + 1
                    res -= 3

        return res

    # Slot en plus
    @Slot()
    def addRetenues(self):
        if not self.isMembreLine(self.cursor):
            r1 = self.cursor - (self.operation.columns * 2) - 1
            r2 = self.cursor - self.operation.columns - 2
            if r1 not in self.retenue_gauche or r2 not in self.retenue_droite:
                return

            res = "" if self.operation.datas[r1] == "1" else "1"
            self.setData(self.index(r1), res, Qt.EditRole)
            self.setData(self.index(r2), res, Qt.EditRole)

    @Slot(result=int)
    def getPosByQuotient(self):
        len_q = len(self.operation.quotient.replace(",", ""))
        len_diviseur = len(str(self.operation.diviseur).replace(",", ""))
        if not len_q or len_q == 1:
            self.cursor = self.operation.columns + 1 + (len_diviseur * 3)
        else:
            self.cursor = self.cursor + self.operation.columns + 3
        return self.cursor

    @Slot()
    def goToAbaisseLine(self):
        debut = int(self.cursor / self.operation.columns) * self.operation.columns
        self.cursor = (
            debut
            + self._get_last_index_filled(
                self.operation.datas[debut : debut + self.operation.columns]
            )
            + 3
        )

    @Slot()
    def goToResultLine(self):
        debut = int(self.cursor / self.operation.columns) * self.operation.columns
        self.cursor = self.go_to_end_line_result(debut)

    @Slot(int, result=bool)
    def isDividendeLine(self, index):
        return index in range(self.operation.columns)

    @Slot(int, result=bool)
    def isMembreLine(self, index):
        return bool(int(index / self.operation.columns) & 1)

    @Slot(int, result=bool)
    def isRetenue(self, index):
        return index in self.retenue_gauche or index in self.retenue_droite

    @Slot(int, result=bool)
    def isRetenueDroite(self, index):
        return index in self.retenue_droite

    @Slot(int, result=bool)
    def isRetenueGauche(self, index):
        return index in self.retenue_gauche

    @Slot(int, result=bool)
    def isEditable(self, value):
        return value in self.editables

    # private utils property / methods

    @cached_property
    def retenue_gauche(self):
        res = set()
        for i in range(
            self.operation.rows - 2
        ):  # pas de rentenu gauche pour la derniere ligne
            if bool(i & 1):  # on saute les lignes impaires
                continue
            debut = i * self.operation.columns
            res.update(set(range(debut + 3, debut + self.operation.columns, 3)))
        return res

    @cached_property
    def retenue_droite(self):
        res = set()
        for i in range(1, self.operation.rows - 1):
            if not bool(i & 1):  # on saute les lignes paires
                continue
            debut = i * self.operation.columns + 2
            res.update(set(range(debut, debut + self.operation.columns - 3, 3)))
        return res

    @cached_property
    def regular_chiffre(self):
        res = set()
        for i in range(1, self.operation.rows):
            debut = i * self.operation.columns + 1
            res.update(set(range(debut, debut + self.operation.columns, 3)))
        return res

    @staticmethod
    def _get_last_index_filled(liste):
        # retourne les dernier index rempli
        # accepte une ligne de content
        if not isinstance(liste, list):
            liste = list(liste)
        for n, i in enumerate(liste[::-1]):
            if i:
                return len(liste) - (n + 1)
        return len(liste) - 1

    def go_to_end_line_result(self, debut_ligne):
        ligne = slice(debut_ligne, debut_ligne + self.operation.columns)
        new_index = self._get_last_index_filled(self.operation.datas[ligne])
        return debut_ligne + self.operation.columns + new_index

    # @Slot(int, result=bool)
    # def readOnly(self, value):
    #     return value not in self.editables

    def is_ligne_dividende(self, index):
        return 0 <= index < self.operation.columns

    def is_ligne_last(self, index):
        return (
            self.operation.size - self.operation.columns <= index < self.operation.size
        )

    def get_editables(self):
        last = set(
            range(
                self.operation.size - self.operation.columns + 1, self.operation.size, 3
            )
        )
        milieu = set()
        for i in range(1, self.operation.rows - 1):
            debut = i * self.operation.columns
            impair = bool(i & 1)
            mini_index = 1
            # rangée des chiffres
            milieu.update(
                set(range(debut + mini_index, debut + self.operation.columns, 3))
            )
            mini_index = 2 if impair else 3  # rien dans la premiere colone
            skip_end = 3 if impair else 0
            # # rangée des retenues /// A priorri les tests on été fait AVEC cette ligne là
            # milieu.update(
            #     set(
            #         range(
            #             debut + mini_index, debut + self.operation.columns - skip_end, 3
            #         )
            #     )
            # )

        return milieu | last
