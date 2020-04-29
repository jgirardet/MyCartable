# currentMatiere
import logging

from PySide2.QtCore import Signal, Property, Slot
from pony.orm import db_session, ObjectNotFound

LOG = logging.getLogger(__name__)


class MatiereMixin:
    currentMatiereChanged = Signal()
    matieresListNomChanged = Signal()
    setCurrentMatiereFromIndexSignal = Signal(int)
    matiereReset = Signal()

    def __init__(self):
        self._currentMatiere = 0
        self.setCurrentMatiereFromIndexSignal.connect(self.setCurrentMatiereFromIndex)
        self.currentMatiereChanged.connect(self.pagesParSectionChanged)

    def init_matieres(self, annee=None):
        annee = annee or self.annee_active
        self.m_d = MatieresDispatcher(self.db, self.annee_active)

    @Property(int, notify=currentMatiereChanged)
    def currentMatiere(self):
        return self._currentMatiere

    @currentMatiere.setter
    def current_matiere_set(self, value):
        if self._currentMatiere != value and isinstance(value, int):
            self._currentMatiere = value
            LOG.debug(f"current matiere set to: {self._currentMatiere}")
            self.currentMatiereChanged.emit()

    @Slot(int)
    def setCurrentMatiereFromIndex(self, value):
        self.currentMatiere = self.m_d.matieres_list_id[value]
        LOG.debug(
            f"current matiere set with index  {value } to: {self._currentMatiere}"
        )
        self.matiereReset.emit()

    @Slot(int, result=int)
    def getMatiereIndexFromId(self, matiere_id):
        try:
            return self.m_d.id_index[matiere_id]
        except KeyError:
            LOG.debug("matiere index non trouvé ou currentMatiere non settée")

    # matieresList
    @Property("QVariantList", notify=matieresListNomChanged)
    def matieresList(self):
        return self.m_d.matieres_list

    @Slot()
    def matieresListRefresh(self):
        self.init_matieres(annee=self.annee_active)
        self.matieresListNomChanged.emit()

    pagesParSectionChanged = Signal()

    @Property("QVariantList", notify=pagesParSectionChanged)
    def pagesParSection(self):
        res = []
        if self.currentMatiere:
            with db_session:
                matiere = self.db.Matiere[self.currentMatiere]
                res = matiere.pages_par_section()
        return res

    # @pagesParSection.setter
    # def pagesParSection_set(self, value: int):
    #     self._pagesParSection = value
    #     self.pagesParSectionChanged.emit()

    CurrentMatiereItemChanged = Signal()

    @Property("QVariantMap", notify=CurrentMatiereItemChanged)
    def currentMatiereItem(self):
        with db_session:
            mat = self.db.Matiere[self.currentMatiere]
            return mat.to_dict()

    #
    # @CurrentMatiereColor.setter
    # def CurrentMatiereColor_set(self, value: int):
    #     self._CurrentMatiereColor = value
    #     self.CurrentMatiereColorChanged.emit()
    #


class MatieresDispatcher:
    def __init__(self, db, annee_active):
        self.db = db
        with db_session:
            try:
                self.annee = self.db.Annee[annee_active]
            except ObjectNotFound:
                self.annee = self.db.Annee(id=annee_active)
            self.query = self.annee.get_matieres()
            # self.query = self.db.Matiere.select().order_by(self.db.Matiere.id)
            self.nom_id = self._build_nom_id()
            self.id_nom = self._build_id_nom()
            self.id_index = self._build_id_index()
            self.matieres_list = self._build_matieres_list()
        self.matieres_list_id = self._build_matieres_list_id()
        self.matieres_list_nom = self._build_matieres_list_nom()

    def _build_nom_id(self):
        return {p.nom: p.id for p in self.query}

    def _build_id_nom(self):
        return {p.id: p.nom for p in self.query}

    def _build_id_index(self):
        return {p.id: index for index, p in enumerate(self.query)}

    def _build_matieres_list_nom(self):
        return tuple(self.nom_id.keys())

    def _build_matieres_list(self):
        return [p.to_dict() for p in self.query]

    def _build_matieres_list_id(self):
        return tuple(self.nom_id.values())
