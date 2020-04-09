import operator

from PySide2.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    Signal,
    Property,
    QAbstractItemModel,
    QAbstractListModel,
    Slot,
)

from package.database import db
from pony.orm import db_session, make_proxy
from descriptors import cachedproperty


class OperationModel(QAbstractListModel):

    cursorChanged = Signal()
    paramsChanged = Signal()
    sectionIdChanged = Signal()
    ddb = None

    def __init__(self):
        super().__init__()
        self._cursor = 0
        self.editables = []
        self.db = db
        self.params = {"rows": 0, "columns": 0, "datas": [], "size": 0}
        self._sectionId = None
        self.sectionIdChanged.connect(self.load_params)
        self.dataChanged.connect(self.ddb.recentsModelChanged)

    @db_session
    def load_params(self):
        # c'est une post init method
        try:
            self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
        except AttributeError:
            self._sectionId = None
            return
        self.params = self.proxy.to_dict()
        self.editables = self.proxy.get_editables()
        self.custom_params_load()

    # Property

    @Property(int, notify=paramsChanged)
    def columns(self):
        return int(self.params["columns"])

    @Property(int, notify=cursorChanged)
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor_set(self, value: int):
        if value != self._cursor:
            self._cursor = value
            self.cursorChanged.emit()

    @Property("QVariantList", notify=paramsChanged)
    def datas(self):
        return self.params["datas"]

    @Property(int, notify=paramsChanged)
    def rows(self):
        return int(self.params["rows"])

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit()

    @Property(int, notify=paramsChanged)
    def size(self):
        return int(self.params["size"])

    @Property(int, notify=paramsChanged)
    def virgule(self):
        return self.params["virgule"]

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.datas[index.row()]
            return value

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        return QAbstractItemModel.flags(index) | Qt.ItemIsEditable

    def rowCount(self, parent=QModelIndex()) -> int:
        return int(self.params["size"])

    def setData(self, index, value, role) -> bool:
        if index.isValid() and role == Qt.EditRole:
            with db_session:
                self.proxy.update_datas(index.row(), value)
            self.datas[index.row()] = value
            self.dataChanged.emit(index, index)
            if "," not in value:
                self.autoMoveNext(index.row())
            return True
        return False

    # Slot en plus

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    @Slot(result=int)
    def getInitialPosition(self):
        pos = self.get_initial_position()
        a = pos if pos is not None else self.size - 1
        return a

    @Slot(int, int)
    def moveCursor(self, index, key):
        res = self.move_cursor(index, key)
        if res != index:
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
        if position == self.rowCount() - self.columns + 1:  # début de ligne résultat
            return position
        elif position > self.columns:  # reste ligne résutlat
            diff = self.rowCount() - position
            new = int(self.columns - diff - 1)
            if new == self.virgule:
                new -= 1  # saute la virgule dans les retenues
        else:  # le haut
            new = self.columns * (self.rows - 1) + position
        return new

    def is_result_line(self, index):
        return index >= self.rowCount() - self.columns

    def is_retenue_line(self, index):
        return 0 <= index and index < self.columns

    def move_cursor(self, index, key):
        new = self.cursor
        if key == Qt.Key_Up:
            temp = index - self.columns * (self.rows - 1)
            if temp == self.columns - 1:
                new = temp - 1
            elif temp > 0:
                new = temp
        elif key == Qt.Key_Down:
            temp = index + self.columns * (self.rows - 1)
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
    def auto_move_next(self, position):
        if position < self.columns:  # premiere ligne
            res = position + self.columns - 1
            if position > self.virgule and res - self.columns <= self.virgule:
                res -= 1

            return res
        elif self.columns <= position < self.columns * 2:  # deuxième ligne
            res = position + self.columns + 2
            if (
                position - self.columns <= self.virgule
                and res - (self.columns * 2) >= self.virgule
            ):
                res += 1
            return res

        elif self.columns * 2 <= position < self.columns * 3:  # troisieme ligne
            if position - (self.columns * 2) == 5:  # avant dernier aucun autre choix
                return position - 3
            elif position - (self.columns * 2) == 2:  # dernier aucun autre choix
                return position
            res = position - self.columns * 2 - 4
            if position - (self.columns * 2) >= self.virgule and res < self.virgule:
                res -= 1
            return res

    @Slot(int, result=bool)
    def isRetenueGauche(self, index):
        return index in self.editables and self.isRetenueLine(index)

    @Slot(int, result=bool)
    def isRetenueDroit(self, index):
        return index in self.editables and self.isMiddleLine(index)

    def is_result_line(self, index):
        return index >= self.columns * 2

    def is_retenue_line(self, index):
        """retenu == fistr line"""
        return 0 <= index and index < self.columns

    def move_cursor(self, index, key):
        new = self.cursor
        if key == Qt.Key_Up:
            if index == self.columns + 3:  # premier 2èmeligne
                new = min(self.editables)
            elif self.isMiddleLine(index):
                new = index - self.columns - 2
            elif index == self.rowCount() - 2:  # dernier dernière ligne
                new = self.columns - 3
            elif self.isResultLine(index):
                new = index - self.columns + 1
        elif key == Qt.Key_Down:
            if index == self.columns - 3:  # dernier premiere ligne
                new = self.rowCount() - 2
            elif self.isRetenueLine(index):
                new = index + self.columns + 2
            elif self.isMiddleLine(index):
                new = index + self.columns - 1
        elif key == Qt.Key_Right:
            temp = index + 3
            if temp in self.editables:
                new = temp
            elif index % self.columns >= self.columns - 4:
                pass
            elif temp + 1 in self.editables:
                new = temp + 1
        elif key == Qt.Key_Left:
            temp = index - 3
            if temp in self.editables:
                new = temp
            elif self.datas[temp].isdigit() or self.datas[temp] == ",":
                new = temp - 1
            elif self.datas[temp + 1] == ",":
                new = temp - 1

        return new


class MultiplicationModel(OperationModel):
    def custom_params_load(self):
        self.n_chiffres = self.proxy.n_chiffres

    def get_initial_position(self):
        return self.i_line_1.stop + self.columns

    @cachedproperty
    def i_line_0(self):
        start = self.n_chiffres * self.columns
        return slice(start, start + self.columns)

    @cachedproperty
    def i_line_1(self):
        start = self.i_line_0.stop
        return slice(start, start + self.columns)

    @cachedproperty
    def i_line_res(self):
        if self.virgule:
            return slice(self.size - self.columns * 2, self.size - self.columns)
        else:
            return slice(self.size - self.columns, self.size)

    def is_virgule_index(self, index):
        return index % self.columns == self.virgule

    @cachedproperty
    def i_retenue_virgule(self):
        try:
            return self.datas[self.i_line_0].index(",")
        except ValueError:
            return 0  # virgule ne peut jamais avoir index 0

    @cachedproperty
    def len_ligne0(self):
        line1 = self.datas[self.i_line_0]
        for n, i in enumerate(line1):
            if i == "":
                pass
            elif i.isdigit():
                self._len_ligne0 = self.columns - n
                if "," in line1:
                    self._len_ligne0 -= 1
                return self._len_ligne0

    def _get_retenue(self, y, x):
        rev_y = self.n_chiffres - y
        start = rev_y * self.columns - 1  # en fin de ligne de la bonne ligne de retenu
        res = start - x - 1  # -1 car la retenu décale d'une colonne
        new_i_case = res % self.columns
        if new_i_case <= self.i_retenue_virgule:
            res -= 1
        return res

    def _get_middle(self, y, x):
        start = self.i_line_1.stop + (self.columns * y)
        new_i_case = self.columns - 1 - y - x
        res = start + new_i_case
        return res

    def get_next_line(self, y):
        bonus = 0
        # cas où on saute la ligne de la retenue
        if y == self.n_chiffres - 1:
            bonus += 1
        return self.columns * (self.n_chiffres + 2 + y + bonus + 2) - 1

    def _if_middle_line(self, position):
        i_case = position % self.columns
        if self.n_chiffres == 1:
            y = 0
        else:
            y = (position - self.i_line_1.stop) // self.columns
        x = self.columns - i_case - y - 1

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
        elif x > self.len_ligne0 - 1:
            return self.get_next_line(y)
        return None

    def auto_move_next(self, position):
        """
        x: index du chiffre ligne0
        y: index du chiffre ligne1
        i_case: index de la ligne en cours
        res: résultat
        """
        res = position
        i_case = position % self.columns

        # ordre result/middle est important pour le cas ouligne1 a 1 chiffre

        if self.isResultLine(position):
            if self.n_chiffres == 1:  # cas ou mambre 2 a 1 seul chiffre
                if position - 1 != self.size - self.columns:
                    temp = self._if_middle_line(position)
                    if temp is not None:
                        res = temp

            else:
                # tant que pas l'avant dernier
                if i_case > 1:
                    res = position - self.columns - 1

        elif self.isMiddleLine(position):
            temp = self._if_middle_line(position)
            if temp is not None:
                res = temp

        elif self.isRetenueLine(position):
            if position < self.columns * self.n_chiffres:  # retenu du haut.
                y = self.n_chiffres - (position // self.columns) - 1
                x = (
                    self.columns - i_case - 1
                )  # une colonne de retenu correspond toujorus au même x
                if i_case <= self.i_retenue_virgule:
                    x -= 1
                res = self._get_middle(y, x)

            else:  # retenu du bas
                res = position + self.columns

        return res

    def isMembreLine(self, index):
        return self.i_line_0.start <= index < self.i_line_1.stop

    @Slot(int, result=bool)
    def isLine1(self, index):
        return self.i_line_1.start <= index < self.i_line_1.stop

    def is_result_line(self, index):
        return self.size - self.columns <= index < self.size

    def is_retenue_line(self, index):
        """retenu première lignes et  appres addition"""
        if self.rows == 4:  # 1 chiffre en bas
            if index < self.columns:  # premire ligne
                return True
        else:
            if index < self.columns * self.n_chiffres:  # premieres lignes
                return True
            elif (
                (self.n_chiffres * 2 + 2) * self.columns
                <= index
                < (self.n_chiffres * 2 + 2) * self.columns + self.columns
            ):
                return True
        return False

    def move_cursor(self, index, key):
        new = self.cursor

        if key == Qt.Key_Up:
            while index > 0:
                index = index - self.columns
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Down:
            while index < self.size:
                index = index + self.columns
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Right:
            while index % self.columns < self.columns - 1:
                index += 1
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Left:
            while index % self.columns:
                index -= 1
                if index in self.editables:
                    new = index
                    break

        return new


class DivisionModel(OperationModel):
    def custom_params_load(self):
        self._dividende = self.proxy.dividende_as_num
        self._diviseur = self.proxy.diviseur_as_num
        self._quotient = self.proxy.quotient
        self.cursor = 10

    @Slot()
    def addRetenues(self):
        if not self.isMembreLine(self.cursor):
            r1 = self.cursor - (self.columns * 2) - 1
            r2 = self.cursor - self.columns - 2
            if r1 not in self.retenue_gauche or r2 not in self.retenue_droite:
                return

            res = "" if self.datas[r1] == "1" else "1"
            self.setData(self.index(r1), res, Qt.EditRole)
            self.setData(self.index(r2), res, Qt.EditRole)

    @Slot(result=int)
    def getPosByQuotient(self):
        len_q = len(self.quotient.replace(",", ""))
        len_diviseur = len(str(self.diviseur).replace(",", ""))
        if not len_q or len_q == 1:
            self.cursor = self.columns + 1 + (len_diviseur * 3)
        else:
            self.cursor = self.cursor + self.columns + 3

    @Slot()
    def goToAbaisseLine(self):
        debut = int(self.cursor / self.columns) * self.columns
        self.cursor = (
            debut
            + self._get_last_index_filled(self.datas[debut : debut + self.columns])
            + 3
        )

    @Slot()
    def goToResultLine(self):
        debut = int(self.cursor / self.columns) * self.columns
        self.cursor = self.go_to_end_line_result(debut)

    @Slot(int, result=bool)
    def isDividendeLine(self, index):
        return index in range(self.columns)

    @Slot(int, result=bool)
    def isMembreLine(self, index):
        return bool(int(index / self.columns) & 1)

    @Slot(int, result=bool)
    def isRetenue(self, index):
        return index in self.retenue_gauche or index in self.retenue_droite

    @Slot(int, result=bool)
    def isRetenueDroite(self, index):
        return index in self.retenue_droite

    @Slot(int, result=bool)
    def isRetenueGauche(self, index):
        return index in self.retenue_gauche

    memberChanged = Signal()

    @Property(int, notify=memberChanged)
    def diviseur(self):
        return self._diviseur

    @Property(float, notify=memberChanged)
    def dividende(self):
        return self._dividende

    quotientChanged = Signal()

    @Property(str, notify=quotientChanged)
    def quotient(self):
        with db_session:
            return self.proxy.quotient

    @quotient.setter
    def quotient_set(self, value: int):
        with db_session:
            if value != self.proxy.quotient:
                self.proxy.quotient = value
        self.quotientChanged.emit()

    @cachedproperty
    def dividende_indexes(self):
        return set(range(1, self.columns, 3))

    def move_cursor(self, index, key):
        temp = index
        if key == Qt.Key_Up:
            while temp >= self.columns:
                temp -= self.columns
                if temp in self.editables:
                    return temp
                elif temp in self.dividende_indexes and temp != 1:
                    return temp - 1
        elif key == Qt.Key_Down:
            while temp < self.size:
                temp += self.columns
                if temp in self.editables:
                    return temp
        elif key == Qt.Key_Right:
            while temp < self.size:
                temp += 1
                if temp in self.editables:
                    return temp
        elif key == Qt.Key_Left:
            while temp > 0:
                temp -= 1
                if temp in self.editables:
                    return temp
        return self.cursor

    @cachedproperty
    def retenue_gauche(self):
        res = set()
        for i in range(self.rows - 2):  # pas de rentenu gauche pour la derniere ligne
            if bool(i & 1):  # on saute les lignes impaires
                continue
            debut = i * self.columns
            res.update(set(range(debut + 3, debut + self.columns, 3)))
        return res

    @cachedproperty
    def retenue_droite(self):
        res = set()
        for i in range(1, self.rows - 1):
            if not bool(i & 1):  # on saute les lignes paires
                continue
            debut = i * self.columns + 2
            res.update(set(range(debut, debut + self.columns - 3, 3)))
        return res

    @cachedproperty
    def regular_chiffre(self):
        res = set()
        for i in range(1, self.rows):
            debut = i * self.columns + 1
            res.update(set(range(debut, debut + self.columns, 3)))
        return res

    @staticmethod
    def _get_last_index_filled(liste):
        # retourne les dernier index rempli
        # accepte une ligne de data
        if not isinstance(liste, list):
            liste = list(liste)
        for n, i in enumerate(liste[::-1]):
            if i:
                return len(liste) - (n + 1)
        return len(liste) - 1

    def auto_move_next(self, position):
        res = position

        if res in self.retenue_gauche:  # va à la retenue droit du bas
            res = res + self.columns - 1
        elif res in self.retenue_droite:  # va au chiffre d'avant du bas
            res = res + self.columns + 2
        elif res in self.regular_chiffre:
            row = int(position / self.columns)
            if bool(row & 1):  # impair : on va faire le chiffre de gauche
                debut_ligne = row * self.columns
                temp = res - 3
                if temp >= debut_ligne:
                    res = temp
                else:
                    # on va à la ligne, aligné sous plus grand index
                    res = self.go_to_end_line_result(debut_ligne)
            else:  # va aussi au chiffre de gauche mais calcul différent
                if position % self.columns >= 4:  # on shunt la premiere colone
                    # res -= 2 * self.columns + 1
                    res -= 3

        return res

    def go_to_end_line_result(self, debut_ligne):
        ligne = slice(debut_ligne, debut_ligne + self.columns)
        new_index = self._get_last_index_filled(self.datas[ligne])
        return debut_ligne + self.columns + new_index
