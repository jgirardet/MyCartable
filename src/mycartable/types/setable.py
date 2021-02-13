"""
add command setable capabilities
"""
from PyQt5.QtCore import pyqtSlot
from mycartable.undoredo import BaseCommand


class Setable:

    set_command: BaseCommand

    @pyqtSlot(int, "QVariantMap")
    @pyqtSlot(int, "QVariantMap", str)
    def set(self, toset: dict, undo_text="", **kwargs):
        self.undoStack.push(
            self.set_command(bridge=self, toset=toset, text=undo_text, **kwargs)
        )
