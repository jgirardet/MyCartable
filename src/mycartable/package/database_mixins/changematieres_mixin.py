from typing import List, Union

from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QColor
from loguru import logger
from package.database.structure import Activite, Matiere, GroupeMatiere
from package.default_matiere import MATIERE_GROUPE_BASE, MATIERES_BASE
from pony.orm import db_session, flush, sum


class ChangeMatieresMixin:
    changeMatieres = Signal()

    """
    Partie Activités
    """

    @Slot(str, result="QVariantList")
    @Slot(str, bool, result="QVariantList")
    @db_session
    def addActivite(self, someId: str, append: bool = False) -> List[dict]:
        matiereid: str
        if not append:
            pre = Activite[someId]
            new = Activite(nom="nouvelle", matiere=pre.matiere)
            new.position = pre.position
            matiereid = new.matiere.id
        else:
            matiereid = someId
            Activite(nom="nouvelle", matiere=matiereid)

        return self.get_activites(matiereid)

    @Slot(str, result="QVariantList")
    @db_session
    def getActivites(self, matiere: str) -> List[dict]:
        return self.get_activites(matiere)

    @Slot(str, int, result="QVariantList")
    @db_session
    def moveActiviteTo(self, activite: str, new_pos: int) -> List[dict]:
        ac = Activite[activite]
        ac.position = new_pos
        return self.get_activites(ac.matiere.id)

    @Slot(str, result="QVariantList")
    def removeActivite(self, activite: str) -> List[dict]:
        with db_session:
            ac = Activite[activite]
            mat_id = ac.matiere.id
            ac.delete()
        # ac.flush()
        with db_session:
            return self.get_activites(mat_id)

    def get_activites(self, matiere: str) -> List[dict]:
        res = []
        print(matiere)
        for x in Activite.get_by_position(matiere):
            temp = x.to_dict()
            temp["nbPages"] = len(temp.pop("pages"))  # x.pages.count()
            res.append(temp)
        return res

    @Slot(str, str)
    @db_session
    def updateActiviteNom(self, activiteid: str, nom: str):
        Activite[activiteid].nom = nom

    """
    Partie Matières
    """

    @Slot(str, result="QVariantList")
    @db_session
    def getMatieres(self, groupe: str) -> List[dict]:
        return self.get_matieres(groupe)

    def get_matieres(self, groupe: int) -> List[dict]:
        res = []
        for x in Matiere.get_by_position(groupe):
            temp = x.to_dict()
            temp["nbPages"] = sum(ac.pages.count() for ac in x.activites)
            res.append(temp)
        return res

    @Slot(str, int, result="QVariantList")
    @db_session
    def moveMatiereTo(self, matiere: str, new_pos: int) -> List[dict]:
        mat = Matiere[matiere]
        mat.position = new_pos
        return self.get_matieres(mat.groupe.id)

    @Slot(str, result="QVariantList")
    def removeMatiere(self, matiere: str) -> List[dict]:
        with db_session:
            ac = Matiere[matiere]
            groupe_id = ac.groupe.id
            ac.delete()
        with db_session:
            return self.get_matieres(groupe_id)

    @Slot(str, result="QVariantList")
    @Slot(str, bool, result="QVariantList")
    @db_session
    def addMatiere(self, someId: str, append: bool = False) -> List[dict]:
        groupeid: str
        if not append:
            pre = Matiere[someId]
            groupeid = pre.groupe.id
            new = Matiere(nom="nouvelle", groupe=pre.groupe)
            new.position = pre.position
        else:
            groupeid = someId
            Matiere(nom="nouvelle", groupe=groupeid)

        return self.get_matieres(groupeid)

    @Slot(str, str)
    @db_session
    def updateMatiereNom(self, matiereid: str, nom: str):
        Matiere[matiereid].nom = nom

    """
    Partie GroupeMatiere
    """

    @Slot(str, result="QVariantList")
    @db_session
    def getGroupeMatieres(self, annee: str) -> List[dict]:
        return self.get_groupe_matieres(annee)

    def get_groupe_matieres(self, annee: int) -> List[dict]:
        res = []
        for g in GroupeMatiere.get_by_position(annee):
            temp = g.to_dict()
            temp["nbPages"] = sum(
                ac.pages.count() for m in g.matieres for ac in m.activites
            )
            res.append(temp)
        return res

    @Slot(str, int, result="QVariantList")
    @db_session
    def moveGroupeMatiereTo(self, groupe_matiere: str, new_pos: int) -> List[dict]:
        groupe = GroupeMatiere[groupe_matiere]
        groupe.position = new_pos
        return self.get_groupe_matieres(groupe.annee.id)

    @Slot(str, result="QVariantList")
    def removeGroupeMatiere(self, groupe_matiere: str) -> List[dict]:
        with db_session:
            groupe = GroupeMatiere[groupe_matiere]
            annee_id = groupe.annee.id
            groupe.delete()
        with db_session:
            return self.get_groupe_matieres(annee_id)

    @Slot(str, result="QVariantList")
    @db_session
    def addGroupeMatiere(self, groupeid: str) -> List[dict]:
        pre = GroupeMatiere[groupeid]
        new = GroupeMatiere(nom="nouveau", annee=pre.annee)
        new.position = pre.position
        Matiere(nom="nouvelle matière", groupe=new)

        return self.get_groupe_matieres(new.annee.id)

    @Slot(str, QColor, result="QVariantList")
    def applyGroupeDegrade(self, groupe_id: str, color: QColor) -> List[dict]:
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

    @Slot(str, result="QVariantList")
    def reApplyGroupeDegrade(self, groupeid: str) -> List[dict]:
        with db_session:
            color = GroupeMatiere[groupeid].bgColor
        return self.applyGroupeDegrade(groupeid, color)

    @Slot(str, str)
    @db_session
    def updateGroupeMatiereNom(self, groupeid: str, nom: str):
        GroupeMatiere[groupeid].nom = nom

    @Slot(int)
    @db_session
    def peuplerLesMatieresParDefault(self, annee):
        # print(MATIERE_GROUPE)
        #
        # gm = [GroupeMatiere(**x, annee=annee) for x in MATIERE_GROUPE]
        # flush()
        # print(MATIERES)
        # mat = [Matiere(**x) for x in MATIERES]
        groupes = []
        compteur = 0
        for groupe in MATIERE_GROUPE_BASE:
            gr = GroupeMatiere(
                annee=annee, bgColor=groupe["bgColor"], nom=groupe["nom"]
            )
            for mat in MATIERES_BASE:
                if mat["groupe"] == groupe["id"]:
                    Matiere(groupe=gr, nom=mat["nom"])
                    compteur += 1
            groupes.append(gr)

        for groupe in groupes:
            self.reApplyGroupeDegrade(groupe.id)

        self.ui.sendToast.emit(f"{compteur} matières créées")
        logger.info(f"{len(groupes)} groupes de matières créées")
        logger.info(f"{compteur} matières créées")
        self.changeMatieres.emit()
