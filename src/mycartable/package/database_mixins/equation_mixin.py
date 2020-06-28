import json
from PySide2.QtCore import Slot, Signal
import logging

from package.operations.equation import TextEquation
from pony.orm import db_session

LOG = logging.getLogger(__name__)


class EquationMixin:

    equationChanged = Signal()

    @Slot(int, str, int, str, result="QVariantMap")
    def updateEquation(self, sectionId, content, curseur, event):
        event = json.loads(event)
        new_lines, new_curseur = TextEquation(content, curseur, event)()
        with db_session:
            obj = self.db.Section.get(id=sectionId)
            obj.set(content=new_lines, curseur=new_curseur)
        self.equationChanged.emit()
        return {"content": new_lines, "curseur": new_curseur}

    @Slot(str, int, result=bool)
    def isEquationFocusable(self, content, curseur):
        return TextEquation(
            content, curseur, {"key": None, "text": None, "modifiers": None}
        ).is_focusable