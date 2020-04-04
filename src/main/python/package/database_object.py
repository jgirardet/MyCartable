import logging
from PySide2.QtCore import QObject, Signal
from package.database_mixins.activite_mixin import ActiviteMixin
from package.database_mixins.image_section_mixin import ImageSectionMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.database_mixins.section_mixin import SectionMixin
from package.database_mixins.settings_mixin import SettingsMixin


LOG = logging.getLogger(__name__)

MIXINS = [
    PageMixin,
    MatiereMixin,
    ActiviteMixin,
    LayoutMixin,
    RecentsMixin,
    SectionMixin,
    ImageSectionMixin,
    SettingsMixin,
]


class DatabaseObject(QObject, *MIXINS):

    updateRecentsAndActivites = Signal()

    def __init__(self, db, debug=True):
        super().__init__()
        self.db = db
        self.models = {}

        for mixin in MIXINS:
            mixin.__init__(self)

        if not debug:
            self.setup_settings()
        self.setup_connections()

    def setup_connections(self):

        self.matiereReset.connect(self.onMatiereReset)
        self.currentPageChanged.connect(self.onCurrentPageChanged)
        self.currentTitreSetted.connect(self.updateRecentsAndActivites)

        self.newPageCreated.connect(self.onNewPageCreated)
        self.recentsItemClicked.connect(self.onRecentsItemClicked)
        self.sectionAdded.connect(self.pageModel.insertRow)
        self.sectionRemoved.connect(self.pageModel.removeRow)

        self.updateRecentsAndActivites.connect(self.pagesParSectionChanged)
        self.updateRecentsAndActivites.connect(self.recentsModelChanged)

    def onCurrentPageChanged(self, page):
        if not page:
            self.pageModel.slotReset(0)
            self.updateRecentsAndActivites.emit()
        else:
            self.pageModel.slotReset(page["id"])
            self.currentMatiere = page["matiere"]

    def onMatiereReset(self):
        # self.pagesParSectionChanged.emit()
        # self.onCurrentPageChanged({})
        # self.onCurrentPageChanged(0)
        self.currentPage = 0

    def onNewPageCreated(self, item: dict):
        self.currentPage = item["id"]

    def onRecentsItemClicked(self, id, matiere):
        self.currentPage = id
        self.currentMatiere = matiere
