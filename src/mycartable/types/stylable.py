from typing import Any

from PySide2.QtCore import Slot, Signal, Property
from PySide2.QtGui import QColor
from loguru import logger
from mycartable.types.dtb import DTB
from pony.orm import db_session


class Stylable:

    _dtb: DTB
    _data: dict

    bgColorChanged = Signal()
    fgColorChanged = Signal()
    underlineChanged = Signal()
    pointSizeChanged = Signal()
    strikeoutChanged = Signal()
    weightChanged = Signal()
    familyChanged = Signal()

    """
    Python Code
    """

    def _set_field_style(self, name: str, value: Any) -> bool:
        try:
            if value == getattr(self, name):
                return False
        except AttributeError as err:
            logger.error(err)
        if self._dtb.setDB("Style", self.styleId, {name: value}):
            return True
        return False

    def set_style(self, name: str, value: Any):
        if self._set_field_style(name, value):
            self._data["style"][name] = value
            getattr(self, name + "Changed").emit()

    """
    Qt Property
    """

    @Property(QColor, notify=bgColorChanged)
    def bgColor(self):
        return self._data["style"]["bgColor"]

    @bgColor.setter
    def bgColor_set(self, value: QColor):
        self.set_style("bgColor", value)

    @Property(str, notify=familyChanged)
    def family(self):
        return self._data["style"]["family"]

    @family.setter
    def family_set(self, value: str):
        self.set_style("family", value)

    @Property(QColor, notify=fgColorChanged)
    def fgColor(self):
        return self._data["style"]["fgColor"]

    @fgColor.setter
    def fgColor_set(self, value: QColor):
        self.set_style("fgColor", value)

    @Property(float, notify=pointSizeChanged)
    def pointSize(self):
        return self._data["style"]["pointSize"]

    @pointSize.setter
    def pointSize_set(self, value: float):
        self.set_style("pointSize", value)

    @Property(bool, notify=underlineChanged)
    def underline(self):
        return self._data["style"]["underline"]

    @underline.setter
    def underline_set(self, value: bool):
        self.set_style("underline", value)

    @Property(bool, notify=strikeoutChanged)
    def strikeout(self):
        return self._data["style"]["strikeout"]

    @strikeout.setter
    def strikeout_set(self, value: bool):
        self.set_style("strikeout", value)

    @Property(str, constant=True)
    def styleId(self):
        return self._data["style"]["styleId"]

    @Property(int, notify=weightChanged)
    def weight(self):
        return self._data["style"]["weight"]

    @weight.setter
    def weight_set(self, value: int):
        self.set_style("weight", value)

    # @Slot(str, "QVariantMap", result="QVariantMap")
    # def setStyle(self, styleId, content):
    #     with dbsession_autodisconnect:
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
