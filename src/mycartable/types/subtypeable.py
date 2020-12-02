from __future__ import annotations
from typing import Union

from PySide2.QtCore import Property, QObject
from mycartable.types import Bridge


class SubTypeAble:
    @Property(str, constant=True)
    def classtype(self):
        return self._data["classtype"]

    @classmethod
    def get_class(cls, data: Union[dict, str]) -> SubTypeAble:
        name = data.get("classtype", "") if isinstance(data, dict) else data
        for sub in cls.available_subclass():
            if name == sub.entity_name:
                return sub
        return cls

    @staticmethod
    def available_subclass() -> list:
        raise NotImplementedError(
            "available_sublass must be implemented to inherit SubTypeAble"
        )

    @classmethod
    def new_sub(cls, parent: QObject = None, **kwargs) -> Bridge:
        _class = cls.get_class(kwargs)
        return _class.new(parent, **kwargs)
