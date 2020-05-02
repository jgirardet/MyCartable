from PySide2.QtGui import QColor


class ColorMixin:
    @staticmethod
    def color_getter(value):
        return QColor.fromRgba(value)

    @staticmethod
    def color_setter(value):
        try:
            if isinstance(value, QColor):
                return value.rgba()
            elif isinstance(value, str):
                return QColor(value).rgba()
            elif isinstance(value, int):
                return value
            elif isinstance(value, tuple):
                return QColor(*value).rgba()
        except TypeError:
            return None

    def fgColor_get(self):
        return self.color_getter(self._fgColor)

    def fgColor_set(self, value):
        res = self.color_setter(value)
        if res:
            self._fgColor = self.color_setter(value)

    def bgColor_get(self):
        return self.color_getter(self._bgColor)

    def bgColor_set(self, value):
        res = self.color_setter(value)
        if res:
            self._bgColor = self.color_setter(value)
