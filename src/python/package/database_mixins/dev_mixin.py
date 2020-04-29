from PySide2.QtCore import Slot


class DevMixin:
    @Slot()
    def peupler(self):
        from package.database.factory import populate_database

        populate_database()
        self.changeAnnee.emit(2019)
