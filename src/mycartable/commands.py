from PyQt5.QtWidgets import QUndoCommand
from mycartable.types import DTB


class BaseCommand(QUndoCommand):

    undo_text = ""

    def __init__(self, parent: QUndoCommand = None, **kwargs):
        super().__init__(parent=parent)
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
