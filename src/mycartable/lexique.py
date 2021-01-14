from typing import Optional, Any, Union, Dict

import flag
from PyQt5.QtCore import (
    QModelIndex,
    Qt,
    QSortFilterProxyModel,
    pyqtProperty,
    QObject,
    QLocale,
    pyqtSlot,
    QRegExp,
)
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
        for row in data:
            self._format_internal_data(row)
            self._data.append(row)

    def _format_internal_data(self, lexon: dict):
        # on crée les cases vides qui n'ont pas de traduction
        res = [None] * len(self._locales)
        for t in lexon["traductions"]:
            res[self._locales.index(t["locale"])] = t
        lexon["traductions"] = res

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

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if role == Qt.DisplayRole and 0 <= section < len(self._locales):
            locale = QLocale(self._locales[section])
            drapeau = flag.flag(locale.name().split("_")[-1])
            nom = locale.nativeLanguageName().split(" ")[-1].upper()
            return f"{drapeau} {nom} {drapeau}"

    @pyqtProperty("QVariantList", constant=True)
    def locales(self):
        return self._locales

    def addLexon(self, trads: list) -> bool:
        if new_lexon := self._dtb.execDB("Lexon", None, "add", trads, td=True):
            self._format_internal_data(new_lexon)
            self._data.append(new_lexon)
            return True

        return False


class LexiqueProxy(QSortFilterProxyModel):
    def __init__(self, parent=None, source=None, **kwargs):
        super().__init__(parent=parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setSourceModel(source)

    @pyqtSlot(int)
    def doSort(self, col: int):
        if col == self.sortColumn():
            self.sort(col, int(not self.sortOrder()))
        else:
            self.sort(col, Qt.AscendingOrder)


class Lexique(QQuickItem):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self._model = LexiqueModel(parent=self)
        self._proxy = LexiqueProxy(parent=self, source=self._model)

    """ "
    Qt Properties
    """

    @pyqtProperty(QObject, constant=True)
    def model(self) -> LexiqueModel:
        return self._model

    @pyqtProperty(QObject, constant=True)
    def proxy(self) -> LexiqueProxy:
        return self._proxy

    """"
    Qt SLot
    """

    @pyqtSlot("QVariantList", result=bool)
    def addLexon(self, trads: list) -> bool:
        if self.model.addLexon(trads):
            self.model.insertRow(0)
            self.proxy.doSort(0)
            return True
        return False

    @pyqtSlot(int, str)
    def filter(self, index: int, value: str):
        self.proxy.setFilterKeyColumn(index)
        self.proxy.setFilterRegExp(
            QRegExp(value, Qt.CaseInsensitive, QRegExp.FixedString)
        )
