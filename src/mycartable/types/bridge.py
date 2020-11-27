from __future__ import annotations

from typing import Any, Union
from uuid import UUID

from PySide2.QtCore import Signal, Property, QObject
from loguru import logger
from mycartable.types.dtb import DTB


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
    def get(
        cls, item: Union[str, int, UUID, dict], class_factory: callable = None
    ) -> Bridge:
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
            _class = cls if class_factory is None else class_factory(data)
            return _class(data=data)

    @classmethod
    def new(cls, parent=None, **kwargs) -> Bridge:
        """
        Create new entry in database and return the corresponding Bridge subclass
        :param kwargs: entity parameters
        :return: instance of {cls.__name__} or None
        """
        class_factory = kwargs.pop("class_factory", None)
        entity_factory = kwargs.pop("entity_factory", None)
        entity_name = entity_factory or cls.entity_name
        if new_item := DTB().addDB(entity_name, kwargs):
            _class = cls if class_factory is None else class_factory(new_item)
            return _class(data=new_item)

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

        if res := self._dtb.setDB(self.entity_name, self.id, {name: value}):
            self._data[name] = res[name]
            return True
        return False

    def set_field(self, name: str, value: Any):
        if self._set_field(name, value):
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
