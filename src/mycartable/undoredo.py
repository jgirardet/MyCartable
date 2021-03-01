from PyQt5.QtWidgets import QUndoGroup, QUndoStack, QUndoCommand


class UndoGroup(QUndoGroup):
    """
    Base Undo Group
    """

    def __init__(self, *, parent):
        super().__init__(parent=parent)


class UndoStack(QUndoStack):
    """
    Base Undo Stack
    """

    def __init__(self, *, parent):
        super().__init__(parent=parent)
        self.setUndoLimit(50)


class BaseCommand(QUndoCommand):
    """
    Base Undo Command
    """

    undo_text = ""

    def __init__(self, *, text="", **kwargs):
        super().__init__(text or self.undo_text)
        self.params = kwargs
