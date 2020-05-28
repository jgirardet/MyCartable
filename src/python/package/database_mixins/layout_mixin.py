from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtGui import QColor
from package.constantes import LAYOUT_SIZES, BASE_FONT
from pony.orm import db_session, ObjectNotFound

import logging

LOG = logging.getLogger(__name__)


class LayoutMixin:

    # init sizes
    @Slot(str, result=float)
    def getLayoutSizes(self, nom):
        return LAYOUT_SIZES[nom]

    @Slot(int, "QVariantMap", result="QVariantMap")
    def setStyle(self, styleId, content):
        with db_session:
            try:
                item = self.db.Style[styleId]
                item.set(**content)
            except ObjectNotFound as err:
                LOG.error(
                    f"Echec de la mise à jour du style : {type(err).__name__}  {err}"
                )
                return
            except TypeError as err:
                LOG.error(f"Echec de la mise à jour du style : {err}")
                return
            res = item.to_dict()
            print(res)
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

    @Property(str, notify=ColorChanged)
    def fontMain(self):
        return fonts["main"]


colors = {
    "fond": QColor(130, 134, 138),
    "mainMenuBar": QColor(83, 93, 105),
    "pageToolBar": QColor(197, 197, 197),
}


fonts = {"main": BASE_FONT}
