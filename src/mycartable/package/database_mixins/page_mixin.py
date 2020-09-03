import uuid
from functools import partial

from PySide2.QtCore import Slot, Signal, Property, QObject
from PySide2.QtGui import QDesktopServices
from loguru import logger
from package.constantes import TITRE_TIMER_DELAY
from package.convert import soffice_convert, escaped_filename
from package.utils import create_singleshot
from pony.orm import db_session, make_proxy
from loguru import logger

from loguru import logger


class PageMixin:
    currentPageChanged = Signal("QVariantMap")
    newPageCreated = Signal(dict)
    currentTitreChanged = Signal()
    currentTitreSetted = Signal()

    TITRE_TIMER_DELAY = TITRE_TIMER_DELAY

    def __init__(self):
        self._currentPage = ""
        self._currentTitre = ""
        self._currentEntry = None

        self.timer_titre = create_singleshot(self._currentTitreSet)
        self.timer_titre_setted = create_singleshot(
            partial(self._currentTitreSet, setted=True)
        )

        from package.page.page_model import PageModel

        self._pageModel = PageModel(self.db)

    @Property(QObject, notify=currentPageChanged)
    def pageModel(self):
        return self._pageModel

    # newPage
    @Slot(str, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite)
        self.newPageCreated.emit(new_item)

    # currentPage
    @Property(str, notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPageSet(self, new_id):
        if isinstance(new_id, uuid.UUID):
            new_id = str(new_id)
        if self._currentPage == new_id:
            return

        self._currentPage = new_id
        logger.debug(f"CurrentPage changed to {new_id}")

        # breakpoint()
        if new_id:
            with db_session:
                page = self.db.Page[new_id].to_dict()
            self.currentPageChanged.emit(page)
            self.setCurrentEntry()
        else:
            self._currentEntry = None
            self._currentPage = ""
            self.currentPageChanged.emit({})

    @Slot(str)
    def removePage(self, pageId):

        with db_session:
            item = self.db.Page.get(id=pageId)
            if item:
                item.delete()
        # bien après les modifs de database pour être ne pas emmettres
        # signaux avant modif de database
        self.currentPage = ""

    def setCurrentEntry(self):
        with db_session:
            item = self.db.Page.get(id=self.currentPage)
            self._currentTitre = item.titre
            self._currentEntry = make_proxy(item)
            self.currentTitreChanged.emit()

    @Property(str, notify=currentTitreChanged)
    def currentTitre(self):
        return self._currentTitre

    @currentTitre.setter
    def currentTitreSet(self, value):
        if self.currentPage:
            if value != self._currentTitre:
                self._currentTitre = value
                self.timer_titre.start(self.TITRE_TIMER_DELAY)

    def _currentTitreSet(self, setted=False):
        with db_session:
            self._currentEntry.titre = self._currentTitre
        if setted:
            self.currentTitreSetted.emit()
        else:
            self.currentTitreChanged.emit()
        logger.debug(f"nouveau titre : {self._currentTitre}")

    @Slot(str)
    def setCurrentTitre(self, value):
        """comme setter maais sans signal"""

        if self.currentPage and value != self._currentTitre:
            self._currentTitre = value
            self.timer_titre_setted.start(self.TITRE_TIMER_DELAY)

    @Slot()
    def exportToPDF(self):

        filename = escaped_filename(self.currentTitre, ".pdf")
        new_file = soffice_convert(
            self.currentPage, "pdf:writer_pdf_Export", filename, self.ui
        )
        QDesktopServices.openUrl(new_file.as_uri())

    @Slot()
    def exportToOdt(self):
        filename = escaped_filename(self.currentTitre, ".odt")
        new_file = soffice_convert(self.currentPage, "odt", filename, self.ui)
        QDesktopServices.openUrl(new_file.as_uri())
