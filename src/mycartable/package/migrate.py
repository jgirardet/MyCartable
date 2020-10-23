"""
Ici sont expliquées les migrations chaque changement dans la ddb.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Union

from package.database.base_db import Schema
from package.utils import Version
from pony.orm import Database, db_session

"""
type:
    1 ajout d'une foreignKey : Optional <=> Optional:
        1 Si nouvelle table : ajouter la relation dans la nouvelle table via:
        new_field_de_new_class =  Optional("OldClasse", column="new_field_de_new_class")
        Du coup rien à faire de plus
        - Si 2 anciennes table: ???
        
"""


migrations_list = {"1.3.0": {"type": "1.1"}}


def get_db_version(file: Union[Database, str, Path]):
    schema = Schema(file=file)
    version = schema.version
    if version == Version(
        "0"
    ):  # absence de version on considère 1.2.2 (début migration)
        return Version("1.2.2")
    else:
        return version


# migrations = {"1.3.0": ["ALTER TABLE Annotation ADD points TEXT"]}


class Migrator:
    def __init__(self, db: Database, version: Version, migrations: dict):
        self.db = db
        self.version = version
        self.migrations = migrations

    def select_migrations(self):
        selected = []
        for ver, migs in self.migrations.items():
            version = Version(ver)
            if version < self.version:
                selected += migs
        return selected

    def process_one(self, line: str):
        with db_session:
            self.db.execute(line)

    def process_migrations(self, mig_list: list):
        for mig in mig_list:
            self.process_one(mig)

    def __call__(self):
        migrations = self.select_migrations()
        self.process_migrations(migrations)


#
# def apply_new_schema_version(db, version):
#     with db_session:
#         db.Configuration.add
#
#
# def apply_all_migrations(filename):
#     pass
