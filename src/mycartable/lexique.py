from typing import Optional, Any, Union

from PyQt5.QtCore import QModelIndex, Qt, QSortFilterProxyModel, pyqtProperty, QObject
from PyQt5.QtQuick import QQuickItem
from mycartable.types.collections import DtbTableModel


class LexiqueModel(DtbTableModel):
    def __init__(self, **kwargs):
        self._data = []
        self._locales = []
        super().__init__(**kwargs)

    def _reset(self):
        data = self._dtb.execDB("Lexon", None, "all")
        self._locales = self._dtb.execDB("Locale", None, "all")
        # on crée les cases vides qui n'ont pas de traduction
        for row in data:
            res = [None] * len(self._locales)
            for t in row["traductions"]:
                res[self._locales.index(t["locale"])] = t
            row["traductions"] = res
            self._data.append(row)

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._locales)

    def data(self, index: QModelIndex, role: int) -> Optional[str]:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if trad := self._data[index.row()]["traductions"][index.column()]:
                return trad["content"]
            else:
                return ""

    def setData(self, index: QModelIndex, value: Any, role: int) -> Union[bool, str]:
        if index.isValid():
            if role == Qt.EditRole:
                row = self._data[index.row()]
                trad = row["traductions"][index.column()]
                res = self._dtb.setDB("Traduction", trad["id"], {"content": value})
                if res:
                    self._data[index.row()]["traductions"][index.column()][
                        "content"
                    ] = value
                    self.dataChanged.emit(index, index)
                    return True

        return False


class LexiqueProxy(QSortFilterProxyModel):
    def __init__(self, parent=None, source=None, **kwargs):
        super().__init__(parent=parent)
        self.setSourceModel(source)


class Lexique(QObject):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self._model = LexiqueModel(parent=self)
        self._proxy = LexiqueProxy(parent=self, source=self._model)

    """ "
    Qt Properties
    """

    @pyqtProperty(QObject, constant=True)
    def model(self):
        return self._model

    @pyqtProperty(QObject, constant=True)
    def proxy(self):
        return self._proxy
