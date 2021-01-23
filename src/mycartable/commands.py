from PyQt5.QtWidgets import QUndoCommand
from mycartable.types import DTB


class BaseCommand(QUndoCommand):

    undo_text = ""

    def __init__(self, parent: QUndoCommand = None, undo_text="", **kwargs):
        super().__init__(parent=parent)
        if undo_text:
            self.undo_text = undo_text
        self.params = kwargs
        self._dtb = DTB()

    def redo(self) -> None:
        self.redo_command()
        self.setText(self.undo_text)

    def undo(self) -> None:
        self.undo_command()

    def redo_command(self):
        pass

    def undo_command(self):
        pass
