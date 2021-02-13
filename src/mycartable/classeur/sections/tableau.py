from PyQt5.QtCore import pyqtSignal, pyqtProperty, pyqtSlot
from flatten_dict import flatten, unflatten
from loguru import logger

from .section import Section, UpdateSectionCommand


class TableauSection(Section):

    entity_name = "TableauSection"

    colonnesChanged = pyqtSignal()
    lignesChanged = pyqtSignal()

    cellUpdated = pyqtSignal("QVariantMap")  # bug si int, int, QVariantMap, pourquoi ?

    def update_cell(self, y: int, x: int, content: dict, cursor: int, emit=True):
        self._dtb.setDB("TableauCell", (self.id, y, x), content)
        if emit:
            content["_cursor"] = cursor
            content["_index"] = y * self.colonnes + x
            self.cellUpdated.emit(content)

    def modify_tableau(self, *, command: str, value: int):

        if self._dtb.execDB("TableauSection", self.id, command, value):
            signe = 1 if "insert" in command else -1
            cate = "colonnes" if "column" in command else "lignes"
            signal = self.colonnesChanged if "column" in command else self.lignesChanged
            verb = "insérée" if "insert" in command else "supprimée"

            logger.debug(f"{cate[:-1]} {verb} in position {value} in {self.id}")
            self._data[cate] += signe
            signal.emit()

    def restore_cells(self, *, col: int, cells: list, cate: str):
        """
        call restore_line/column  at `col` using cells
        """
        if cate == "lignes":
            self._dtb.execDB("TableauSection", self.id, "restore_line", col, cells)
            self.lignes = self.lignes + 1
        elif cate == "colonnes":
            self._dtb.execDB("TableauSection", self.id, "restore_column", col, cells)
            self.colonnes = self.colonnes + 1

    """
    PyQtProperty
    """

    @pyqtProperty(int, notify=colonnesChanged)
    def colonnes(self):
        return self._data["colonnes"]

    @colonnes.setter
    def colonnes(self, value):
        self.set_field("colonnes", value)

    @pyqtProperty(int, notify=lignesChanged)
    def lignes(self):
        return self._data["lignes"]

    @lignes.setter
    def lignes(self, value):
        self.set_field("lignes", value)

    """
    Qt pyqtSlots
    """

    @pyqtSlot(result="QVariantList")
    def initTableauDatas(self):
        return self._dtb.execDB("TableauSection", self.id, "get_cells")

    @pyqtSlot(int, int, "QVariantMap", int, int)
    def updateCell(self, y: int, x: int, content: dict, cursor_avant: int, cursor: int):
        self.undoStack.push(
            UpdateCellTableauSectionCommand(
                y=y,
                x=x,
                content=content,
                section=self,
                cursor_avant=cursor_avant,
                cursor=cursor,
            )
        )

    @pyqtSlot(int)
    def insertRow(self, value):
        self.undoStack.push(InsertRowTableauCommand(section=self, value=value))

    @pyqtSlot()
    def appendRow(self):
        self.insertRow(self.lignes)

    @pyqtSlot(int)
    def removeRow(self, value):
        self.undoStack.push(RemoveRowTableauCommand(section=self, value=value))

    @pyqtSlot(int)
    def insertColumn(self, value):
        self.undoStack.push(InsertColumnTableauCommand(section=self, value=value))

    # def insert_column(self, value):
    #     if self._dtb.execDB("TableauSection", self.id, "insert_one_column", value):
    #         logger.debug(f"Column inserted in position {value} in {self.id}")
    #         self._data["colonnes"] += 1
    #         self.colonnesChanged.emit()

    @pyqtSlot()
    def appendColumn(self):
        self.insertColumn(self.colonnes)

    @pyqtSlot(int)
    def removeColumn(self, value):
        self.undoStack.push(RemoveColumnTableauCommand(section=self, value=value))


class UpdateCellTableauSectionCommand(UpdateSectionCommand):
    def __init__(
        self,
        *,
        section=TableauSection,
        y: int,
        x: int,
        content: dict,
        cursor_avant: int,
        cursor: int,
        emit=False,
        **kwargs,
    ):
        super().__init__(section=section, **kwargs)
        self.y = y
        self.x = x
        self.content = content
        self.backup = section.backup()
        self.emit = emit
        self.cursor_avant = cursor_avant
        self.cursor = cursor

    def redo(self) -> None:
        section: TableauSection = self.get_section()
        section.update_cell(
            self.y,
            self.x,
            dict(self.content),
            cursor=self.cursor,
            emit=self.emit,  # dict content pour garder self.content non modifié
        )
        if not self.emit:
            self.emit = True

    def undo(self) -> None:
        section: TableauSection = self.get_section()
        cell = self.get_cell()  # self.redo_command: str = "remove_one_column"

        prev = flatten(cell)
        content = flatten(self.content)
        to_update = unflatten({k: prev[k] for k in content})
        section.update_cell(self.y, self.x, to_update, self.cursor_avant)

    def get_cell(
        self,
    ):
        return self.backup["cells"][self.y * self.backup["colonnes"] + self.x]


class ModifyTableauSectionCommand(UpdateSectionCommand):
    def __init__(self, *, section=TableauSection, value: int, **kwargs):
        super().__init__(section=section, **kwargs)
        self.backup: dict = section.backup()
        self.value: int = value


class InsertRowColumnTableauCommand(ModifyTableauSectionCommand):

    redo_command: str
    undo_command: str

    def redo(self) -> None:
        section: TableauSection = self.get_section()
        section.modify_tableau(command=self.redo_command, value=self.value)

    def undo(self) -> None:
        section: TableauSection = self.get_section()
        section.modify_tableau(command=self.undo_command, value=self.value)


class InsertColumnTableauCommand(InsertRowColumnTableauCommand):

    undo_text = "Insérer un colonne"
    redo_command: str = "insert_one_column"
    undo_command: str = "remove_one_column"


class InsertRowTableauCommand(InsertRowColumnTableauCommand):

    undo_text = "Insérer une ligne"
    redo_command: str = "insert_one_line"
    undo_command: str = "remove_one_line"


class RemoveRowColumnTableauCommand(ModifyTableauSectionCommand):
    redo_command: str
    cate: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_cells = self.backup_cells()

    def redo(self) -> None:
        section: TableauSection = self.get_section()
        section.modify_tableau(command=self.redo_command, value=self.value)

    def undo(self) -> None:
        section: TableauSection = self.get_section()
        section.restore_cells(
            col=self.value, cells=list(self.backup_cells), cate=self.cate
        )

    def backup_cells(self):
        rang = "x" if self.cate == "colonnes" else "y"
        return [cel for cel in self.backup["cells"] if cel[rang] == self.value]


class RemoveColumnTableauCommand(RemoveRowColumnTableauCommand):
    undo_text = "Supprimer une colonne"
    redo_command = "remove_one_column"
    cate = "colonnes"


class RemoveRowTableauCommand(RemoveRowColumnTableauCommand):
    undo_text = "Supprimer une ligne"
    redo_command = "remove_one_line"
    cate = "lignes"
