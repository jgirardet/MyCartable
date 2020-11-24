from loguru import logger
from PySide2.QtCore import QObject, Signal
from package.database_mixins.equation_mixin import EquationMixin
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.page_mixin import PageMixin
from package.database_mixins.recents_mixin import RecentsMixin
from package.database_mixins.section_mixin import SectionMixin
from package.database_mixins.session import SessionMixin
from package.database_mixins.tableau_mixin import TableauMixin

from loguru import logger
from package.files_path import FILES
from pony.orm import db_session

MIXINS = [
    SessionMixin,
    PageMixin,
    LayoutMixin,
    RecentsMixin,
    SectionMixin,
    EquationMixin,
    TableauMixin,
]


class DatabaseObject(QObject, *MIXINS):

    updateRecentsAndActivites = Signal()

    def __init__(self, db, ui, debug=True):
        super().__init__()
        self.db = db
        self.ui = ui

        for mixin in MIXINS:
            mixin.__init__(self)

        # if not debug:
        # self.setup_settings()
        #
        # if self.annee_active:
        #     self.init_matieres()

        self.files = FILES

        self.setup_connections()

        self.changeAnnee.emit(self.initialize_session())

    def setup_connections(self):

        # todo: self.matiereReset.connect(self.onMatiereReset)
        # todo: self.currentPageChanged.connect(self.onCurrentPageChanged)
        # todo: self.currentTitreSetted.connect(self.updateRecentsAndActivites)

        self.newPageCreated.connect(self.onNewPageCreated)
        self.recentsItemClicked.connect(self.onRecentsItemClicked)
        # todo: self.sectionAdded.connect(self.pageModel.insertRows)
        self.sectionAdded.connect(self.ui.unSetBuzyIndicator)
        # todo: self.sectionRemoved.connect(self.pageModel.removeRow)
        # OK: self.pageActiviteChanged.connect(self.pagesParSectionChanged)

        # mise à jour
        # todo: self.imageChanged.connect(self.updateRecentsAndActivites)
        self.equationChanged.connect(self.updateRecentsAndActivites)
        self.tableauChanged.connect(self.updateRecentsAndActivites)
        # todo: self.textSectionChanged.connect(self.updateRecentsAndActivites)
        # TODO: self.changeMatieres.connect(lambda: self.onChangeAnnee(self.anneeActive))

        # OK: self.updateRecentsAndActivites.connect(self.pagesParSectionChanged)
        # TODO: self.updateRecentsAndActivites.connect(self.recentsModelChanged)

        # session
        self.changeAnnee.connect(self.onChangeAnnee)

    def onCurrentPageChanged(self, page):
        if not page:
            self.pageModel.slotReset(0)
            self.updateRecentsAndActivites.emit()
        else:
            self.pageModel.slotReset(page["id"])
            # TODO:  self.currentMatiere = page["matiere"]

    def onMatiereReset(self):
        self.currentPage = ""

    def onNewPageCreated(self, item: dict):
        self.currentPage = item["id"]

    def onRecentsItemClicked(self, id: str, matiere: str):
        self.currentPage = id
        self.currentMatiere = matiere

    def onChangeAnnee(self, value: int):
        self.currentPage = ""
        self.currentMatiere = ""
        if value:
            self.anneeActive = value
            # TODO: ? self.init_matieres(annee=value)
        self.recentsModelChanged.emit()
        # ok self.matieresListNomChanged.emit()
        # ok self.anneeActiveChanged.emit()
