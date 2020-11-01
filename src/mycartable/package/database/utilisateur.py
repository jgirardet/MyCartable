import datetime
from typing import Tuple
from uuid import UUID, uuid4

from pony.orm import (
    Required,
    Set,
    Optional,
    PrimaryKey,
    Database,
    Json,
)


def class_utilisateur(db: Database) -> Tuple["Utilisateur", "Configuration"]:
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

    class Configuration(db.Entity):
        key = PrimaryKey(str)
        field = Required(str)

        EASY_TYPES = [str, int, bool, float, datetime.datetime, datetime.date]

        str_value = Optional(str)
        int_value = Optional(int)
        bool_value = Optional(bool)
        float_value = Optional(float)
        uuid_value = Optional(UUID)
        datetime_value = Optional(datetime.datetime)
        date_value = Optional(datetime.date)
        json_value = Optional(Json)

        @classmethod
        def add(cls, key, value):
            field = cls._get_field(value)
            item = cls.get(key=key)
            if item:
                item.field = field
                setattr(item, field, value)
            else:
                Configuration(**{"key": key, "field": field, field: value})

        @classmethod
        def option(cls, key):
            if item := Configuration.get(key=key):
                return getattr(item, item.field)

        @staticmethod
        def _get_field(value: str) -> str:
            res = ""
            if type(value) in Configuration.EASY_TYPES:
                res = value.__class__.__name__
            elif isinstance(value, UUID):
                res = "uuid"
            elif isinstance(value, (list, dict)):
                res = "json"
            else:
                raise ValueError("Le type d'option est inconnu")
            return res + "_value"

    return (Utilisateur, Configuration)
