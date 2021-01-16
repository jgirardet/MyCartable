from PyQt5.QtCore import QModelIndex, pyqtProperty, QObject, Qt, QByteArray
from mycartable.types import DtbListModel


class ListOfPageModel(DtbListModel):
    TitreRole = Qt.UserRole + 1
    PageIdRole = Qt.UserRole + 2
    BgColorRole = Qt.UserRole + 3

    def __init__(self, **kwargs):
        self._data = []
        super().__init__(**kwargs)

    def _roleNames(self) -> dict:
        return {
            self.TitreRole: QByteArray(b"titre"),
            self.PageIdRole: QByteArray(b"pageid"),
            self.BgColorRole: QByteArray(b"bgcolor"),
        }

    def _insertRows(self, row, count):
        self._reset()

    def _removeRows(self, row, count):
        self._reset()

    def _moveRows(self, sourceRow, count, destinationChild):
        if count:
            raise NotImplementedError(
                "ListOfPageModel ne peut déplacer qu'un rang à la fois"
            )
        self._reset()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def data(self, index: QModelIndex, role: int) -> dict:
        if not index.isValid():
            return None
        elif role == self.TitreRole:
            return self._data[index.row()]["titre"]
        elif role == self.PageIdRole:
            return self._data[index.row()]["id"]
        elif role == self.BgColorRole:
            return self._data[index.row()]["matiereBgColor"]
        else:
            return None

    def update_titre(self, pageobj: "Page") -> bool:
        for idx, page in enumerate(self._data):
            if page["id"] == pageobj.id:
                self._data[idx]["titre"] = pageobj.titre
                self.dataChanged.emit(
                    self.index(idx, 0),
                    self.index(idx, 0),
                )
                return True
        return False

    def remove_by_Id(self, pageid: str) -> bool:
        for idx, page in enumerate(self._data):
            if pageid == page["id"]:
                return self.remove(idx)
        return False

    def move_to(self, pageid: str, dest: int) -> bool:
        for idx, page in enumerate(self._data):
            if pageid == page["id"]:
                return self.move(idx, dest)
        return False

    """
    Qt pyqtProperty
    """


class RecentsModel(ListOfPageModel):
    def __init__(self, annee, **kwargs):
        self.annee = annee
        super().__init__(**kwargs)

    def _reset(self):
        self._data = self._dtb.execDB("Page", None, "recents", self.classeur.annee)

    @pyqtProperty(QObject, constant=True)
    def classeur(self):
        return self.parent()


class ActiviteModel(ListOfPageModel):
    def __init__(self, activite: str, **kwargs):
        self.activite = activite
        super().__init__(**kwargs)

    def _reset(self):
        self._data = self._dtb.execDB("Activite", self.activite, "pages_by_created")
