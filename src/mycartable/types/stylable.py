from typing import Any

from PyQt5.QtCore import pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor
from loguru import logger
from mycartable.types.dtb import DTB


class Stylable:

    _dtb: DTB
    _data: dict

    bgColorChanged = pyqtSignal()
    fgColorChanged = pyqtSignal()
    underlineChanged = pyqtSignal()
    pointSizeChanged = pyqtSignal()
    strikeoutChanged = pyqtSignal()
    weightChanged = pyqtSignal()
    familyChanged = pyqtSignal()

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
    Qt pyqtProperty
    """

    @pyqtProperty(QColor, notify=bgColorChanged)
    def bgColor(self):
        return self._data["style"]["bgColor"]

    @bgColor.setter
    def bgColor(self, value: QColor):
        self.set_style("bgColor", value)

    @pyqtProperty(str, notify=familyChanged)
    def family(self):
        return self._data["style"]["family"]

    @family.setter
    def family(self, value: str):
        self.set_style("family", value)

    @pyqtProperty(QColor, notify=fgColorChanged)
    def fgColor(self):
        return self._data["style"]["fgColor"]

    @fgColor.setter
    def fgColor(self, value: QColor):
        self.set_style("fgColor", value)

    @pyqtProperty(float, notify=pointSizeChanged)
    def pointSize(self):
        return self._data["style"]["pointSize"] or 0.0

    @pointSize.setter
    def pointSize(self, value: float):
        self.set_style("pointSize", value)

    @pyqtProperty(bool, notify=underlineChanged)
    def underline(self):
        return self._data["style"]["underline"]

    @underline.setter
    def underline(self, value: bool):
        self.set_style("underline", value)

    @pyqtProperty(bool, notify=strikeoutChanged)
    def strikeout(self):
        return self._data["style"]["strikeout"]

    @strikeout.setter
    def strikeout(self, value: bool):
        self.set_style("strikeout", value)

    @pyqtProperty(str, constant=True)
    def styleId(self):
        return self._data["style"]["styleId"]

    @pyqtProperty(int, notify=weightChanged)
    def weight(self):
        return self._data["style"]["weight"]

    @weight.setter
    def weight(self, value: int):
        self.set_style("weight", value)

    # @pyqtSlot(str, "QVariantMap", result="QVariantMap")
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
