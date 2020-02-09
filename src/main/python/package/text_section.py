import re

from PySide2.QtCore import QObject, Signal, Property, Slot
from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QFont,
    QBrush,
    QColor,
    QTextBlock,
    QTextBlockFormat,
)
from pony.orm import db_session, make_proxy
from package.database import db

RE_HEADER = "^#+\s.+"


class DocumentEditor(QObject):
    documentChanged = Signal()
    positionChanged = Signal(int)
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
        self._document.setDefaultStyleSheet("body { p {font-size:30pt; } }")
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
        pass
        return self._cursor.selectionEnd()

    @selectionEnd.setter
    def selectionEnd_set(self, value: int):
        pass
        # self._cursor.setPosition(value, QTextCursor.KeepAnchor)

    @Property(int, notify=selectionStartChanged)
    def selectionStart(self):
        pass
        return self._cursor.selectionStart()

    @selectionStart.setter
    def selectionStart_set(self, value: int):
        pass
        self._cursor.setPosition(value)

    #
    # def documentContentsChange(self, pos, removed, added):
    #     f = QTextCharFormat()
    #     f.setFontItalic(False if self._cursor.charFormat().fontItalic() else True)
    #     self._cursor.select(QTextCursor.LineUnderCursor)
    #     self._cursor.setCharFormat(f)
    #     with db_session:
    #         self._db_instance.text = self._document.toHtml()
    #     # print(pos, removed, added)
    #     # print(self._document.toHtml())

    # Slots

    @Slot()
    def _init(self):
        self._cursor = QTextCursor(self._document)  # type: QTextCursor

        # self._document.contentsChanged.connect(self.print_html)

    @Slot()
    def print_html(self):
        print(self._document.toHtml())

    def _iter_document(self):
        bloc = self.document.begin()
        while True:
            yield bloc
            bloc = bloc.next()
            if bloc == self.document.end() or not bloc.isValid():
                return

    @Slot(result=bool)
    def inspect(self):

        print(self._cursor.positionInBlock())
        if not self._cursor.atBlockEnd():
            return False

        matched = []
        P = QTextBlockFormat()
        P.setHeadingLevel(0)
        H1 = QTextBlockFormat()
        H1.setHeadingLevel(1)

        bloc = self._document.findBlock(self._cursor.position())
        self._cursor.select(QTextCursor.LineUnderCursor)
        line = self._cursor.selectedText()
        matched = re.search("^(#+)\s.+", line)
        if matched:
            level = len(matched.groups()[0])
            new_level = QTextBlockFormat()
            new_level.setHeadingLevel(level)
            self._cursor.movePosition(QTextCursor.StartOfLine)
            self._cursor.setPosition(
                self._cursor.position() + level + 1, QTextCursor.KeepAnchor
            )
            self._cursor.removeSelectedText()
            self._cursor.mergeBlockFormat(new_level)

        else:
            return False

        self._cursor.clearSelection()

        #
        if bloc == self._document.lastBlock():
            self._cursor.movePosition(QTextCursor.End)
            self._cursor.insertBlock(P)
        else:
            self._cursor = QTextCursor(bloc.next())

        print(self._document.toHtml())
        return True

    @Slot("QVariantMap")
    def setStyle(self, data):
        if not self._cursor.hasSelection():
            self._cursor.select(QTextCursor.WordUnderCursor)
        f = QTextCharFormat()
        if data["type"] == "color":
            print(data)
            f.setForeground(QBrush(QColor(data["value"])))

        self._cursor.mergeCharFormat(f)

    @Slot(int)
    def _updateProxy(self, value):
        with db_session:

            item = db.TextSection.get(id=value)
            if item:
                print(self._document.defaultStyleSheet())

                self._document.setHtml(item.text)
                self._document.setDefaultStyleSheet("body { p {font-size:30pt; } }")

                self._proxy = make_proxy(item)
            else:
                self._proxy = None

    # def

    # Other method
    def _setup_connections(self):
        self.sectionIdChanged.connect(self._updateProxy)
        self.sectionIdChanged.connect(self._init)
