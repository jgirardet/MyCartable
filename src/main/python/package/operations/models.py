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
        print(value, "dans cursor set")
        if value != self._cursor:
            print("cursor set donc emot = ", value)
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


#
# class SoustractionModel(OperationModel):
#     def auto_move_next(self, position):
#         if position < self.columns:  # premiere ligne
#             res = position + self.columns - 1
#             if position > self.virgule and res - self.columns <= self.virgule:
#                 res -= 1
#
#             return res
#         elif self.columns <= position < self.columns * 2:  # deuxième ligne
#             res = position + self.columns + 2
#             if (
#                 position - self.columns <= self.virgule
#                 and res - (self.columns * 2) >= self.virgule
#             ):
#                 res += 1
#             return res
#
#         elif self.columns * 2 <= position < self.columns * 3:  # troisieme ligne
#             if position - (self.columns * 2) == 5:  # avant dernier aucun autre choix
#                 return position - 3
#             elif position - (self.columns * 2) == 2:  # dernier aucun autre choix
#                 return position
#             res = position - self.columns * 2 - 4
#             if position - (self.columns * 2) >= self.virgule and res < self.virgule:
#                 res -= 1
#             return res
#
#     @Slot(int, result=bool)
#     def isRetenueGauche(self, index):
#         return index in self.editables and self.isRetenueLine(index)
#
#     @Slot(int, result=bool)
#     def isRetenueDroit(self, index):
#         return index in self.editables and self.isMiddleLine(index)
#
#     def is_result_line(self, index):
#         return index >= self.columns * 2
#
#     def is_retenue_line(self, index):
#         """retenu == fistr line"""
#         return 0 <= index and index < self.columns
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
