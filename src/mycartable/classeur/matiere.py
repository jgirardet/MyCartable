from typing import List

from PySide2.QtCore import QObject, Signal, Property, Slot
from PySide2.QtGui import QColor
from pony.orm import db_session, Database


class Matiere(QObject):
    def __init__(self, data: dict):
        super().__init__()
        self._data: dict = data

    @Property(str, constant=True)
    def id(self):
        return self._data.get("id", "")

    @Property(str, constant=True)
    def nom(self):
        return self._data.get("nom", "")

    @Property(QColor, constant=True)
    def bgColor(self):
        return self._data.get("bgColor", "")

    @Property(QColor, constant=True)
    def fgColor(self):
        return self._data.get("fgColor", "")

    def __repr__(self):
        return self.nom


class MatieresDispatcher(QObject):

    matieresListChanged = Signal()

    def __init__(self, db: Database, annee_active: int):
        super().__init__()
        self.db = db
        self.annee_active = annee_active
        with db_session:
            self.annee = self.db.Annee[annee_active]
            self.query = self.annee.get_matieres()
            self.id_index = self._build_id_index()
            self.matieres_list_id = tuple(self.id_index.keys())
            self.matieres_list = self._build_matieres_list()

    @Slot(str, result=int)
    def indexFromId(self, matiere_id):
        return self.id_index[matiere_id]

    @Slot(int, result=int)
    def idFromIndex(self, index):
        return self.matieres_list_id[index]

    @Slot(result="QVariantList")
    @db_session
    def getDeplacePageModel(self) -> List:
        res = []
        for m in self.db.Annee[self.annee_active].get_matieres():
            new = {"activites": []}
            new["nom"] = m.nom
            new["bgColor"] = m.bgColor
            for ac in m.activites.order_by(lambda x: x.position):
                new["activites"].append(
                    {
                        "nom": ac.nom,
                        "id": str(ac.id),
                    }
                )
            res.append(new)
        return res

    @Property("QVariantList", notify=matieresListChanged)
    def matieresList(self):
        return self.matieres_list

    def _build_id_index(self):
        return {str(p.id): index for index, p in enumerate(self.query)}

    def _build_matieres_list(self):
        return [p.to_dict() for p in self.query]
