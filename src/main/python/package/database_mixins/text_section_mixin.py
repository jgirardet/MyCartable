from time import sleep

from PyQt5.QtGui import QTextDocument
from PySide2.QtCore import Slot, Signal, Property, QObject
from PySide2.QtGui import QTextCursor, QTextCharFormat, QFont
from pony.orm import db_session, make_proxy


class TextSectionMixin:
    documentChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._document = None  # QTextDocument()
        self._cursor = QTextCursor()
        # self.documentChanged.connect(self.changed)

    @Slot(QObject)
    def setDocument(self, obj):
        self._document = obj.children()[0]
        self._document.contentsChanged.connect(self.changed_none)
        self._cursor = QTextCursor(self._document)
        self._document.setHtml("blabl")

    @Property(QTextCursor)
    def cursor(self):
        return self._cursor

    @Property(QTextDocument, notify=documentChanged)
    def document(self):
        return self._document

    @document.setter
    def document_set(self, doc: QTextDocument):
        self._document = doc

    @Slot()
    def changed_none(self):
        # print(doc.textDocument)
        print(self.document.toHtml())
        # f = QTextCharFormat()
        # f.setFontItalic(True)
        # # print(self._cursor.setPosition(20))
        # self._cursor.setCharFormat(f)

    @Slot()
    def toItalic(self):
        print("to itali")
        f = QTextCharFormat()
        f.setFontWeight(
            QFont.DemiBold
            if self._cursor.charFormat().fontWeight() == QFont.Bold
            else QFont.Normal
        )
        f.setFontItalic(False if self._cursor.charFormat().fontItalic() else True)
        # f.setFontFamily("Arial")
        # self._cursor.charFormat().fontWeight()  # .fontWeight() == QFont::Bold
        # print(self._cursor.sxetPosition(20))
        self._cursor.setPosition(self._document.characterCount())
        self._cursor.setCharFormat(f)

    # @Slot()
    def changed(self, depuis, removed, added):
        # print(doc.textDocument)

        print(depuis)
        print(removed)
        print(added)

    # @Slot(QTextDocument)


from package.database import db


class TextSectionClass(QObject):
    documentInit = Signal()
    sectionIdChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documentInit.connect(self.init_class)

    def init_class(self):
        self._cursor = QTextCursor(self._document)
        self._document.contentsChange.connect(self.documentContentsChange)
        with db_session:
            loaded_text = self._db_instance.text
        self._document.setHtml(loaded_text)

    @Property(QObject, notify=documentInit)
    def document(self):
        return self._document

    @document.setter
    def document_set(self, doc: QTextDocument):
        self._document = doc.children()[0]
        self.documentInit.emit()

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        with db_session:
            self._db_instance = make_proxy(db.TextSection[value])
        self.sectionIdChanged.emit()

    def documentContentsChange(self, pos, removed, added):
        f = QTextCharFormat()
        f.setFontItalic(False if self._cursor.charFormat().fontItalic() else True)
        self._cursor.select(QTextCursor.LineUnderCursor)
        self._cursor.setCharFormat(f)
        with db_session:
            self._db_instance.text = self._document.toHtml()
        # print(pos, removed, added)
        # print(self._document.toHtml())
