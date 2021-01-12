from __future__ import annotations
from typing import Tuple, List
from uuid import UUID, uuid4

from pony.orm import Database, PrimaryKey, Required, Set


def class_lexique(db: Database) -> Tuple["Lexon", "Traduction", "Locale"]:
    class Lexon(db.Entity):
        """
        Definie une "ligne" de lexique.
        Chaque Lexon à différents traduction.
        """

        id = PrimaryKey(UUID, auto=True, default=uuid4)
        traductions = Set("Traduction")

        @classmethod
        def add(cls, traductions: List[dict]):
            lexon = cls()
            for trad in traductions:
                Traduction(lexon=lexon, **trad)

            return lexon

        @classmethod
        def all(cls):
            """tous les lexons as dict"""
            return [lex.to_dict() for lex in Lexon.select()]

        def to_dict(self):
            res = {}
            res["id"] = str(self.id)
            res["traductions"] = [t.to_dict() for t in self.traductions]
            return res

    class Traduction(db.Entity):
        """
        Une Traduction d'un Lexon pour Langue Donnée
        """

        id = PrimaryKey(UUID, auto=True, default=uuid4)
        content = Required(str)
        lexon = Required(Lexon)
        locale = Required("Locale")

        def __init__(self, *, locale, **kwargs):
            locale = Locale.get(id=locale) or Locale(id=locale)
            super().__init__(locale=locale, **kwargs)

        def __repr__(self):
            return f"[{self.locale.id}] {self.content}"

        def to_dict(self):
            return {
                "id": str(self.id),
                "lexon": str(self.lexon.id),
                "content": self.content,
                "locale": self.locale.id,
            }

    class Locale(db.Entity):
        """
        Une Langue
        id: au format "en_US"
        """

        id = PrimaryKey(str)
        traductions = Set(Traduction)

        @classmethod
        def all(cls):
            return [l.id for l in cls.select().order_by(cls.id)]

    return Lexon, Traduction, Locale
