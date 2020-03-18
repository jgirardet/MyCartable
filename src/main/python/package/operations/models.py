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
            return True
        return False

    # Slot en plus

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    @Slot(int, int)
    def moveCursor(self, index, key):
        res = self.move_cursor(index, key)
        if res != index:
            self.cursor = self.move_cursor(index, key)

    @Slot(int, result=bool)
    def readOnly(self, value):
        return value not in self.editables

    @Slot(int, result=bool)
    def isMiddleLine(self, index):
        return not self.isResultLine(index) and not self.isRetenueLine(index)

    @Slot(int, result=bool)
    def isResultLine(self, index):
        return self.is_result_line(index)

    @Slot(int, result=bool)
    def isRetenueLine(self, index):
        return self.is_retenue_line(index)

    # fonction overidable par subclass

    def auto_move_next(self, position):
        return position

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

    def get_retenue(self, y, x):
        rev_y = self.n_chiffres - y
        start = rev_y * self.columns - 1  # en fin de ligne de la bonne ligne de retenu
        print(start)
        res = start - x - 1  # -1 car la retenu décale d'une colonne
        new_i_case = res % self.columns
        if self.is_virgule_index(res):
            print("oui is virgule index")
            res -= 1
        elif new_i_case < self.virgule:
            print("icase et icas < virgule", new_i_case, self.virgule)
            res -= 1
        return res

    def get_middle(self, y, x):
        print("dans get middle", y, x)
        start = self.i_line_1.stop + (self.columns * y)
        new_i_case = self.columns - 1 - y - x
        if new_i_case < self.virgule:
            print("icase et icas < virgule", new_i_case, self.virgule)
            new_i_case -= 1
        print("newicas", new_i_case)
        res = start + new_i_case
        # new_i_case = res % self.columns

        print(res)
        if self.is_virgule_index(res):
            res -= 1
        return res

    def get_next_line(self, y):
        bonus = 0
        # cas où on saute la ligne de la retenue
        if y == self.n_chiffres - 1:
            bonus += 1

        return self.columns * (self.n_chiffres + 2 + y + +bonus + 2) - 1

    def if_middle_line(self, position):
        i_case = position % self.columns
        if self.n_chiffres == 1:
            y = 0
        else:
            y = (position - self.i_line_1.stop) // self.columns
        x = self.columns - i_case - y - 1
        print(i_case, y, x, self.len_ligne0)

        # cas du point de décalge
        if x < 0:
            temp = position - 1
            print("ici")
            return temp
        # cas du l'avant dernier à gauche qui sera toujorus un retour à la ligne
        elif i_case == 1:
            return self.get_next_line(y)

        # cas où on va vers la retenu
        elif x < self.len_ligne0 - 1:  # pas de retenu pour le dernier de line0
            return self.get_retenue(y, x)

        # cas pré fin de ligne
        elif x == self.len_ligne0 - 1:
            return position - 1

        # cas fin de ligne
        elif x > self.len_ligne0 - 1:
            return self.get_next_line(y)
        return None

    def if_middle_line_virgule(self, position):
        i_case = position % self.columns
        if self.n_chiffres == 1:
            y = 0
        else:
            y = (position - self.i_line_1.stop) // self.columns
        x = self.columns - i_case - y - 1 - (i_case < self.virgule)
        print(i_case, y, x, self.len_ligne0)

        # cas du point de décalge
        if x < 0:
            temp = position - 1
            if self.is_virgule_index(temp):
                temp -= 1
            return temp
        # cas du l'avant dernier à gauche qui sera toujorus un retour à la ligne
        elif i_case == 1:
            return self.get_next_line(y)

        # cas où on va vers la retenu
        elif x < self.len_ligne0 - 1:  # pas de retenu pour le dernier de line0
            print(f"on va à la retenu avec ", y, x)
            return self.get_retenue(y, x)

        # cas pré fin de ligne
        elif x == self.len_ligne0 - 1:
            return position - 1

        # cas fin de ligne
        elif x > self.len_ligne0 - 1:
            return self.get_next_line(y)
        return None

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

    def auto_move_next(self, position):
        if not self.virgule:
            return self.auto_move_next_sans_virgule(position)
        else:
            return self.auto_move_next_sans_virgule(position)

    def auto_move_next_sans_virgule(self, position):
        """
        x: index du chiffre ligne0
        y: index du chiffre ligne1
        i_case: index de la ligne en cours
        res: résultat
        """
        res = position
        i_case = position % self.columns

        print(self.isResultLine(11))
        print(self.isMiddleLine(11))

        # ordre result/middle est important pour le cas ouligne1 a 1 chiffre

        if self.isResultLine(position):
            if self.n_chiffres == 1:
                # tant que pas l'avant dernier
                if position - 1 != self.size - self.columns:
                    temp = self.if_middle_line(position)
                    if temp is not None:
                        res = temp

            else:
                # tant que pas l'avant dernier
                if position - 1 != self.size - self.columns:
                    res = position - self.columns - 1
                    if self.is_virgule_index(res):
                        res -= 1

        elif self.isMiddleLine(position):
            if self.virgule:
                temp = self.if_middle_line_virgule(position)
            else:
                temp = self.if_middle_line(position)
            if temp is not None:
                res = temp

        elif self.isRetenueLine(position):
            if position < self.columns * self.n_chiffres:  # retenu du haut.
                y = self.n_chiffres - (position // self.columns) - 1
                x = (
                    self.columns - i_case - 1
                )  # une colonne de retenu correspond toujorus au même x
                if i_case < self.virgule:
                    print("icase et icas < virgule", i_case, self.virgule)
                    x -= 1
                print("y ", y, "x ", x)
                res = self.get_middle(y, x)

            else:  # retenu du bas
                res = position + self.columns
                print("dans retenu bass", res)

        return res

    @property
    def n_chiffres(self):
        res = int((self.rows - 4) / 2)
        return res if res else res + 1

    def is_result_line(self, index):
        if self.virgule:
            return self.size - self.columns * 2 <= index < self.size - self.columns
        else:
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
                print(index % self.columns)
                index += 1
                if index in self.editables:
                    new = index
                    break

        elif key == Qt.Key_Left:
            while index % self.columns:
                print(index % self.columns)
                index -= 1
                if index in self.editables:
                    new = index
                    break

        return new
