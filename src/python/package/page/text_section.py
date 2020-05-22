import io
import re

from PySide2 import QtCore
from PySide2.QtCore import QObject, Signal, Property, Slot, QFile, QUrl, QIODevice
from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QBrush,
    QColor,
)
from PySide2.QtWidgets import QApplication
from bs4 import BeautifulSoup
from package.page.blockFormat import P, BlockFormats
from package.page.charFormat import CharFormats
from pony.orm import db_session, make_proxy
from package.database import db


RE_AUTOPARAGRAPH = re.compile(r"^(#{1,6})\s\S.+\S$")


class DocumentEditor(QObject):
    documentChanged = Signal()
    sectionIdChanged = Signal(int)
    selectionStartChanged = (
        Signal()
    )  # pour signal les changements de position de curseur au textarea
    selectionEndChanged = Signal()
    selectionCleared = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proxy = None
        self._cursor = None

        # property handler
        self._document = None
        self._sectionId = 0

        self.dao = QApplication.instance().dao
        self._setup_connections()

    # Other method
    def _setup_connections(self):
        # First setup connection next call _init
        self.sectionIdChanged.connect(self._updateProxy)
        self.sectionIdChanged.connect(self._init)

    @Slot()
    def _init(self):
        # pass
        self._cursor = QTextCursor(self._document)  # type: QTextCursor

    @Property(QObject, notify=documentChanged)
    def document(self):
        return self._document

    @document.setter
    def document_set(self, value: QObject):
        self._document = value.children()[0]  # type: QTextDocument
        self._cursor = QTextCursor(self._document)  # type: QTextCursor
        self.documentChanged.emit()
        # ce signal est géré dans le QML

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        """setté dans le QML"""
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit(value)

    @Property(int, notify=selectionEndChanged)
    def selectionEnd(self):
        return self._cursor.selectionEnd()

    @selectionEnd.setter
    def selectionEnd_set(self, value: int):
        """selection de cursor strictement equivalente à textearea.
        A tester via cursor.hasSelection
        """
        self._cursor.setPosition(value, QTextCursor.KeepAnchor)

    @Property(int, notify=selectionStartChanged)
    def selectionStart(self):
        return self._cursor.selectionStart()

    @selectionStart.setter
    def selectionStart_set(self, value: int):
        """LE sens prévu est de textarea vers Document Editor.
        Pour transmettre une nouvelle position a textarea, il faut emmetre
        selectionStartChanged manuellement.
        """
        self._cursor.setPosition(value)

    @Slot(result=bool)
    def paragraphAutoFormat(self):

        # on agit uniquement en fin de ligne
        if not self._cursor.atBlockEnd():
            return False

        # on check les expressions régulières suivantes:
        #   #, ##, ###, ####, #####, ######
        line = self._cursor.block().text()
        matched = RE_AUTOPARAGRAPH.search(line)
        if not matched:
            return False

        self._cursor.beginEditBlock()

        bloc = self._cursor.block()
        level = len(matched.groups()[0])

        # strip les # et applique les styles par défault
        text = bloc.text()[level + 1 :]
        self._cursor = QTextCursor(bloc)
        self._cursor.setBlockFormat(BlockFormats[level])
        self._cursor.select(QTextCursor.LineUnderCursor)
        self._cursor.insertText(text)
        self._cursor.movePosition(QTextCursor.StartOfBlock)
        self._cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self._cursor.setCharFormat(CharFormats[level])

        # simple sécurité
        self._cursor.clearSelection()

        if self._cursor.block().next().isValid():
            # en milieu de paragraphie,on passe simplement à la ligne du dessous
            self._cursor.movePosition(QTextCursor.NextBlock)
            self.selectionStartChanged.emit()
        else:
            # en fin de paragraphe, on créer un nouvelle ligne d'écritue simple.
            self._cursor.movePosition(QTextCursor.End)
            self._cursor.insertBlock(BlockFormats["p"])
            self._cursor.select(QTextCursor.BlockUnderCursor)
            # self._cursor.setBlockCharFormat(QTextCharFormat())
            self._cursor.setBlockCharFormat(CharFormats["p"])
            self._cursor.clearSelection()

        self._cursor.endEditBlock()
        return True

    @Slot("QVariantMap")
    def setStyleFromMenu(self, data):
        if not self._cursor.hasSelection():
            self._cursor.select(QTextCursor.WordUnderCursor)
        f = QTextCharFormat()
        if "style" in data:

            if "fgColor" in data["style"]:
                f.setForeground(QBrush(data["style"]["fgColor"]))

            if "underline" in data["style"]:
                f.setFontUnderline(data["style"]["underline"])

        self._cursor.mergeCharFormat(f)
        self.selectionCleared.emit()

    @Slot(int)
    def _updateProxy(self, value):
        print(value)
        with db_session:

            item = db.TextSection.get(id=value)
            print("item", item)
            if item:
                self._proxy = make_proxy(item)

                # set primitive style
                # aaa = QFile(":/css/textsection.css")
                # aaa.open(QFile.ReadOnly | QFile.Text)
                # self._document.setDefaultStyleSheet(aaa.readData(aaa.bytesAvailable()))
                # print(self._document.defaultStyleSheet())
                self._document.setDefaultStyleSheet(
                    "body { font-size: 16pt; color: black; }"
                )
                # # on convertit en html si plain text
                if not bool(BeautifulSoup(item.text, "html.parser").find()):
                    item.text = f"<html><body>{item.text}</body></html>"

                # load content
                # print(item.text)
                self.document.setHtml(item.text)
                # print(self.document.toHtml())
                self._update_block_format()

                # set connection later to avoid save on first load
                self._document.contentsChanged.connect(self.onDocumenContentsChanged)
                # self._document.contentsChanged.connect(self.dao.updateRecentsAndActivites)

            else:
                self._proxy = None

    # documentContentChanged = Signal()

    @Slot()
    def onDocumenContentsChanged(self):
        with db_session:
            self._proxy.text = self.document.toHtml()
            # print("//////", self._proxy.text, "///////")
        self.dao.updateRecentsAndActivites.emit()
        # self.documentChanged.emit()
        # self.documentContentChanged.emit()

    def _update_block_format(self):
        b = self._document.begin()
        while b.isValid():
            c = QTextCursor(b)
            heading_level = b.blockFormat().headingLevel()
            if heading_level:
                c.setBlockFormat(BlockFormats[heading_level])
                c.select(QTextCursor.BlockUnderCursor)
                c.setCharFormat(CharFormats[heading_level])
            else:
                c.setBlockFormat(BlockFormats["p"])
                # c.setCharFormat(CharFormats["p"])

            b = b.next()
