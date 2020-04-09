from datetime import datetime
from pathlib import Path

from PySide2.QtCore import Property, Signal, Slot, QSettings
from package.constantes import ORGNAME, FILES
from pony.orm import db_session


class SettingsMixin:

    changeAnnee = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.annee_active = None
        self.settings = QSettings()

    def setup_settings(self, annee=None):
        self.annee_active = annee or self.get_annee_active()
        self.files = FILES

    anneeActiveChanged = Signal()

    @Property(int, notify=anneeActiveChanged)
    def anneeActive(self):
        return self.annee_active

    def get_annee_active(self):
        annee = self.settings.value("General/annee_active")
        if annee:
            return int(annee)
        else:
            new = self._determine_annee()
            self.settings.setValue("General/annee_active", new)
            return new

    @Slot(result="QVariantList")
    def getMenuAnnees(self):
        with db_session:
            return [
                x.to_dict() for x in self.db.Annee.select().order_by(self.db.Annee.id)
            ]

    @staticmethod
    def _determine_annee(day=None):
        today = day or datetime.today()
        if (
            datetime(year=today.year, month=1, day=1)
            <= today
            < datetime(year=today.year, month=8, day=15)
        ):
            return today.year - 1
        else:
            return today.year
