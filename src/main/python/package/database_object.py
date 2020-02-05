from PySide2 import QtGui
from PySide2.QtCore import QObject, Signal, Property, Slot, QRegExp
from PySide2.QtQml import QQmlProperty
from package.constantes import LAYOUT_SIZES
from package.database_mixins.activite_mixin import ActiviteMixin
from package.database_mixins.image_section_mixin import ImageSectionMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.database_mixins.section_mixin import SectionMixin
import logging


LOG = logging.getLogger(__name__)

MIXINS = [
    PageMixin,
    MatiereMixin,
    ActiviteMixin,
    LayoutMixin,
    RecentsMixin,
    SectionMixin,
    ImageSectionMixin,
]


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

        self.currentTitreChanged.connect(self.onCurrentTitreChanged)

    def onCurrentMatiereChanged(self):
        self.update_activites()

    def onRecentsItemClicked(self, id, matiere):
        self.currentPage = id
        self.currentMatiere = matiere

    def onNewPageCreated(self, item: dict):
        self.recentsModelChanged.emit()
        self.currentPage = item["id"]
        self.currentMatiere = item["matiere"]
        self.activites_signal_all[
            item["famille"]
        ].emit()  # force when currentmatiere doesnt change

    def onCurrentTitreChanged(self):
        self.update_activites()
        self.recentsModelChanged.emit()
