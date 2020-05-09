import json
from PySide2.QtCore import Slot
import logging

from package.operations.equation import TextEquation

LOG = logging.getLogger(__name__)


class EquationMixin:
    @Slot(int, str, int, str, int, result="QVariantMap")
    def updateEquation(self, sectionId, content, curseur, event, modifiers):
        event = json.loads(event)
        new_lines, new_curseur = TextEquation(content, curseur, event)()
        return {"content": new_lines, "curseur": new_curseur}
