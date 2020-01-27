from PySide2 import QtGui
from PySide2.QtCore import QObject, Signal, Property, Slot, QRegExp
from PySide2.QtQml import QQmlProperty
from package.constantes import LAYOUT_SIZES
from package.database_mixins.activite_mixin import ActiviteMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
import logging

from pony.orm import db_session

LOG = logging.getLogger(__name__)

MIXINS = [PageMixin, MatiereMixin, ActiviteMixin, RecentsMixin, LayoutMixin]


class DatabaseObject(QObject, *MIXINS):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.models = {}

        for mixin in MIXINS:
            mixin.__init__(self)

        self.setup_connections()

    def setup_connections(self):

        self.currentMatiereChanged.connect(self.onCurrentMatiereChanged)

        self.newPageCreated.connect(self.onNewPageCreated)

        self.recentsItemClicked.connect(self.onRecentsItemClicked)

        self.currentPageChanged.connect(self.currentMatiereChanged)
        self.currentPageChanged.connect(self.models['pageModel'].slotReset)

    def onCurrentMatiereChanged(self):
        self.currentMatiereChanged.connect(self.update_activites)

    def onRecentsItemClicked(self, id, matiere):
        self.currentPage = id
        self.currentMatiere = matiere

    def onNewPageCreated(self, item: dict):
        self.recentsModel.slotResetModel()
        self.currentPage = item["id"]
        self.currentMatiere = item["matiere"]
        self.activites_signal_all[
            item["activiteIndex"]
        ].emit()  # force when currentmatiere doesnt change
