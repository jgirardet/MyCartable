from PySide2.QtCore import Slot, Signal, Property
from pony.orm import db_session


class PageMixin:
    # newPage
    @Slot(int)
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite)
        self.recentsModel.modelReset()
        self.currentPage = new_item["id"]
        self.currentMatiere = new_item["matiere"]


    # currentPage
    currentPageChanged = Signal()

    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPageSet(self, new_id):
        self._currentPage = new_id
        self.currentPageChanged.emit()

