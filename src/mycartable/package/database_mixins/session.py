from PySide2.QtCore import Slot, Property, Signal
from loguru import logger
from package.database.utilisateur import Utilisateur
from pony.orm import db_session


class SessionMixin:
    def __init__(self):
        self.current_user = {}

    @db_session
    def initialize_session(self):
        if user := self.init_user():
            self.current_user = user
            return user["last_used"]
        else:
            return 0

    def init_user(self) -> dict:
        if user := Utilisateur.user():
            logger.info(f"Utilisateur {user.prenom} {user.nom} activé")
            return user.to_dict()
        else:
            logger.warning("Aucun utilisateur configuré")
            return {}

    currentUserChanged = Signal()

    @Property("QVariantMap", notify=currentUserChanged)
    def currentUser(self):
        return self.current_user

    # @currentUser.setter
    # def currentUser_set(self, value: int):
    #     self.current_user = value
    #     self.currentUserChanged.emit()

    # def init_annee(self, user: dict) -> dict:
    #     if an := user["last_used"]:
    #         return an
    #     else:
