import json
from PySide2.QtCore import Slot, Signal
import logging

from package.page.text_section import TextSectionParser, TextSectionEditor
from pony.orm import db_session

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

    @Slot(int, result="QVariantMap")
    def loadTextSection(
        self, sectionId,
    ):
        with db_session:
            item = self.db.Section[int(sectionId)]
            return TextSectionEditor(sectionId, item.text, 0, 0, 0).onLoad()
