import re

from PySide2.QtCore import QObject, Signal, Property, Slot
from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QBrush,
    QColor,
    QTextBlockFormat,
)
from package.page.blockFormat import H1, H2, H3, P, BlockFormats
from package.page.charFormat import H1c, H2c, CharFormats
from pony.orm import db_session, make_proxy
from package.database import db

RE_HEADER = "^#+\s.+"


class DocumentEditor(QObject):
    documentChanged = Signal()
    cursorPositionChanged = Signal(int)
    sectionIdChanged = Signal(int)
    selectionStartChanged = Signal()
    selectionEndChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proxy = None
        self._cursor = None

        # property handler
        self._document = None
        self._sectionId = 0
        self._position = 0
        self._selectionStart = None
        self._selectionEnd = None

        self._setup_connections()

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
        self._cursor.setPosition(value, QTextCursor.KeepAnchor)

    @Property(int, notify=selectionStartChanged)
    def selectionStart(self):
        return self._cursor.selectionStart()

    @selectionStart.setter
    def selectionStart_set(self, value: int):
        self._cursor.setPosition(value)

    @Slot()
    def _init(self):
        self._cursor = QTextCursor(self._document)  # type: QTextCursor

        # self._document.contentsChanged.connect(self.print_html)

    @Slot()
    def print_html(self):
        pass
        print(self._document.toHtml())

    def _iter_document(self):
        bloc = self.document.begin()
        while True:
            yield bloc
            bloc = bloc.next()
            if bloc == self.document.end() or not bloc.isValid():
                return

    @Slot(result=bool)
    def paragraphAutoFormat(self):

        # on agit uniquement en fin de ligne
        if not self._cursor.atBlockEnd():
            return False

        # on check les expressions régulières suivantes:
        #   #, ##, ###, ####, #####, ######
        line = self._cursor.block().text()
        matched = re.search("^(#+)\s.+", line)
        if not matched:
            return False

        self._cursor.beginEditBlock()

        bloc = self._cursor.block()
        level = len(matched.groups()[0])
        if level > 6:
            self._cursor.endEditBlock()
            return False

        # strip les # et applique les styles par défault
        text = bloc.text()[level + 1 :]
        self._cursor.select(QTextCursor.BlockUnderCursor)
        self._cursor.insertBlock(BlockFormats[level])
        self._cursor.insertText(text)
        self._cursor.movePosition(QTextCursor.StartOfBlock)
        self._cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self._cursor.setCharFormat(CharFormats[level])

        # simple sécurité
        self._cursor.clearSelection()

        # en milieu de paragraphie,on passe simplement à la ligne du dessous
        if self._cursor.block().next().isValid():
            self._cursor.movePosition(QTextCursor.NextBlock)
            self.cursorPositionChanged.emit(self._cursor.position())
        # en fin de paragraphe, on créer un nouvelle ligne d'écritue simple.
        else:
            self._cursor.movePosition(QTextCursor.End)
            self._cursor.insertBlock(BlockFormats["p"])
            self._cursor.select(QTextCursor.BlockUnderCursor)
            self._cursor.setBlockCharFormat(QTextCharFormat())
            self._cursor.clearSelection()

        self._cursor.endEditBlock()
        return True

    @Slot("QVariantMap")
    def setStyle(self, data):
        if not self._cursor.hasSelection():
            self._cursor.select(QTextCursor.WordUnderCursor)
        f = QTextCharFormat()
        if data["type"] == "color":
            f.setForeground(QBrush(QColor(data["value"])))

        self._cursor.mergeCharFormat(f)

    @Slot(int)
    def _updateProxy(self, value):
        with db_session:

            item = db.TextSection.get(id=value)
            if item:
                # self._document.setDefaultStyleSheet("p {margin-top:30px;}")
                # self._cursor.insertHtml(f"<body><p>{item.text}</p></body>")
                self._document.setHtml(item.text)
                html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:''; font-weight:400; font-style:normal;">
<h1 style=" margin-top:50px; margin-bottom:50px; margin-left:50px; margin-right:50px; -qt-block-indent:0; text-indent:0px;">aaa11</h1>
<h2 style=" margin-top:50px; margin-bottom:50px; margin-left:50px; margin-right:50px; -qt-block-indent:0; text-indent:0px;">bbb22</h2>
<h3 style=" margin-top:50px; margin-bottom:50px; margin-left:50px; margin-right:50px; -qt-block-indent:0; text-indent:0px;">aaa33</h3>
<h2 style=" margin-top:50px; margin-bottom:50px; margin-left:50px; margin-right:50px; -qt-block-indent:0; text-indent:0px;">bbb22</h2>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:2px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">pppppp</p></body></html>"""
                # self._document.setHtml(html)
                self._updateStyle()

                self._proxy = make_proxy(item)
            else:
                self._proxy = None

            print(self._document.toHtml())

    def _updateStyle(self):
        b = self._document.begin()
        c = QTextCursor(b)
        while b.isValid():
            if b.blockFormat().headingLevel() == 1:
                c.setBlockFormat(H1)
                c.select(QTextCursor.BlockUnderCursor)
                c.setCharFormat(H1c)
            elif b.blockFormat().headingLevel() == 2:
                c.setBlockFormat(H2)
                c.select(QTextCursor.BlockUnderCursor)
                c.setCharFormat(H2c)
            elif b.blockFormat().headingLevel() == 3:
                c.setBlockFormat(H3)
            elif b.blockFormat().headingLevel() == 0:
                c.setBlockFormat(P)
            b = b.next()
            c.movePosition(QTextCursor.NextBlock)

    # Other method
    def _setup_connections(self):
        self.sectionIdChanged.connect(self._updateProxy)
        self.sectionIdChanged.connect(self._init)
