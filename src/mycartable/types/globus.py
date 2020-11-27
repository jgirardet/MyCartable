from typing import Any

from PySide2.QtCore import QObject, Property, Signal, Slot
from mycartable.types.dtb import DTB
from pony.orm import db_session


class Globus(DTB):
    """
    Cette classe est responsable de la gestion globale de l'application.
    Les éléments ne sont pas spécifique, d'un catégorie.
    Devrait être un singleton
    """

    anneeChanged = Signal()

    @Property(int, notify=anneeChanged)
    def annee(self):
        return self.getConfig("annee") or 0

    @annee.setter
    def annee_set(self, value: int):
        self.setConfig("annee", value)
        self.anneeChanged.emit()
