# currentMatiere
import logging

from PySide2.QtCore import Signal, Property, Slot
from package.utils import MatieresDispatcher

LOG = logging.getLogger(__name__)


class MatiereMixin:
    currentMatiereChanged = Signal()
    matiereListNomChanged = Signal()

    @Property(int, notify=currentMatiereChanged)
    def currentMatiere(self, notify=currentMatiereChanged):
        return self._currentMatiere

    @currentMatiere.setter
    def current_matiere_set(self, value):
        if self._currentMatiere != value and isinstance(value, int):
            self._currentMatiere = value
            LOG.info(f"current matiere set to: {self._currentMatiere}")
            self.currentMatiereChanged.emit()

    @Slot(int)
    def setCurrentMatiereFromIndex(self, value):
        self._currentMatiere = self.m_d.matieres_list_id[value]
        LOG.info(f"current matiere set with index  {value } to: {self._currentMatiere}")

        self.currentMatiereChanged.emit()

    @Slot(int, result=int)
    def getMatiereIndexFromId(self, matiere_id):
        try:
            return self.m_d.id_index[matiere_id]
        except KeyError:
            LOG.info("matiere index non trouvé ou currentMatiere non settée")

    # matieresList
    @Property("QVariantList", notify=matiereListNomChanged)
    def matieresListNom(self):
        return self.m_d.matieres_list_nom

    @Slot()
    def matieresListRefresh(self):
        self.m_d = MatieresDispatcher(self.db)
        self.matiereListNomChanged.emit()
