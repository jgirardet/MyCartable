from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QUndoStack

from .bridge import Bridge
from pony.orm import db_session


class Annee(Bridge):

    """
    Attention Peut être utilisé directement sans new
    Sans être instancié par un id précis

    """

    entity_name = "Annee"

    niveauChanged = pyqtSignal()

    def __init__(self, data={"id": 0}, parent=None, **kwargs):
        undo = kwargs.pop("undoStack", QUndoStack(parent=self))
        super().__init__(data, parent=parent, undoStack=undo, **kwargs)

    @pyqtProperty(str, notify=niveauChanged)
    def niveau(self):
        return self._data.get("niveau", 0)

    @niveau.setter
    def niveau(self, value: int):
        if self.id:  # pragma: no branch
            self.set_field("niveau", value)

    @pyqtSlot(result="QVariantList")
    def getMenuAnnees(self):
        with db_session:
            res = [
                x.to_dict()
                for x in self._dtb.db.Annee.select().order_by(self._dtb.db.Annee.id)
            ]
            return res
