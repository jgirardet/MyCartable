from typing import List

from PySide2.QtCore import QObject, Signal, Property, Slot
from PySide2.QtGui import QColor
from .pagelist_model import ActiviteModel
from mycartable.types import Bridge
from pony.orm import db_session, Database


class Matiere(Bridge):
    entity_name = "Matiere"

    def __init__(self, data={}, parent=None):
        super().__init__(data=data, parent=parent)
        self._activites = [
            Activite.get(activite_id, parent=self)
            for activite_id in self._data["activites"]
        ]

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

    @Property(QColor, constant=True)
    def fgColor(self):
        return self._data.get("fgColor", "")

    @Property("QVariantList", constant=True)
    def activites(self):
        return self._activites

    def __repr__(self):
        return "Matiere: " + self.nom


class Activite(Bridge):
    entity_name = "Activite"

    def __init__(self, data={}, parent=None):
        super().__init__(data=data, parent=parent)
        self._pages = ActiviteModel(self.id, parent=self)

    @Property(str, constant=True)
    def nom(self):
        return self._data.get("nom", "")

    @Property(QObject, constant=True)
    def matiere(self):
        return self.parent()

    @Property(QObject, constant=True)
    def position(self):
        return self._data.get("position", "")

    @Property(QObject, constant=True)
    def pages(self):
        return self._pages


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
            for ac in m.activites.order_by(lambda x: x.position):  # pragma: no branch
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
