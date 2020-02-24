from PySide2.QtCore import Slot, QObject, QAbstractTableModel
from package.operations.models import AdditionModel


class OperationsMixin:
    @Slot(int, result="QVariantList")
    def getOperation(self, sectionId):
        # return AdditionModel([["", ""], ["", "1"], ["+", "2"], ["", ""]])
        return [["", ""], ["", "1"], ["+", "2"], ["", ""]]
