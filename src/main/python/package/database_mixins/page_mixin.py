from PySide2.QtCore import Slot, Signal, Property
from pony.orm import db_session


class PageMixin:
    currentPageChanged = Signal()
    newPageCreated = Signal()

    # def setup_connections(self):
    #     self.newPageCreated.connect(self.currentPageChanged)

    # newPage
    @Slot(int)
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite, titre="nouveau")

        self.recentsModel.modelReset()
        self.currentPage = new_item["id"]
        self.currentMatiere = new_item["matiere"]
        print(activite%3)
        self.update_activite()


    # currentPage


    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPageSet(self, new_id):
        self._currentPage = new_id
        self.currentPageChanged.emit()
        print("emited")


    # #@Property("QVariantMap")
    # def currentEntry(self):
    #     res = {}
    #     if self.currentMatiere:
    #         with db_session:
    #             item = self.db.Page.get(id=self.currentMatiere)
    #             if item:
    #                 res= item.to_dict()
    #     return res