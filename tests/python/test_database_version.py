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
    db = s.in_memory()

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

    db = s.in_memory()

    # on verifie par rapport au schema ancien stocké
    assert (base.parent / (version + ".sql")).read_text() == s.schema == s.get_schema()


def test_get_schema_actual_schema(ddbr):
    s = Schema(file=ddbr)
    db = s.in_memory()
    generate_items(db)


@pytest.mark.parametrize(
    "version",
    [
        "0",  # no version in pragma
        "1.2.2",
    ],
)
def test_get_version(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    assert Schema(file=base).get_version() == Version(version)
