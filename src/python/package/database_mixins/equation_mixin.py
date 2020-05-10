import json
from PySide2.QtCore import Slot
import logging

from package.operations.equation import TextEquation
from pony.orm import db_session

LOG = logging.getLogger(__name__)


class EquationMixin:
    @Slot(int, str, int, str, result="QVariantMap")
    def updateEquation(self, sectionId, content, curseur, event):
        event = json.loads(event)
        new_lines, new_curseur = TextEquation(content, curseur, event)()
        with db_session:
            obj = self.db.Section.get(id=sectionId)
            obj.set(content=new_lines, curseur=new_curseur)
        return {"content": new_lines, "curseur": new_curseur}
