from PySide2.QtCore import Signal, Property, QObject
from mycartable.types import SubTypeAble
from mycartable.types.bridge import Bridge


class Section(SubTypeAble, Bridge):

    entity_name = "Section"

    @staticmethod
    def available_subclass() -> list:
        from . import ImageSection, TextSection

        return Section, TextSection, ImageSection
