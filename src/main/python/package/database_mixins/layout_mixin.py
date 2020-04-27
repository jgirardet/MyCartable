from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtGui import QColor
from package.constantes import LAYOUT_SIZES
from pony.orm import db_session


class LayoutMixin:

    # init sizes
    @Slot(str, result=float)
    def getLayoutSizes(self, nom):
        return LAYOUT_SIZES[nom]

    ColorChanged = Signal()

    @Property("QColor", notify=ColorChanged)
    def colorFond(self):
        return colors["fond"]

    @Property("QColor", notify=ColorChanged)
    def colorMainMenuBar(self):
        return colors["mainMenuBar"]


colors = {"fond": QColor(130, 134, 138), "mainMenuBar": QColor(83, 93, 105)}
