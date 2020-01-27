from PySide2.QtCore import Slot, Signal, Property, QObject
from pony.orm import db_session


class PageMixin:
    currentPageChanged = Signal(int)
    newPageCreated = Signal(dict)

    def __init__(self):
        self._currentPage = 0
        from package.list_models import PageModel
        # self.models.update({"pageModel": [{"type":"texte"}]})
        self.models.update({"pageModel": PageModel()})

    @Property(QObject, notify=currentPageChanged)
    def pageModel(self):
        return self.models["pageModel"]

    # newPage
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite, titre="nouveau")
        self.newPageCreated.emit(new_item)

    # currentPage
    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPageSet(self, new_id):
        self._currentPage = new_id
        self.currentPageChanged.emit(new_id)


    @Slot(result="QVariantMap")
    def fakeModel(self):
        return [{"type": "texte"}]

    # #@Property("QVariantMap")
    # def currentEntry(self):
    #     res = {}
    #     if self.currentMatiere:
    #         with db_session:
    #             item = self.db.Page.get(id=self.currentMatiere)
    #             if item:
    #                 res= item.to_dict()
    #     return res
