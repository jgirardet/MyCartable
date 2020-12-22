from PySide2.QtCore import QObject, Signal, Property
from package.database_mixins.layout_mixin import LayoutMixin
from package.database_mixins.page_mixin import PageMixin

from package.files_path import FILES

MIXINS = [
    PageMixin,
    LayoutMixin,
]


class DatabaseObject(QObject, *MIXINS):

    updateRecentsAndActivites = Signal()

    anneeActiveChanged = Signal()

    @Property(int, notify=anneeActiveChanged)
    def anneeActive(self):
        return 2019

    @anneeActive.setter
    def anneeActive_set(self, value: int):
        self._anneeActive = value
        self.anneeActiveChanged.emit()

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

        # todo: self.changeAnnee.emit(self.initialize_session())

    def setup_connections(self):
        pass

    # todo: self.matiereReset.connect(self.onMatiereReset)
    # todo: self.currentPageChanged.connect(self.onCurrentPageChanged)
    # todo: self.currentTitreSetted.connect(self.updateRecentsAndActivites)

    # todo: self.newPageCreated.connect(self.onNewPageCreated)
    # todo: self.recentsItemClicked.connect(self.onRecentsItemClicked)
    # todo: self.sectionAdded.connect(self.pageModel.insertRows)
    # todo: self.sectionAdded.connect(self.ui.unSetBuzyIndicator)
    # todo: self.sectionRemoved.connect(self.pageModel.removeRow)
    # OK: self.pageActiviteChanged.connect(self.pagesParSectionChanged)

    # mise à jour
    # todo: self.imageChanged.connect(self.updateRecentsAndActivites)
    # todo: self.equationChanged.connect(self.updateRecentsAndActivites)
    # todo: self.tableauChanged.connect(self.updateRecentsAndActivites)
    # todo: self.textSectionChanged.connect(self.updateRecentsAndActivites)
    # TODO: self.changeMatieres.connect(lambda: self.onChangeAnnee(self.anneeActive))

    # OK: self.updateRecentsAndActivites.connect(self.pagesParSectionChanged)
    # TODO: self.updateRecentsAndActivites.connect(self.recentsModelChanged)

    # session
    # todo: self.changeAnnee.connect(self.onChangeAnnee)

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
        # ok: self.recentsModelChanged.emit()
        # ok self.matieresListNomChanged.emit()
        # ok self.anneeActiveChanged.emit()
