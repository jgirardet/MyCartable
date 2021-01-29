from __future__ import annotations

from typing import Any, Union
from uuid import UUID

from PyQt5.QtCore import pyqtProperty, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QUndoStack
from loguru import logger

from .dtb import DTB

from mycartable.commands import BaseCommand


class Bridge(QObject):

    """
    Base class d'interface entre Database et Qt
    """

    entity_name = None
    undoStackChanged = pyqtSignal()

    """
    Pure python  section
    
    """

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        if cls.entity_name is None:
            raise NotImplementedError("Bridge sublclass must set 'entity_name'")

    def __init__(self, data: dict = {}, *, parent, undoStack=None, **kwargs):
        super().__init__(parent)
        self._data: dict = data
        self._dtb = DTB(parent=self)
        self._undostack = undoStack if undoStack is not None else parent.undoStack

    @classmethod
    def get_class(cls, data: Union[dict, str]) -> type(Bridge):
        """
        Retourne le type de classe à créer, peut être overrider
        :param data: entity parameters
        :return: Bridge subclass
        """
        return cls

    @classmethod
    def get(cls, item: Union[str, int, UUID, dict], parent=None, **kwargs) -> Bridge:
        f"""
        Create a new instance of {cls.__name__}
        :param item: id as string or data as dict
        :param classtype: callable to produce custom classtype
        :return: instance of {cls.__name__} or None
        """
        data = None
        if isinstance(item, (str, UUID, int)):
            data = DTB().getDB(cls.entity_name, item)
        elif isinstance(item, dict):
            data = item
        if data:
            _class = cls.get_class(data)
            return _class(data=data, parent=parent, **kwargs)

    @classmethod
    def new(cls, *, parent, **kwargs) -> Bridge:
        """
        Create new entry in database and return the corresponding Bridge subclass
        :param kwargs: entity parameters
        :return: instance of {cls.__name__} or None
        """
        _class = cls.get_class(kwargs)
        entity = _class.entity_name
        undostack = kwargs.pop("undoStack", None)
        if data := DTB().addDB(entity, kwargs):
            return _class(parent=parent, data=data, undoStack=undostack)

    def delete(self) -> bool:
        """
        Delete entry in database
        :return: instance of {cls.__name__} or None
        """
        return self._dtb.delDB(self.entity_name, self.id)

    def _set_field(self, name: str, value: Any) -> bool:
        # pas getattr avec default au cas ou on set un value à None (je sais pas si c possible)
        try:
            if value == getattr(self, name):
                return False
        except AttributeError as err:
            logger.error(err)
            return False
        if self._dtb.setDB(self.entity_name, self.id, {name: value}):
            return True
        return False

    def set_field(self, name: str, value: Any, push=True):
        if self._set_field(name, value):
            com = SetFieldBridgeCommand(bridge=self, field=name, value=value)
            if push:
                self.undoStack.push(com)
            else:
                com.redo()

    def __eq__(self, other):
        if isinstance(other, Bridge):
            return self.id == other.id
        return False

    def __hash__(self):
        # surtout utilisé pour waitSignals de pytest_qt
        return UUID(self.id).int

    """
    QT Properties
    """

    @pyqtProperty(str, constant=True)
    def id(self) -> str:
        return self._data.get("id", "")

    @pyqtProperty(QObject, notify=undoStackChanged)
    def undoStack(self) -> QUndoStack:
        return self._undostack

    @undoStack.setter
    def undoStack(self, value: QUndoStack):
        self._undostack = value

    """
    QT pyqtSlots
    """

    @pyqtSlot("QVariantMap")
    @pyqtSlot("QVariantMap", str)
    def set(self, data: dict, undo_text=""):
        self.undoStack.push(
            SetBridgeCommand(bridge=self, toset=data, undo_text=undo_text)
        )


class BridgeCommand(BaseCommand):
    def __init__(self, *, bridge: Bridge, **kwargs):
        super().__init__(**kwargs)
        self.bridge = bridge


class SetFieldBridgeCommand(BridgeCommand):
    def __init__(self, *, field: str, value: Any, **kwargs):
        super().__init__(**kwargs)
        self.field = field
        self.b_value = getattr(self.bridge, self.field)
        self.value = value

    def redo_command(self):
        if self.bridge._set_field(self.field, self.value):
            self.bridge._data[self.field] = self.value
            getattr(self.bridge, self.field + "Changed").emit()

    def undo_command(self):
        # if self.bridge._set_field(self.field, self.value):
        self.bridge._data[self.field] = self.b_value
        getattr(self.bridge, self.field + "Changed").emit()


class SetBridgeCommand(BridgeCommand):
    def __init__(self, toset={}, **kwargs):
        super().__init__(**kwargs)
        self.toset = toset
        self.b_toset = {k: getattr(self.bridge, k) for k in toset}

    def redo_command(self):
        for name, value in self.toset.items():
            # permet de mettre à jour aussi bien setfield/setstylefield
            setattr(self.bridge, name, value)

    def undo_command(self):
        for name, value in self.b_toset.items():
            # permet de mettre à jour aussi bien setfield/setstylefield
            setattr(self.bridge, name, value)
