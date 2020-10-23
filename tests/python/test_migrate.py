import pytest
from package.database import init_database
from package.database.base_db import Schema
from package.migrate import get_db_version, Migrator
from package.utils import Version
from pony.orm import Database, PrimaryKey, Required, Optional, db_session


def test_122_to_130(resources):
    """testé à la main sur 1.2.2"""
    page_to_test = "ed7521a1-6f8e-41dc-a4b3-25806009a5be"
    base = resources / "db_version" / "1_2_2.sqlite"

    db = init_database(Database(), filename=base, create_db=False)
    with db_session:
        item = db.TableauCell.select().first()
        page = db.Page.select().first()
        assert item.style.zone_frise is None
        zf = db.ZoneFrise(frise=db.FriseSection(page=page, height=400), ratio=0.3)
        assert zf.style is not None


def test_get_db_version(mdb):
    assert get_db_version(mdb) == Version("1.2.2")
    s = Schema(file=mdb)
    s.version = Version("3.5.4")
    assert get_db_version(mdb) == Version("3.5.4")


class TestMigrator:
    migrations = {
        "1.3.0": ["""ALTER TABLE bla ADD "texta" TEXT"""],
        "1.3.1": [
            """ALTER TABLE bla ADD "textb" TEXT""",
            """ALTER TABLE bla ADD "textc" TEXT""",
        ],
        "1.3.4": [
            """ALTER TABLE bla ADD "textd" TEXT""",
        ],
    }

    @pytest.fixture()
    def onetable(self, mdb):
        with db_session:
            mdb.execute("""CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY);""")
            mdb.execute("""INSERT INTO "bla" VALUES("prems")""")
        return mdb

    def test_one_migration(self, onetable):
        m = Migrator(
            onetable, Version("1"), {"0.9": ["""INSERT INTO "bla" VALUES("deux")"""]}
        )
        m()
        with db_session:
            assert m.db.execute("select * from bla").fetchall() == [
                ("prems",),
                ("deux",),
            ]

    def test_many_migrations_not_all(self, onetable):
        m = Migrator(onetable, Version("1.3.2"), self.migrations)
        m()
        with db_session:
            assert (
                m.db.execute("select * from sqlite_master").fetchone()[4]
                == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT)'
            )

    def test_many_migrations_all(self, onetable):
        m = Migrator(onetable, Version("1.3.5"), self.migrations)
        m()
        with db_session:
            assert (
                m.db.execute("select * from sqlite_master").fetchone()[4]
                == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT, "textd" TEXT)'
            )

    def test_one_migration_not_null_with_default(self, onetable):
        m = Migrator(
            onetable,
            Version("1"),
            {"0.9": ["""ALTER TABLE bla ADD "textd" TEXT NOT NULL DEFAULT "a" """]},
        )
        m()
        with db_session:
            assert m.db.execute("select * from bla").fetchone() == ("prems", "a")

    def test_one_migration_not_null_with_initial_value(self, onetable):
        m = Migrator(
            onetable,
            Version("1"),
            {
                "0.9": [
                    """ALTER TABLE bla ADD "textd" TEXT NOT NULL DEFAULT "";""",
                    """UPDATE bla SET textd="b";""",
                ]
            },
        )
        m()
        with db_session:
            assert m.db.execute("select * from bla").fetchone() == ("prems", "b")
