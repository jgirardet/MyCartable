from PySide2 import QtGui
from PySide2.QtCore import QObject, Signal, Property, Slot, QRegExp
from PySide2.QtQml import QQmlProperty
from package.utils import MatieresDispatcher
import logging

from pony.orm import db_session

LOG = logging.getLogger(__name__)


class DatabaseObject(QObject):
    objectName="ddb"
    fakenotify = Signal()
    matiereListChanged = Signal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.m_d = MatieresDispatcher(self.db)
        self._currentPage = {}
        self._currentMatiere = -1

    # currentMatiere
    currentMatiereChanged = Signal()

    @Property(int, notify=currentMatiereChanged)
    def currentMatiere(self, notify=currentMatiereChanged):
        return self._currentMatiere

    @currentMatiere.setter
    def current_matiere_set(self, value):
        if self._currentMatiere == value:
            return
        elif isinstance(value, int):
            self._currentMatiere = value
        else:
            return
        LOG.info(f"current matiere set to: {self._currentMatiere}")
        self.currentMatiereChanged.emit()

    @Slot(str)
    def setCurrentMatiereFromString(self, value):
        print("set current; ", value)
        self._currentMatiere = self.m_d.nom_id[value]
        LOG.info(f"current matiere set with {value } to: {self._currentMatiere}")

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
    @Property("QVariantList", notify=matiereListChanged)
    def matieresListNom(self):
        return self.m_d.matieres_list_nom

    @Slot()
    def matieresListRefresh(self):
        self.m_d = MatieresDispatcher(self.db)
        self.matiereListChanged.emit()

    # newPage
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            return self.db.Page.new_page(activite=activite)

    # currentPage
    currentPageChanged = Signal()

    @Property("QVariantMap", notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    # @currentPage.setter
    # def currentPage_set(self, value):
    #     "fake function needed for read/Write. property need dict to be set"
    #     pass

    @Slot(int)
    def setCurrentPage(self, value):
        with db_session:
            self._currentPage = self.db.Page.get(id=value).to_dict()
        self.currentPageChanged.emit()

    @Slot(str, int, result="QVariantList")
    def getPagesByMatiereAndActivite(self, matiere_nom, activite_index):
        with db_session:
            if not matiere_nom:
                return []
            matiere = self.db.Matiere.get(id=self.m_d.nom_id[matiere_nom])
            if matiere:
                return self.db.Activite.pages_by_matiere_and_famille(
                    matiere.id, activite_index
                )
            return []


    @Slot(QObject)
    def child(self, un):
        print(un.findChildren(QObject, QRegExp('bla')))
        # print(a)
        # for i in a:
        #     print(QQmlProperty.read(i, "objectName"))
