from pony.orm import Required, Set, Optional

from .root_db import db


class Utilisateur(db.Entity):
    nom = Required(str)
    prenom = Required(str)
    annees = Set("Annee")
    last_used = Optional(int, default=0)

    @classmethod
    def user(cls):
        assert cls.select().count() <= 1, "Only one user allowed"
        return cls.select().first()
