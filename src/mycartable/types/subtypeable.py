from abc import ABC, abstractmethod
from typing import Union
from uuid import UUID

from PySide2.QtCore import Signal, Property
from mycartable.types import Bridge


class SubTypeAble:
    classtypeChanged = Signal()

    @Property(str, notify=classtypeChanged)
    def classtype(self):
        return self._data["classtype"]

    @classmethod
    def get_class(cls, data: dict) -> "SubTypeAble":
        for sub in cls.available_subclass():
            if data["classtype"] == sub.entity_name:
                return sub

    @staticmethod
    def available_subclass() -> list:
        raise NotImplementedError(
            "available_sublass must be implemented to inherit SubTypeAble"
        )

    @classmethod
    def new(cls, **kwargs) -> Bridge:
        entity_name = kwargs["classtype"] if "classtype" in kwargs else None
        return super().new(
            entity_factory=entity_name, class_factory=cls.get_class, **kwargs
        )

    @classmethod
    def get(cls, item: Union[str, int, UUID, dict]) -> Bridge:
        return super().get(item, class_factory=cls.get_class)
