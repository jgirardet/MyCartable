from typing import Any

from PySide2.QtCore import Slot, Signal, Property
from PySide2.QtGui import QColor
from loguru import logger
from mycartable.types.dtb import DTB
from pony.orm import db_session


class Stylable:

    dtb: DTB
    _data: dict

    bgColorChanged = Signal()
    fgColorChanged = Signal()
    styleIdChanged = Signal()
    underlineChanged = Signal()
    pointSizeChanged = Signal()
    strikeoutChanged = Signal()
    weightChanged = Signal()
    familyChanged = Signal()

    """
    Python Code
    """

    def _set_field_style(self, name: str, value: Any) -> None:
        if value != getattr(self, name):
            if res := self._dtb.setDB("Style", self.styleId, {name: value}):
                self._data["style"][name] = res[name]

    """
    Qt Property
    """

    @Property(QColor, notify=bgColorChanged)
    def bgColor(self):
        return self._data["style"]["bgColor"]

    @bgColor.setter
    def bgColor_set(self, value: QColor):
        self._set_field_style("bgColor", value)
        self.bgColorChanged.emit()

    @Property(str, notify=familyChanged)
    def family(self):
        return self._data["style"]["family"]

    @family.setter
    def family_set(self, value: str):
        self._set_field_style("family", value)
        self.familyChanged.emit()

    @Property(QColor, notify=fgColorChanged)
    def fgColor(self):
        return self._data["style"]["fgColor"]

    @fgColor.setter
    def fgColor_set(self, value: QColor):
        self._set_field_style("fgColor", value)
        self.fgColorChanged.emit()

    @Property(float, notify=pointSizeChanged)
    def pointSize(self):
        return self._data["style"]["pointSize"]

    @pointSize.setter
    def pointSize_set(self, value: float):
        self._set_field_style("pointSize", value)
        self.pointSizeChanged.emit()

    @Property(bool, notify=underlineChanged)
    def underline(self):
        return self._data["style"]["underline"]

    @underline.setter
    def underline_set(self, value: bool):
        self._set_field_style("underline", value)
        self.underlineChanged.emit()

    @Property(bool, notify=strikeoutChanged)
    def strikeout(self):
        return self._data["style"]["strikeout"]

    @strikeout.setter
    def strikeout_set(self, value: bool):
        self._set_field_style("strikeout", value)
        self.strikeoutChanged.emit()

    @Property(str, notify=styleIdChanged)
    def styleId(self):
        return self._data["style"]["styleId"]

    @Property(int, notify=weightChanged)
    def weight(self):
        return self._data["style"]["weight"]

    @weight.setter
    def weight_set(self, value: int):
        self._set_field_style("weight", value)
        self.weightChanged.emit()

    # @Slot(str, "QVariantMap", result="QVariantMap")
    # def setStyle(self, styleId, content):
    #     with db_session:
    #         try:
    #             item = self.db.Style[styleId]
    #             item.set(**content)
    #         except ObjectNotFound as err:
    #             logger.error(
    #                 f"Echec de la mise à jour du style : {type(err).__name__}  {err}"
    #             )
    #             return
    #         except TypeError as err:
    #             logger.error(f"Echec de la mise à jour du style : {err}")
    #             return
    #         res = item.to_dict()
    #         return res
