from signal import signal
from typing import List

from PySide2.QtCore import Slot, Signal
from pony.orm import db_session


class ActiviteMixin:

    pageActiviteChanged = Signal()

    @Slot(int, result="QVariantList")
    @db_session
    def getDeplacePageModel(self, annee: int) -> List:
        res = []
        for m in self.db.Annee[annee].get_matieres():
            new = {"activites": []}
            new["nom"] = m.nom
            new["bgColor"] = m.bgColor
            for ac in m.activites.order_by(lambda x: x.position):
                new["activites"].append(
                    {"nom": ac.nom, "id": str(ac.id),}
                )
            res.append(new)
        return res

    @Slot(str, str)
    @db_session
    def changeActivite(self, pageId: str, activiteId: str):
        self.db.Page[pageId].activite = activiteId
        self.pageActiviteChanged.emit()
