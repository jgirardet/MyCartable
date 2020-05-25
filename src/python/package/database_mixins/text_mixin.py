import json
from PySide2.QtCore import Slot, Signal
import logging

from package.page.text_section import TextSectionEditor, RED, BLUE, GREEN, BLACK
from pony.orm import db_session
from PySide2.QtGui import QColor
LOG = logging.getLogger(__name__)


class TextSectionMixin:
    @Slot(int, str, int, int, int, str, result="QVariantMap")
    def updateTextSectionOnKey(
        self, sectionId, content, curseur, selectionStart, selectionEnd, event
    ):
        event = json.loads(event)
        # new_lines, new_curseur = TextSectionEditor(
        #     sectionId, content, curseur, selectionStart,
        # )()
        return TextSectionEditor(
            sectionId, content, curseur, selectionStart, selectionEnd
        ).onKey(event)

    @Slot(int, str, int, int, int, result="QVariantMap")
    def updateTextSectionOnChange(
        self, sectionId, content, curseur, selectionStart, selectionEnd
    ):
        return TextSectionEditor(
            sectionId, content, curseur, selectionStart, selectionEnd
        ).onChange()

    @Slot(int, str, int, int, int, "QVariantMap", result="QVariantMap")
    def updateTextSectionOnMenu(
        self, sectionId, content, curseur, selectionStart, selectionEnd
    ,params):
        return TextSectionEditor(
            sectionId, content, curseur, selectionStart, selectionEnd
        ).onMenu(**params)

    @Slot(int, result="QVariantMap")
    def loadTextSection(self, sectionId):
        return TextSectionEditor(sectionId).onLoad()


    @Slot(str, result="QColor")
    def getTextSectionColor(self, col):
        if col == "red":
            return QColor(RED)
        elif col == "blue":
            return QColor(BLUE)
        elif col == "green":
            return QColor(GREEN)
        elif col == "black":
            return QColor(BLACK)

        # pas terrible mais on laisse comme ça pour le moment

