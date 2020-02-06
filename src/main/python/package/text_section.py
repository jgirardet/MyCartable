from PySide2.QtCore import QObject, Signal, Property, Slot
from PySide2.QtGui import QTextDocument, QTextCharFormat, QTextCursor
from pony.orm import db_session, make_proxy
from package.database import db


class DocumentEditor(QObject):
    documentChanged = Signal()
    positionChanged = Signal(int)
    sectionIdChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proxy = None
        self._cursor = None

        # property handler
        self._document = None
        self._sectionId = 0
        self._position = 0

        self.setup_connections()

    def setup_connections(self):
        self.sectionIdChanged.connect(self._updateProxy)
        self.sectionIdChanged.connect(self._init)

    @Property(QObject, notify=documentChanged)
    def document(self):
        return self._document

    @document.setter
    def document_set(self, value: QObject):
        self._document = value.children()[0]
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

    @Property(int, notify=positionChanged)
    def position(self):
        return self._position

    @position.setter
    def position_set(self, value: int):
        self._position = value
        self.positionChanged.emit(value)

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

    @Slot()
    def _init(self):
        self._cursor = QTextCursor(self._document)
        # self._document.contentsChange.connect(self.documentContentsChange)

    @Slot(int)
    def _updateProxy(self, value):
        with db_session:

            item = db.TextSection.get(id=value)
            if item:
                self._document.setHtml(item.text)
                self._proxy = make_proxy(item)
            else:
                self._proxy = None
