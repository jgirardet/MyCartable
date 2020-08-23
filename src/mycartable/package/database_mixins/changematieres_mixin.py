from typing import List, Union

from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QColor
from package.database.structure import Activite, Matiere, GroupeMatiere
from pony.orm import db_session, flush, sum


class ChangeMatieresMixin:
    changeMatieres = Signal()

    """
    Partie Activités
    """

    @Slot(int, result="QVariantList")
    @Slot(str, result="QVariantList")
    @db_session
    def addActivite(self, someId: Union[int, str]) -> List[dict]:
        matiereid: int
        if isinstance(someId, int):
            pre = Activite[someId]
            new = Activite(nom="nouvelle", matiere=pre.matiere)
            new.position = pre.position
            matiereid = new.matiere.id
        elif isinstance(someId, str):
            matiereid = int(someId)
            Activite(nom="nouvelle", matiere=matiereid)

        return self.get_activites(matiereid)

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
    def removeActivite(self, activite: int) -> List[dict]:
        with db_session:
            ac = Activite[activite]
            mat_id = ac.matiere.id
            ac.delete()
        # ac.flush()
        with db_session:
            return self.get_activites(mat_id)

    def get_activites(self, matiere: int) -> List[dict]:
        res = []
        for x in Activite.get_by_position(matiere):
            temp = x.to_dict()
            temp["nbPages"] = x.pages.count()
            res.append(temp)
        return res

    @Slot(int, str)
    @db_session
    def updateActiviteNom(self, activiteid: int, nom: str):
        Activite[activiteid].nom = nom

    """
    Partie Matières
    """

    @Slot(int, result="QVariantList")
    @db_session
    def getMatieres(self, groupe: int) -> List[dict]:
        return self.get_matieres(groupe)

    def get_matieres(self, groupe: int) -> List[dict]:
        res = []
        for x in Matiere.get_by_position(groupe):
            temp = x.to_dict()
            temp["nbPages"] = sum(ac.pages.count() for ac in x.activites)
            res.append(temp)
        return res

    @Slot(int, int, result="QVariantList")
    @db_session
    def moveMatiereTo(self, matiere: int, new_pos: int) -> List[dict]:
        mat = Matiere[matiere]
        mat.position = new_pos
        return self.get_matieres(mat.groupe.id)

    @Slot(int, result="QVariantList")
    def removeMatiere(self, matiere: int) -> List[dict]:
        with db_session:
            ac = Matiere[matiere]
            groupe_id = ac.groupe.id
            ac.delete()
        with db_session:
            return self.get_matieres(groupe_id)

    @Slot(int, result="QVariantList")
    @db_session
    def addMatiere(self, matiereid: int) -> List[dict]:
        pre = Matiere[matiereid]
        new = Matiere(nom="nouvelle", groupe=pre.groupe)
        new.position = pre.position

        return self.get_matieres(new.groupe.id)

    @Slot(int, str)
    @db_session
    def updateMatiereNom(self, matiereid: int, nom: str):
        Matiere[matiereid].nom = nom

    """
    Partie GroupeMatiere
    """

    @Slot(int, result="QVariantList")
    @db_session
    def getGroupeMatieres(self, annee: int) -> List[dict]:
        return self.get_groupe_matieres(annee)

    def get_groupe_matieres(self, annee: int) -> List[dict]:
        return [x.to_dict() for x in GroupeMatiere.get_by_position(annee)]

    @Slot(int, int, result="QVariantList")
    @db_session
    def moveGroupeMatiereTo(self, groupe_matiere: int, new_pos: int) -> List[dict]:
        groupe = GroupeMatiere[groupe_matiere]
        groupe.position = new_pos
        return self.get_groupe_matieres(groupe.annee.id)

    @Slot(int, result="QVariantList")
    def removeGroupeMatiere(self, groupe_matiere: int) -> List[dict]:
        with db_session:
            groupe = GroupeMatiere[groupe_matiere]
            annee_id = groupe.annee.id
            groupe.delete()
        with db_session:
            return self.get_groupe_matieres(annee_id)

    @Slot(int, result="QVariantList")
    @db_session
    def addGroupeMatiere(self, groupeid: int) -> List[dict]:
        pre = GroupeMatiere[groupeid]
        new = GroupeMatiere(nom="nouveau", annee=pre.annee)
        new.position = pre.position
        Matiere(nom="nouvelle matière", groupe=new)

        return self.get_groupe_matieres(new.annee.id)

    @Slot(int, QColor, result="QVariantList")
    def applyGroupeDegrade(self, groupe_id: int, color: QColor) -> List[dict]:
        with db_session:
            groupe = GroupeMatiere[groupe_id]
            matiere_count = groupe.matieres.count()
            if not matiere_count:
                return []
            elif matiere_count == 1:
                matiere_count = 2
            groupe.bgColor = color.toRgb()
            color = color.toHsv()
            saturation = max(color.saturation(), 40)
            ajout = (saturation - 40) / (matiere_count - 1)
            for mat in Matiere.get_by_position(groupe_id):
                mat.bgColor = color.toRgb()
                color.setHsv(color.hue(), color.saturation() - ajout, color.value())
        with db_session:
            return self.get_matieres(groupe_id)

    @Slot(int, result="QVariantList")
    def reApplyGroupeDegrade(self, groupeid) -> List[dict]:
        with db_session:
            color = GroupeMatiere[groupeid].bgColor
        return self.applyGroupeDegrade(groupeid, color)

    @Slot(int, str)
    @db_session
    def updateGroupeMatiereNom(self, groupeid: int, nom: str):
        GroupeMatiere[groupeid].nom = nom
