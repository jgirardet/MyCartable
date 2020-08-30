from uuid import UUID, uuid4

from pony.orm import Required, Set, Optional, PrimaryKey

from .root_db import db


class Utilisateur(db.Entity):
    id = PrimaryKey(UUID, auto=True, default=uuid4)

    nom = Required(str)
    prenom = Required(str)
    annees = Set("Annee")
    last_used = Optional(int, default=0)

    @classmethod
    def user(cls):
        assert cls.select().count() <= 1, "Only one user allowed"
        return cls.select().first()

    def to_dict(self, *args, **kwargs):
        dico = super().to_dict(*args, **kwargs)
        dico["id"] = str(self.id)
        return dico
