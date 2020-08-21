from typing import List

from PySide2.QtCore import Signal, Slot
from package.database.structure import Activite, Matiere
from pony.orm import db_session


class ChangeMatieresMixin:
    changeMatieres = Signal()

    """
    Partie Activités
    """

    @Slot(int, result="QVariantList")
    @db_session
    def addActivite(self, matiere: int) -> List[dict]:
        Activite(nom="nouvelle", matiere=matiere)
        return self.get_activites(matiere)

    @Slot(int, result="QVariantList")
    @db_session
    def getActivites(self, matiere: int) -> List[dict]:
        return self.get_activites(matiere)

    @Slot(int, int, result="QVariantList")
    @db_session
    def moveActiviteTo(self, activite: int, new_pos: int) -> List[dict]:
        ac = Activite[activite]
        ac.position = new_pos
        return self.get_activites(ac.matiere.id)

    @Slot(int, result="QVariantList")
    @db_session
    def removeActivite(self, activite: int) -> List[dict]:
        ac = Activite[activite]
        mat_id = ac.matiere.id
        ac.delete()
        ac.flush()
        return self.get_activites(mat_id)

    def get_activites(self, matiere: int) -> List[dict]:
        return [x.to_dict() for x in Activite.get_by_position(matiere)]

    """
    Partie Matières
    """

    @Slot(int, result="QVariantList")
    @db_session
    def getMatieres(self, groupe: int) -> List[dict]:
        return self.get_matieres(groupe)

    def get_matieres(self, groupe: int) -> List[dict]:
        return [x.to_dict() for x in Matiere.get_by_position(groupe)]

    @Slot(int, int, result="QVariantList")
    @db_session
    def moveMatiereTo(self, matiere: int, new_pos: int) -> List[dict]:
        mat = Matiere[matiere]
        mat.position = new_pos
        return self.get_matieres(mat.groupe.id)

    @Slot(int, result="QVariantList")
    @db_session
    def removeMatiere(self, matiere: int) -> List[dict]:
        ac = Matiere[matiere]
        groupe_id = ac.groupe.id
        ac.delete()
        ac.flush()
        return self.get_matieres(groupe_id)

    @Slot(int, result="QVariantList")
    @db_session
    def addMatiere(self, groupe: int) -> List[dict]:
        Matiere(nom="nouvelle", groupe=groupe)
        return self.get_matieres(groupe)
