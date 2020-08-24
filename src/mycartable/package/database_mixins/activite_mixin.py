from signal import signal
from typing import List

from PySide2.QtCore import Slot, Signal
from package.database.structure import Annee, Page
from pony.orm import db_session


class ActiviteMixin:

    pageActiviteChanged = Signal()

    @Slot(int, result="QVariantList")
    @db_session
    def getDeplacePageModel(self, annee: int) -> List:
        res = []
        for m in Annee[annee].get_matieres():
            new = {"activites": []}
            new["nom"] = m.nom
            new["bgColor"] = m.bgColor
            for ac in m.activites.order_by(lambda x: x.position):
                new["activites"].append(
                    {"nom": ac.nom, "id": ac.id,}
                )
            res.append(new)
        return res

    @Slot(int, int)
    @db_session
    def changeActivite(self, pageId: int, activiteId: int):
        Page[pageId].activite = activiteId
        self.pageActiviteChanged.emit()
