from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtGui import QColor
from package.constantes import LAYOUT_SIZES, BASE_FONT
from pony.orm import db_session, ObjectNotFound

from loguru import logger

from loguru import logger


class LayoutMixin:

    # init sizes
    @Slot(str, result=float)
    def getLayoutSizes(self, nom):
        return LAYOUT_SIZES[nom]

    @Slot(str, "QVariantMap", result="QVariantMap")
    def setStyle(self, styleId, content):
        with db_session:
            try:
                item = self.db.Style[styleId]
                item.set(**content)
            except ObjectNotFound as err:
                logger.error(
                    f"Echec de la mise à jour du style : {type(err).__name__}  {err}"
                )
                return
            except TypeError as err:
                logger.error(f"Echec de la mise à jour du style : {err}")
                return
            res = item.to_dict()
            return res

    ColorChanged = Signal()

    @Property("QColor", notify=ColorChanged)
    def colorFond(self):
        return colors["fond"]

    @Property("QColor", notify=ColorChanged)
    def colorMainMenuBar(self):
        return colors["mainMenuBar"]

    @Property("QColor", notify=ColorChanged)
    def colorPageToolBar(self):
        return colors["pageToolBar"]

    fontChanged = Signal()

    @Property(str, notify=fontChanged)
    def fontMain(self):
        return fonts["main"]


colors = {
    "fond": QColor(130, 134, 138),
    "mainMenuBar": QColor(83, 93, 105),
    "pageToolBar": QColor(197, 197, 197),
}


fonts = {"main": BASE_FONT}
