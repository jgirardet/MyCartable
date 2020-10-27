import sqlite3

import pytest
from package.database.base_db import init_models, Schema
from package.utils import Version
from pony.orm import Database, db_session

from tests.factory import Faker


def generate_items(db: Database):
    """genere au moins 1 élément de chaque table"""
    init_models(db)
    db.generate_mapping()
    f = Faker(db)
    f.f_annotationDessin()  # User, Annee,  GroupeMatiere, Matiere, ACtivite, Section, Page , Annotation
    f.f_tableauCell()  # TableauSection, TableauCell
    f.f_friseLegende()  # FriseSection, ZoneFrise, FriseLegende
    f.f_configuration()  # configuration


@pytest.mark.parametrize(
    "version",
    [
        "1.2.2",
    ],
)
def test_get_schema(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    s = Schema(file=base)

    # on verifie par rapport au schema ancien stocké
    assert (base.parent / (version + ".sql")).read_text() == s.schema


@pytest.mark.parametrize(
    "version",
    [
        "1.2.2",
    ],
)
def test_get_schema_version(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    s = Schema(file=base)
    s.file = base

    # on verifie par rapport au schema ancien stocké
    assert (base.parent / (version + ".sql")).read_text() == s.schema


def test_get_schema_actual_schema(ddbr, mdb):
    s = Schema(file=ddbr)
    schema = s.schema
    with db_session:
        for cmd in schema.split(";"):
            mdb.execute(cmd)
    generate_items(mdb)


@pytest.mark.parametrize(
    "version",
    [
        "0",  # no version in pragma
        "1.2.2",
    ],
)
def test_version_get(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    assert Schema(file=base).version == Version(version)


def test_version_set():
    db = Database(provider="sqlite", filename=":memory:")
    s = Schema(file=db)
    assert s.version == Version("0")
    s.version = Version("12.34.56")
    with db_session:
        assert s.db.execute("PRAGMA user_version").fetchone()[0] == 123456
    assert s.version == Version("12.34.56")
