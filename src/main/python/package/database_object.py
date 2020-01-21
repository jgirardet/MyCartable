from PySide2 import QtGui
from PySide2.QtCore import QObject, Signal, Property, Slot, QRegExp
from PySide2.QtQml import QQmlProperty
from package.constantes import LAYOUT_SIZES
from package.database_mixins.activite_mixin import ActiviteMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.utils import MatieresDispatcher
import logging

from pony.orm import db_session

LOG = logging.getLogger(__name__)


class DatabaseObject(QObject, PageMixin, MatiereMixin, ActiviteMixin, RecentsMixin):
    objectName = "ddb"

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.m_d = MatieresDispatcher(self.db)
        self._currentPage = {}
        self._currentMatiere = -1
        self.models = {}
        self.setup_connections()

    def setup_connections(self):

        self.currentMatiereChanged.connect(self.lessonsListChanged)
        self.currentMatiereChanged.connect(self.exercicesListChanged)
        self.currentMatiereChanged.connect(self.evaluationsListChanged)

        # self.currentPageChanged.conect(self.)

    # init sizes
    @Slot(str, result=float)
    def getLayoutSizes(self, nom):
        return LAYOUT_SIZES[nom]

    @Slot(int)
    def recentsItemClicked(self, id: int):
        with db_session:
            item = self.db.Page.get(id=id)
            if item:
                self.currentPage = item.id
                self.currentMatiere = item.activite.matiere.id
