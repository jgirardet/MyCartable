from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QColor
from pony.orm import db_session, sum, Database


class ChangeMatieres(QObject):
    changeMatieres = pyqtSignal()

    """
    Partie Activités
    """

    db: Database = None

    @pyqtSlot(str, result="QVariantList")  # ajout par activite id
    @pyqtSlot(str, bool, result="QVariantList")  # append via matiere id
    @db_session
    def addActivite(self, someId: str, append: bool = False) -> List[dict]:
        matiereid: str
        if not append:
            pre = self.db.Activite[someId]
            new = self.db.Activite(nom="nouvelle", matiere=pre.matiere)
            new.position = pre.position
            matiereid = new.matiere.id
        else:
            matiereid = someId
            self.db.Activite(nom="nouvelle", matiere=matiereid)

        return self.get_activites(matiereid)

    @pyqtSlot(str, result="QVariantList")
    @db_session
    def getActivites(self, matiere: str) -> List[dict]:
        return self.get_activites(matiere)

    @pyqtSlot(str, int, result="QVariantList")
    @db_session
    def moveActiviteTo(self, activite: str, new_pos: int) -> List[dict]:
        ac = self.db.Activite[activite]
        ac.position = new_pos
        return self.get_activites(ac.matiere.id)

    @pyqtSlot(str, result="QVariantList")
    def removeActivite(self, activite: str) -> List[dict]:
        with db_session:
            ac = self.db.Activite[activite]
            mat_id = ac.matiere.id
            ac.delete()
        # ac.flush()
        with db_session:
            return self.get_activites(mat_id)

    def get_activites(self, matiere: str) -> List[dict]:
        res = []
        for x in self.db.Activite.get_by_position(matiere):
            temp = x.to_dict()
            temp["nbPages"] = len(temp.pop("pages"))  # x.pages.count()
            res.append(temp)
        return res

    @pyqtSlot(str, str)
    @db_session
    def updateActiviteNom(self, activiteid: str, nom: str):
        self.db.Activite[activiteid].nom = nom

    """
    Partie Matières
    """

    @pyqtSlot(str, result="QVariantList")
    @db_session
    def getMatieres(self, groupe: str) -> List[dict]:
        return self.get_matieres(groupe)

    def get_matieres(self, groupe: int) -> List[dict]:
        res = []
        for x in self.db.Matiere.get_by_position(groupe):
            temp = x.to_dict()
            temp["nbPages"] = sum(ac.pages.count() for ac in x.activites)
            res.append(temp)
        return res

    @pyqtSlot(str, int, result="QVariantList")
    @db_session
    def moveMatiereTo(self, matiere: str, new_pos: int) -> List[dict]:
        mat = self.db.Matiere[matiere]
        mat.position = new_pos
        return self.get_matieres(mat.groupe.id)

    @pyqtSlot(str, result="QVariantList")
    def removeMatiere(self, matiere: str) -> List[dict]:
        with db_session:
            ac = self.db.Matiere[matiere]
            groupe_id = ac.groupe.id
            ac.delete()
        with db_session:
            return self.get_matieres(groupe_id)

    @pyqtSlot(str, result="QVariantList")
    @pyqtSlot(str, bool, result="QVariantList")
    @db_session
    def addMatiere(self, someId: str, append: bool = False) -> List[dict]:
        groupeid: str
        if not append:
            pre = self.db.Matiere[someId]
            groupeid = pre.groupe.id
            new = self.db.Matiere(nom="nouvelle", groupe=pre.groupe)
            new.position = pre.position
        else:
            groupeid = someId
            self.db.Matiere(nom="nouvelle", groupe=groupeid)

        return self.get_matieres(groupeid)

    @pyqtSlot(str, str)
    @db_session
    def updateMatiereNom(self, matiereid: str, nom: str):
        self.db.Matiere[matiereid].nom = nom

    """
    Partie GroupeMatiere
    """

    @pyqtSlot(int, result="QVariantList")
    @db_session
    def getGroupeMatieres(self, annee: int) -> List[dict]:
        return self.get_groupe_matieres(annee)

    def get_groupe_matieres(self, annee: int) -> List[dict]:
        res = []
        for g in self.db.GroupeMatiere.get_by_position(annee):
            temp = g.to_dict()
            temp["nbPages"] = sum(
                ac.pages.count() for m in g.matieres for ac in m.activites
            )
            res.append(temp)
        return res

    @pyqtSlot(str, int, result="QVariantList")
    @db_session
    def moveGroupeMatiereTo(self, groupe_matiere: str, new_pos: int) -> List[dict]:
        groupe = self.db.GroupeMatiere[groupe_matiere]
        groupe.position = new_pos
        return self.get_groupe_matieres(groupe.annee.id)

    @pyqtSlot(str, result="QVariantList")
    def removeGroupeMatiere(self, groupe_matiere: str) -> List[dict]:
        with db_session:
            groupe = self.db.GroupeMatiere[groupe_matiere]
            annee_id = groupe.annee.id
            groupe.delete()
        with db_session:
            return self.get_groupe_matieres(annee_id)

    @pyqtSlot(str, result="QVariantList")
    @db_session
    def addGroupeMatiere(self, groupeid: str) -> List[dict]:

        if groupeid.startswith("annee"):
            annee = groupeid.split(":")[1]
            new = self.db.GroupeMatiere(
                nom="nouveau groupe", annee=int(annee), position=0
            )
        else:
            pre = self.db.GroupeMatiere[groupeid]
            new = self.db.GroupeMatiere(nom="nouveau", annee=pre.annee)
            new.position = pre.position
        self.db.Matiere(nom="nouvelle matière", groupe=new)

        return self.get_groupe_matieres(new.annee.id)

    @pyqtSlot(str, QColor, result="QVariantList")
    def applyGroupeDegrade(self, groupe_id: str, color: QColor) -> List[dict]:
        with db_session:
            groupe = self.db.GroupeMatiere[groupe_id]
            matiere_count = groupe.matieres.count()
            if not matiere_count:
                return []
            elif matiere_count == 1:
                matiere_count = 2
            groupe.bgColor = color.toRgb()
            color = color.toHsv()
            saturation = max(color.saturation(), 40)
            ajout = (saturation - 40) / (matiere_count - 1)
            for mat in self.db.Matiere.get_by_position(groupe_id):
                mat.bgColor = color.toRgb()
                color.setHsv(
                    color.hue(), color.saturation() - round(ajout), color.value()
                )
        with db_session:
            return self.get_matieres(groupe_id)

    @pyqtSlot(str, result="QVariantList")
    def reApplyGroupeDegrade(self, groupeid: str) -> List[dict]:
        with db_session:
            color = self.db.GroupeMatiere[groupeid].bgColor
        return self.applyGroupeDegrade(groupeid, color)

    @pyqtSlot(str, str)
    @db_session
    def updateGroupeMatiereNom(self, groupeid: str, nom: str):
        self.db.GroupeMatiere[groupeid].nom = nom
