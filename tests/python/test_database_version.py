import pytest
from mycartable.database.base_db import Schema
from mycartable.migrations.migrations import migrations_history
from mycartable.utils import Version
from pony.orm import Database, db_session

migs = list(migrations_history.keys())


@pytest.mark.parametrize(
    "version",
    migs,
)
def test_get_schema(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    s = Schema(file=base)

    # on verifie par rapport au schema ancien stocké
    assert (base.parent / (version + ".sql")).read_text() == s.schema


@pytest.mark.parametrize(
    "version",
    migs,
)
def test_get_schema_version(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    s = Schema(file=base)
    s.file = base

    # on verifie par rapport au schema ancien stocké
    assert (base.parent / (version + ".sql")).read_text() == s.schema


@pytest.mark.parametrize(
    "version",
    ["0", *migs],  # no version in pragma
)
def test_version_get(resources, version):
    base = resources / "db_version" / f"{version}.sqlite"
    if version == "1.2.2":  # exception pour la premiere
        version = "0"
    assert Schema(file=base).version == Version(version)


def test_version_set():
    db = Database(provider="sqlite", filename=":memory:")
    s = Schema(file=db)
    assert s.version == Version("0")
    s.version = Version("12.34.56")
    with db_session:
        assert s.db.execute("PRAGMA user_version").fetchone()[0] == 123456
    assert s.version == Version("12.34.56")
