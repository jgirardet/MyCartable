from PySide2.QtCore import Slot, Property, Signal
from loguru import logger
from pony.orm import db_session


class SessionMixin:
    changeAnnee = Signal(int)
    anneeActiveChanged = Signal()

    def __init__(self):
        self.current_user = {}
        self.annee_active = None

    @db_session
    def initialize_session(self):
        if user := self.init_user():
            self.current_user = user
            return user["last_used"]
        else:
            return 0

    @Property(int, notify=anneeActiveChanged)
    def anneeActive(self):
        return self.annee_active

    @anneeActive.setter
    def anneeActive_set(self, value):
        self.annee_active = value
        with db_session:
            if user := self.db.Utilisateur.user():
                user.last_used = value
                logger.info(f"Nouvelle année sélectionnée : {value}")
                self.anneeActiveChanged.emit()

    def init_user(self) -> dict:
        if user := self.db.Utilisateur.user():
            logger.info(f"Utilisateur {user.prenom} {user.nom} activé")
            return user.to_dict()
        else:
            logger.warning("Aucun utilisateur configuré")
            return {}

    currentUserChanged = Signal()

    @Property("QVariantMap", notify=currentUserChanged)
    def currentUser(self):
        return self.current_user

    @currentUser.setter
    def currentUser_set(self, value: dict):
        self.current_user = value
        logger.info(f"Utilisateur en cours {value['prenom']} {value['nom']} ")
        self.currentUserChanged.emit()

    @Slot(str, str)
    def newUser(self, nom, prenom):
        with db_session:
            assert not self.db.Utilisateur.select().count()
            user = self.db.Utilisateur(nom=nom, prenom=prenom)
            self.currentUser = user.to_dict()

    @Slot(int, str)
    def newAnnee(self, annee, classe):
        with db_session:
            user = self.db.Annee(id=annee, niveau=classe, user=self.current_user["id"])

    @Slot(result="QVariantList")
    def getMenuAnnees(self):
        with db_session:
            res = [
                x.to_dict() for x in self.db.Annee.select().order_by(self.db.Annee.id)
            ]
            return res

    # def init_annee(self, user: dict) -> dict:
    #     if an := user["last_used"]:
    #         return an
    #     else:
