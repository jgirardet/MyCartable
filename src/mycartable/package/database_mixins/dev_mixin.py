from PySide2.QtCore import Slot


class DevMixin:  # pragma: no cover
    @Slot()
    def peupler(self):
        from tests.python.factory import populate_database

        populate_database()
        self.changeAnnee.emit(2019)
