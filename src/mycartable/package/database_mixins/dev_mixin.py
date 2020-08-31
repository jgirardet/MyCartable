from PySide2.QtCore import Slot
from loguru import logger


class DevMixin:  # pragma: no cover
    @Slot()
    def peupler(self):
        from tests.python.factory import populate_database

        populate_database()
        self.changeAnnee.emit(2019)

    @Slot(str)
    def debug(self, texte):
        logger.debug(texte)
