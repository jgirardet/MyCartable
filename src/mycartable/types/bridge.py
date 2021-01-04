from __future__ import annotations

from typing import Any, Union
from uuid import UUID

from PySide2.QtCore import Signal, Property, QObject, Slot
from loguru import logger
from mycartable.types.dtb import DTB
from pony.orm import db_session


class Bridge(QObject):

    """
    Base class d'interface entre Database et Qt
    """

    entity_name = None

    """
    Pure python  section
    
    """

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        if cls.entity_name is None:
            raise NotImplementedError("Bridge sublclass must set 'entity_name'")

    def __init__(self, data: dict = {}, parent=None):
        super().__init__(parent)
        self._data: dict = data
        self._dtb = DTB()

    @classmethod
    def get_class(cls, data: Union[dict, str]) -> type(Bridge):
        """
        Retourne le type de classe à créer, peut être overrider
        :param data: entity parameters
        :return: Bridge subclass
        """
        return cls

    @classmethod
    def get(cls, item: Union[str, int, UUID, dict], parent=None) -> Bridge:
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
            return _class(data=data, parent=parent)

    @classmethod
    def new(cls, parent: QObject = None, **kwargs) -> Bridge:
        """
        Create new entry in database and return the corresponding Bridge subclass
        :param kwargs: entity parameters
        :return: instance of {cls.__name__} or None
        """
        _class = cls.get_class(kwargs)
        entity = _class.entity_name
        if data := DTB().addDB(entity, kwargs):
            return _class(parent=parent, data=data)

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

    def set_field(self, name: str, value: Any):
        if self._set_field(name, value):
            self._data[name] = value
            getattr(self, name + "Changed").emit()

    def __eq__(self, other):
        if isinstance(other, Bridge):
            return self.id == other.id
        return False

    """
    QT Properties
    """

    @Property(str, constant=True)
    def id(self) -> str:
        return self._data.get("id", "")

    """
    QT Slots
    """

    @Slot("QVariantMap")
    def set(self, data: dict):
        for name, value in data.items():
            # permet de mettre à jour aussi bien setfield/setstylefield
            setattr(self, name, value)
