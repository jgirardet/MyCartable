from __future__ import annotations

from typing import Any, Union
from uuid import UUID

from PySide2.QtCore import Signal, Property, QObject, Slot
from mycartable.types.dtb import DTB
from pony.orm import Database


class Bridge(QObject):

    """
    Base class d'interface entre Database et Qt
    """

    entity_name = None
    nullSignal = Signal()

    """
    Pure python  section
    
    """

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        if cls.entity_name is None:
            raise NotImplementedError("Bridge sublclass must set 'entity_name'")

    def __init__(self, *, data: dict):
        super().__init__()
        self._data: dict = data
        self._dtb = DTB()

    @classmethod
    def get(cls, item: Union[str, dict]) -> Bridge:
        f"""
        Create a new instance of {cls.__name__}
        :param item: id as string or data as dict
        :return: instance of {cls.__name__} or None
        """
        data = None
        if isinstance(item, (str, UUID)):
            data = DTB().getDB(cls.entity_name, item)
        elif isinstance(item, dict):
            data = item
        if data:
            return cls(data=data)

    @classmethod
    def new(cls, **kwargs) -> Bridge:
        """
        Create new entry in database and return the corresponding Bridge subclass
        :param kwargs: entity parameters
        :return: instance of {cls.__name__} or None
        """
        if new_item := DTB().addDB(cls.entity_name, kwargs):
            return cls(data=new_item)

    def delete(self) -> bool:
        """
        Delete entry in database
        :return: instance of {cls.__name__} or None
        """
        return self._dtb.delDB(self.entity_name, self.id)

    def _set_field(self, name: str, value: Any) -> None:
        if value != getattr(self, name):
            if res := self._dtb.setDB(self.entity_name, self.id, {name: value}):
                self._data[name] = res[name]

    def __eq__(self, other):
        return self._data == other._data

    """
    QT Properties
    """

    @Property(str, notify=nullSignal)
    def id(self) -> str:
        return self._data.get("id", "")

    @Property(QObject, notify=nullSignal)
    def dtb(self) -> DTB:
        return self._dtb

    @Property("QVariantMap", notify=nullSignal)
    def data(self) -> dict:
        return self._data

    """
    QT Slots
    """
