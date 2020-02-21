from PySide2.QtCore import QObject, Slot, Signal, Property
from package.database_mixins.activite_mixin import ActiviteMixin
from package.database_mixins.image_section_mixin import ImageSectionMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.database_mixins.section_mixin import SectionMixin
import logging

from package.page.text_section import DocumentEditor

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

    updateRecentsAndActivites = Signal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.models = {}

        for mixin in MIXINS:
            mixin.__init__(self)

        self.setup_connections()

    def setup_connections(self):

        self.currentMatiereChanged.connect(self.pagesParSectionChanged)
        self.currentPageChanged.connect(self.onCurrentPageChanged)
        self.currentTitreChanged.connect(self.updateRecentsAndActivites)

        self.newPageCreated.connect(self.onNewPageCreated)
        self.recentsItemClicked.connect(self.onRecentsItemClicked)
        self.sectionAdded.connect(self.onSectionAdded)

        self.updateRecentsAndActivites.connect(self.pagesParSectionChanged)
        self.updateRecentsAndActivites.connect(self.recentsModelChanged)

    def onCurrentPageChanged(self, page):
        self.pageModel.slotReset(page["id"])
        self.currentMatiere = page["matiere"]

    def onNewPageCreated(self, item: dict):
        self.currentPage = item["id"]

    def onRecentsItemClicked(self, id, matiere):
        self.currentPage = id
        self.currentMatiere = matiere

    def onSectionAdded(self, position):
        self.pageModel.insertRow()
