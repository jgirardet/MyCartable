import shutil
import tempfile
from pathlib import Path

import pytest
from package.database.base_db import init_models, Schema
from package.database.migrations import migrations_history, check_1_3_0
from package.database.models import schema_version
from package.migrate import MakeMigrations
from pony.orm import Database

from factory import Faker


class GenerateDatabase:
    def __init__(self, version: str, dest_path: Path):

        self.version = version
        self.dest_path = dest_path
        self.sqlite = self.dest_path / (self.version + ".sqlite")
        self.sql = self.dest_path / (self.version + ".sql")
        self.db = Database()
        self.f = Faker(self.db)

        # setup temp file
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        self.tmp_path = Path(file.name)
        self.db.bind(provider="sqlite", filename=file.name)
        init_models(self.db)
        self.db.generate_mapping(create_tables=True)

    def __call__(self):
        self.build()
        self.finalize()

    @property
    def sqlite_and_sql(self):
        return self.sqlite.is_file() and self.sql.is_file()

    def build(self):
        getattr(self, "version_" + self.version.replace(".", "_"))()
        self.db.disconnect()

    def finalize(self):

        if self.sqlite_and_sql:
            self.compare_schema()
        else:
            self.store_db_and_schema()

    def compare_schema(self):
        actual_schema = self.sql.read_text()
        assert (
            Schema(self.db).schema == actual_schema
        ), f"Les schémas actuel et stocké ne correspondent plus. version: {self.version}"

    def store_db_and_schema(self):
        shutil.move(self.tmp_path, self.sqlite)
        Schema(self.sqlite).to_file(self.sql)

    """
    Sous cette marque, on définie les fonctions pour les versions
    """

    def generate_items(self):
        """genere au moins 1 élément de chaque table"""
        self.f.f_annotationDessin()  # User, Annee,  GroupeMatiere, Matiere, ACtivite, Section, Page , Annotation
        self.f.f_tableauCell()  # TableauSection, TableauCell
        self.f.f_friseLegende()  # FriseSection, ZoneFrise, FriseLegende
        self.f.f_configuration()  # configuration

    def version_1_3_0(self):
        self.generate_items()
        self.f.f_annotationDessin(points="""[{"x": 0.3, "y": 0.4}]""")


@pytest.fixture(scope="session", autouse=True)
def check_generate_database_version(resources):
    dest_path = resources / "db_version"
    gd = GenerateDatabase(schema_version, dest_path)
    if gd.sqlite_and_sql:
        gd.compare_schema()
    else:
        gd()


def test_122_to_130(resources, tmpfilename, caplogger):
    """testé à la main sur 1.2.2"""

    base = resources / "db_version" / "1.2.2.sqlite"
    shutil.copy(base, tmpfilename)
    mk = MakeMigrations(tmpfilename, "1.3.0", migrations_history)
    assert mk(check_1_3_0), caplogger.read()
    assert (
        Schema(tmpfilename).formatted
        == Schema(resources / "db_version" / "1.3.0.sqlite").formatted
    )
