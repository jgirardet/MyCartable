from __future__ import annotations

from typing import Any, Union, Callable
from uuid import UUID

from PyQt5.QtCore import pyqtProperty, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QUndoStack
from loguru import logger
from mycartable.undoredo import UndoStack

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
        self._undostack = undoStack if undoStack is not None else UndoStack(parent=self)

    def backup(self) -> dict:
        return self._dtb.execDB(self.entity_name, self.id, "backup")

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
        res = self._dtb.delDB(self.entity_name, self.id)
        self.deleteLater()
        return res

    @classmethod
    def restore(cls, *, parent: QObject, params: dict, **kwargs) -> Bridge:
        """
        REstore entry using restore method in database
        """
        _class = cls.get_class(params)
        entity = _class.entity_name
        res = DTB().execDB(entity, None, "restore", **params)
        return cls.get(res.id, parent=parent, **kwargs)

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

    def set_field(self, name: str, value: Any):
        if self._set_field(name, value):
            self._data[name] = value
            getattr(self, name + "Changed").emit()

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


class AbstractSetBridgeCommand(BaseCommand):
    bridge: Bridge

    def get_bridge(self) -> bridge:
        raise NotImplementedError

    def __init__(self, *, bridge, toset={}, get_bridge: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.toset = toset
        self.backup = {k: getattr(bridge, k) for k in toset}
        if get_bridge is not None:
            self.get_bridge = get_bridge

    def redo(self):
        bridge = self.get_bridge()
        for name, value in self.toset.items():
            # permet de mettre à jour aussi bien setfield/setstylefield
            setattr(bridge, name, value)

    def undo(self):
        bridge = self.get_bridge()
        for name, value in self.backup.items():
            # permet de mettre à jour aussi bien setfield/setstylefield
            setattr(bridge, name, value)
