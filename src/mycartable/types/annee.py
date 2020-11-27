from PySide2.QtCore import Slot, Signal, Property
from mycartable.types.bridge import Bridge
from pony.orm import db_session


class Annee(Bridge):

    """
    Attention Peut être utilisé directement sans new
    Sans être instancié par un id précis

    """

    entity_name = "Annee"

    niveauChanged = Signal()

    def __init__(self, data={"id": 0}, parent=None):
        super().__init__(data, parent)

    @Property(str, notify=niveauChanged)
    def niveau(self):
        return self._data.get("niveau", 0)

    @niveau.setter
    def niveau_set(self, value: int):
        if self.id:
            self.set_field("niveau", value)

    @Slot(result="QVariantList")
    def getMenuAnnees(self):
        with db_session:
            res = [
                x.to_dict()
                for x in self._dtb.db.Annee.select().order_by(self._dtb.db.Annee.id)
            ]
            return res
