import logging
from PySide2.QtCore import QObject, Signal
from package.database_mixins.dev_mixin import DevMixin
from package.database_mixins.equation_mixin import EquationMixin
from package.database_mixins.image_section_mixin import ImageSectionMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.matiere_mixin import MatiereMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.database_mixins.section_mixin import SectionMixin
from package.database_mixins.settings_mixin import SettingsMixin
from package.database_mixins.tableau_mixin import TableauMixin
from package.database_mixins.text_mixin import TextSectionMixin

LOG = logging.getLogger(__name__)

MIXINS = [
    PageMixin,
    MatiereMixin,
    LayoutMixin,
    RecentsMixin,
    SectionMixin,
    ImageSectionMixin,
    SettingsMixin,
    DevMixin,
    EquationMixin,
    TextSectionMixin,
    TableauMixin,
]


class DatabaseObject(QObject, *MIXINS):

    updateRecentsAndActivites = Signal()

    def __init__(self, db, debug=True):
        super().__init__()
        self.db = db

        for mixin in MIXINS:
            mixin.__init__(self)

        if not debug:
            self.setup_settings()

        if self.annee_active:
            self.init_matieres()

        self.setup_connections()

    def setup_connections(self):

        self.matiereReset.connect(self.onMatiereReset)
        self.currentPageChanged.connect(self.onCurrentPageChanged)
        self.currentTitreSetted.connect(self.updateRecentsAndActivites)

        self.newPageCreated.connect(self.onNewPageCreated)
        self.recentsItemClicked.connect(self.onRecentsItemClicked)
        self.sectionAdded.connect(self.pageModel.insertRows)
        self.sectionRemoved.connect(self.pageModel.removeRow)

        # mise à jour
        self.imageChanged.connect(self.updateRecentsAndActivites)
        self.equationChanged.connect(self.updateRecentsAndActivites)
        self.tableauChanged.connect(self.updateRecentsAndActivites)
        self.textSectionChanged.connect(self.updateRecentsAndActivites)

        self.updateRecentsAndActivites.connect(self.pagesParSectionChanged)
        self.updateRecentsAndActivites.connect(self.recentsModelChanged)

        self.changeAnnee.connect(self.onChangeAnnee)

    def onCurrentPageChanged(self, page):
        if not page:
            self.pageModel.slotReset(0)
            self.updateRecentsAndActivites.emit()
        else:
            self.pageModel.slotReset(page["id"])
            self.currentMatiere = page["matiere"]

    def onMatiereReset(self):
        self.currentPage = 0

    def onNewPageCreated(self, item: dict):
        self.currentPage = item["id"]

    def onRecentsItemClicked(self, id, matiere):
        self.currentPage = id
        self.currentMatiere = matiere

    def onChangeAnnee(self, value: int):
        self.currentPage = 0
        self.currentMatiere = 0
        self.setup_settings(value)
        self.init_matieres(annee=value)
        self.recentsModelChanged.emit()
        self.matieresListNomChanged.emit()
        self.anneeActiveChanged.emit()
