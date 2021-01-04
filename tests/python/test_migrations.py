import shutil
import tempfile
from pathlib import Path
import pytest
from mycartable.database.base_db import init_models, Schema, db_session_disconnect_db
from mycartable.migrations.migrate import MakeMigrations
from mycartable.migrations.migrations import (
    make_migrations,
    migrations_history,
    CheckMigrations,
)
from mycartable.database.models import schema_version
from pony.orm import Database

from tests.factory import Faker


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
        schema = Schema(self.sqlite)
        schema.version = self.version
        schema.to_file(self.sql)

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

    def version_1_4_0(self):
        self.generate_items()


@pytest.fixture(scope="session", autouse=True)
def check_generate_database_version(resources):
    dest_path = resources / "db_version"
    gd = GenerateDatabase(schema_version, dest_path)
    if gd.sqlite_and_sql:
        gd.compare_schema()
    else:
        gd()


@pytest.mark.parametrize("version", migrations_history.keys())
def test_depuis_version(resources, tmpfilename, caplogger, version):

    base = resources / "db_version" / f"{version}.sqlite"
    shutil.copy(base, tmpfilename)
    assert make_migrations(tmpfilename), caplogger.read()
    assert (
        Schema(tmpfilename).framgments
        == Schema(resources / "db_version" / f"{schema_version}.sqlite").framgments
    )

    # test tdes données ok
    ddb = Database(provider="sqlite", filename=str(tmpfilename))
    with db_session_disconnect_db(ddb):
        assert ddb.execute("select id from Page").fetchall()


def test_1_3_0_vers_1_4_0(new_res, resources, caplogger):
    # setup
    base = new_res(resources / "db_version" / f"1.3.0.sqlite")
    mk = MakeMigrations(base, "1.4.0", migrations_history)
    ddb = Database(provider="sqlite", filename=str(base))
    print(base, "base")
    # test tdes données ok
    with db_session_disconnect_db(ddb):
        nom, prenom = ddb.get('select nom,prenom from Utilisateur where nom=="lenom"')

    assert mk(CheckMigrations(), lambda x: True), caplogger.read()

    # test: pas de perte de donnée pour Annee
    with db_session_disconnect_db(ddb):
        assert ddb.execute("select * from annee").fetchall() == [
            (2018, "cm2018"),
            (2019, "cm2019"),
        ]
    # test transfert nom, prenom, user_set de Utilisateur vers Configuration
    with db_session_disconnect_db(ddb):
        assert ddb.execute("select * from Configuration").fetchall() == [
            (
                "vue",
                "str_value",
                "intéresser",
                None,
                None,
                None,
                None,
                None,
                None,
                "{}",
            ),
            ("nom", "str_value", nom, None, None, None, None, None, None, 0),
            ("prenom", "str_value", prenom, None, None, None, None, None, None, 0),
            ("user_set", "bool_value", "", None, 1, None, None, None, None, 0),
        ]
