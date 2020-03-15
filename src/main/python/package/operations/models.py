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
    def auto_move_next(self, position):
        res = position
        if self.isMiddleLine(position):
            first_middle_index = self.columns * (self.n_chiffres + 2)
            r_index = position - first_middle_index  # inde relatif au premier middle
            i_line = r_index // self.columns  # index de la ligne dans les n_chiffres
            i_case = r_index % self.columns  # index dans la ligne elle même
            i_retenue_line = (
                self.n_chiffres - i_line - 1
            )  # absolut index de ligne de retenu

            #############
            # temp

            i_rel_base = (
                self.columns - i_line - 1
            )  # index "zéro" relatif de chaque ligne
            i_rel = i_rel_base - i_case
            if i_rel <= self.virgule:
                i_rel -= 1
            ##########
            if i_case + i_line + bool(self.virgule) > self.n_chiffres:
                print("cas 1")
                if self.columns - i_case - 1 <= i_line - 1:
                    res = position - 1
                else:
                    i_rel_base = (
                        self.columns - i_line - 1
                    )  # index "zéro" relatif de chaque ligne
                    i_rel = i_rel_base - i_case
                    print("irel", i_rel, i_rel_base)

                    # cas ou le premier le chiffre de première ligne est nul ou zéro quand virgule
                    index0_ligne0 = self.columns * self.n_chiffres
                    i_ligne0 = index0_ligne0 + self.columns - 1 - i_rel
                    content_i_ligne0 = self.datas[i_ligne0]
                    print("ilign0", i_ligne0, content_i_ligne0)
                    if content_i_ligne0 in {"", "0"}:
                        res = position - 1

                    else:  # cas général avec retenu
                        retenue_index = self.columns - 2 - i_rel
                        if retenue_index == self.virgule:
                            retenue_index -= 1
                        res = self.columns * i_retenue_line + retenue_index
            # elif (
            #     1 < i_case and self.columns - i_line - i_case <= self.n_chiffres
            # ):  # dans les clous
            elif 1 < i_case and i_rel < self.n_chiffres:  # dans les clous
                print("cas 2,", i_case, i_line, i_rel)
                res = position - 1

            elif (
                1 < i_case and i_rel <= self.n_chiffres and self.virgule
            ):  # dans les clous
                print("cas 2,", i_case, i_line, i_rel)
                res = position - 1
            else:  # hors clous, retour à la ligne, on saute la ligne de retnue si dernière
                print("hors clou", i_case, i_line, i_rel)
                print(i_line)
                if i_line < self.n_chiffres:
                    ligne = position // self.columns
                    res = (ligne + 2) * self.columns - 1
                    if self.isRetenueLine(res):
                        res = res + self.columns
                    # res = self.columns * (self.n_chiffres + 2 + i_line + 1)

        elif self.isRetenueLine(position):
            if position < self.columns * self.n_chiffres:  # retenu du haut.
                i_line = self.n_chiffres - (position // self.columns) - 1
                i_case = position % self.columns
                retenue_index = self.columns - 2 - i_case
                i_rel = self.columns - 1 - i_line - retenue_index
                print(i_line, i_case)
                res = (self.n_chiffres + 2 + i_line) * self.columns + i_rel - 1

            else:  # retenu du bas
                res = position + self.columns

        elif self.isResultLine(position):
            if position - 1 != self.size - self.columns:
                res = position - self.columns - 1

        return res

    @property
    def n_chiffres(self):
        return int((self.rows - 4) / 2)

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


#
#     def move_cursor(self, index, key):
#         new = self.cursor
#         if key == Qt.Key_Up:
#             if index == self.columns + 3:  # premier 2èmeligne
#                 new = min(self.editables)
#             elif self.isMiddleLine(index):
#                 new = index - self.columns - 2
#             elif index == self.rowCount() - 2:  # dernier dernière ligne
#                 new = self.columns - 3
#             elif self.isResultLine(index):
#                 new = index - self.columns + 1
#         elif key == Qt.Key_Down:
#             if index == self.columns - 3:  # dernier premiere ligne
#                 new = self.rowCount() - 2
#             elif self.isRetenueLine(index):
#                 new = index + self.columns + 2
#             elif self.isMiddleLine(index):
#                 new = index + self.columns - 1
#         elif key == Qt.Key_Right:
#             temp = index + 3
#             if temp in self.editables:
#                 new = temp
#             elif index % self.columns >= self.columns - 4:
#                 pass
#             elif temp + 1 in self.editables:
#                 new = temp + 1
#         elif key == Qt.Key_Left:
#             temp = index - 3
#             if temp in self.editables:
#                 new = temp
#             elif self.datas[temp].isdigit() or self.datas[temp] == ",":
#                 new = temp - 1
#             elif self.datas[temp + 1] == ",":
#                 new = temp - 1
#
#         return new
