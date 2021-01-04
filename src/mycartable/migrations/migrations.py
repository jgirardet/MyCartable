from pathlib import Path
from typing import Union

from mycartable.migrations.migrate import MakeMigrations, MigrationResultError
from pony.orm import Database, db_session, OperationalError


"""
Mode d'emploi pour ajouter des migrations:

- changer la version dans database/models
- ajouter une nouvelle list de migrations à migration_history : un instruction par ligne
- créer de_1_X_X_vers_1_X_Y dans CheckMigrations
- Ce qui ne peut être mis dans CheckMigrations doit faire l'objet d'un test séparé dans test_migrations.py
"""

migrations_history = {
    "1.2.2": [],
    "1.3.0": [
        'ALTER TABLE Annotation ADD "points" TEXT',
        'ALTER TABLE Section ADD "height" INTEGER',
        'ALTER TABLE Section ADD "titre" TEXT',
        'CREATE TABLE "Configuration" ( "key" TEXT NOT NULL PRIMARY KEY,  "field" TEXT NOT NULL,  "str_value" TEXT NOT NULL,  "int_value" INTEGER,  "bool_value" BOOLEAN,  "float_value" REAL,  "uuid_value" UUID,  "datetime_value" DATETIME,  "date_value" DATE,  "json_value" JSON NOT NULL);',
    ],
    "1.4.0": [
        # debut sauvegardes nom, prenom, user_set
        'INSERT INTO Configuration  ("key","field","str_value","json_value") VALUES ("nom", "str_value", (SELECT nom from Utilisateur),0);',
        'INSERT INTO Configuration  ("key","field","str_value","json_value") VALUES ("prenom", "str_value", (SELECT prenom from Utilisateur),0);',
        'INSERT INTO Configuration  ("key","field","str_value", "bool_value","json_value") VALUES ("user_set", "bool_value","",  true ,0);',
        # fin sauvegarde nom, prenom, user_set
        # DEBUT  drop utilisateur, remove refenrece from Annee
        "PRAGMA foreign_keys = OFF;",
        "DROP INDEX idx_annee__user;",
        'CREATE TABLE AnneeBackup ( "id" INTEGER NOT NULL PRIMARY KEY, "niveau" TEXT NOT NULL);',
        "INSERT INTO AnneeBackup SELECT id, niveau from Annee;",
        "DROP TABLE Utilisateur;",
        "DROP TABLE Annee;",
        "ALTER TABLE AnneeBackup RENAME TO Annee;",
        "PRAGMA foreign_keys = ON;",
        # FIN drop utilisateur, remove refenrece from Annee
    ],
}


def make_migrations(filename: Union[str, Path]):
    from mycartable.database.models import schema_version

    mk = MakeMigrations(filename, schema_version, migrations_history)
    return mk(check_cb=CheckMigrations(), generate_cb=generate_new_mapping)


def generate_new_mapping(db: Database):
    from mycartable.database.base_db import init_models

    init_models(db)


class CheckMigrations:

    db: Database

    def _generate_func_names(self):
        res = []
        keys = list(migrations_history.keys())
        prev = keys[0]
        for k in keys[1:]:
            res.append(f"de_{prev.replace('.','_')}_vers_{k.replace('.','_')}")
            prev = k
        return res

    def check_via_error(
        self, commands, exception_text="", exception_type=OperationalError
    ):
        if isinstance(commands, str):
            commands = [commands]
        for com in commands:
            try:
                self.db.execute(com)
            except exception_type:
                pass
            else:
                raise MigrationResultError(exception_text)

    def de_1_2_2_vers_1_3_0(self):
        try:
            self.db.execute("select points from Annotation")
            self.db.execute("select height from Section")
            self.db.execute("select titre from Section")
            self.db.execute("select key from Configuration")
            self.db.execute("select texte from ZoneFrise")
            self.db.execute("select style from ZoneFrise")
        except OperationalError as err:
            raise MigrationResultError from err

    def de_1_3_0_vers_1_4_0(self):
        self.check_via_error(
            "select * from Utilisateur", "la table Utilisateur n'a pas été effacée"
        )
        self.check_via_error(
            "select user from Annee",
            "La colonne 'user' n'a pas été supprimée dans 'Annee'",
        )

    def __call__(self, db: Database, only=[]) -> bool:
        self.db = db
        funcs = only if only else self._generate_func_names()
        for fn in funcs:
            with db_session:
                getattr(self, fn)()
        return True
