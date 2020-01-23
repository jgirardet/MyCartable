from PySide2.QtCore import Property, Signal, Slot
from package.constantes import LAYOUT_SIZES
from pony.orm import db_session


class LayoutMixin:

    # init sizes
    @Slot(str, result=float)
    def getLayoutSizes(self, nom):
        return LAYOUT_SIZES[nom]