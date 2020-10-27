import pytest
from package.database import init_database
from package.database.base_db import Schema
from package.migrate import Migrator, MakeMigrations
from package.utils import Version
from pony.orm import Database, PrimaryKey, Required, Optional, db_session


def test_122_to_130(resources):
    """testé à la main sur 1.2.2"""
    page_to_test = "ed7521a1-6f8e-41dc-a4b3-25806009a5be"
    base = resources / "db_version" / "1.2.2.sqlite"

    db = init_database(Database(), filename=base, create_db=False)
    with db_session:
        item = db.TableauCell.select().first()
        page = db.Page.select().first()
        assert item.style.zone_frise is None
        zf = db.ZoneFrise(frise=db.FriseSection(page=page, height=400), ratio=0.3)
        assert zf.style is not None


#
# def test_get_db_version(mdb):
#     assert get_db_version(mdb) == Version("1.2.2")
#     s = Schema(file=mdb)
#     s.version = Version("3.5.4")
#     assert get_db_version(mdb) == Version("3.5.4")


def init_onetable(ddb):
    with db_session:
        ddb.execute("""CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY);""")
        ddb.execute("""INSERT INTO "bla" VALUES("prems")""")


@pytest.fixture()
def onetable(mdb):
    init_onetable(mdb)
    return mdb


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


class TestMigrator:
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
        assert m.schema.version == Version("1.0")

    def test_one_migration_same_version(self, onetable):
        m = Migrator(
            onetable,
            Version("1.5.6"),
            {"1.5.6": ["""INSERT INTO "bla" VALUES("quinze")"""]},
        )
        m()
        with db_session:
            assert m.db.execute("select * from bla").fetchall() == [
                ("prems",),
                ("quinze",),
            ]
        assert m.schema.version == Version("1.5.6")

    def test_ignore_older_migration_than_base(self, onetable):
        m = Migrator(
            onetable,
            Version("5"),
            {
                "2": ["""INSERT INTO "bla" VALUES("skipped")"""],
                "4": ["""INSERT INTO "bla" VALUES("notskipped")"""],
            },
        )
        m.schema.version = Version("3")
        m()
        with db_session:
            assert m.db.execute("select * from bla").fetchall() == [
                ("prems",),
                ("notskipped",),
            ]
        assert m.schema.version == Version("5")

    def test_many_migrations_not_all(self, onetable):
        m = Migrator(onetable, Version("1.3.2"), migrations)
        m()
        with db_session:
            assert (
                m.db.execute("select * from sqlite_master").fetchone()[4]
                == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT)'
            )
        assert m.schema.version == Version("1.3.2")

    def test_many_migrations_all(self, onetable):
        m = Migrator(onetable, Version("1.3.5"), migrations)
        m()
        with db_session:
            assert (
                m.db.execute("select * from sqlite_master").fetchone()[4]
                == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT, "textd" TEXT)'
            )

        assert m.schema.version == Version("1.3.5")

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


class TestMakeMigrations:
    @pytest.fixture()
    def mm(self, tmpfile):
        def wrap(version, migrations):
            m = MakeMigrations(tmpfile, version, migrations)
            return m

        return wrap

    @pytest.mark.freeze_time("2017-05-21T12:12:12")
    def test_init(self, mm):
        m = mm(Version("1.0.1"), {})
        assert (
            m._backup_name()
            == "mycartable_backup-from_0.0.0-to_1.0.1-2017-05-21T12_12_12"
        )

    def test_migration_check_fail(self, tmpfile, caplogger):
        ddb = Database(provider="sqlite", filename=str(tmpfile))
        init_onetable(ddb)
        s1 = Schema(ddb)
        s1.version = "0.54"

        def check_cb(check_db):
            with db_session:
                assert (
                    check_db.execute("select * from sqlite_master").fetchone()[4]
                    == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "textX" TEXT, "textb" TEXT, "textc" TEXT)'
                )

        m = MakeMigrations(tmpfile, Version("1.3.2"), migrations)
        assert not m(check_cb, lambda x: True)
        assert "AssertionError" in caplogger.read()

        # check error then no change
        ddb2 = Database(provider="sqlite", filename=str(tmpfile))
        assert Schema(ddb).schema == Schema(ddb2).schema
        assert Schema(ddb2).version == Version("0.54")

    def test_migration_check_success(self, tmpfile, caplogger):
        ddb = Database(provider="sqlite", filename=str(tmpfile))
        init_onetable(ddb)
        s1 = Schema(ddb)
        s1.version = "0.5.0"
        v1 = s1.schema

        def check_cb(check_db):
            with db_session:
                assert (
                    check_db.execute("select * from sqlite_master").fetchone()[4]
                    == 'CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT)'
                )

        m = MakeMigrations(tmpfile, Version("1.3.2"), migrations)
        assert m(check_cb, lambda x: True)
        assert "Error" not in caplogger.read()

        ddb2 = Database(provider="sqlite", filename=str(tmpfile))
        s2 = Schema(ddb2)
        assert (
            s2.schema
            == """CREATE TABLE "bla" ("key" TEXT NOT NULL PRIMARY KEY, "texta" TEXT, "textb" TEXT, "textc" TEXT)\n"""
        )
        assert s2.version == Version("1.3.2")

    def test_restore_backup(self, tmpfile):
        ddb = Database(provider="sqlite", filename=str(tmpfile))
        init_onetable(ddb)
        bck_db = tmpfile.read_bytes()
        m = MakeMigrations(tmpfile, Version("1.3.2"), {"1.3.2": "AZEZRT ERTERT"})
        assert not m(lambda x: True, lambda x: True)
        assert tmpfile.read_bytes() == bck_db

    def test_generate_mapping_success(self, tmpfile):
        ddb = Database(provider="sqlite", filename=str(tmpfile))
        Schema(ddb).version = "0.5.0"

        def check_cb(check_db):
            with db_session:
                check_db.execute("select * from NewTable").fetchall()
            return True

        def generate_cb(generate_db):
            class NewTable(generate_db.Entity):
                aaa = Required(int)

        m = MakeMigrations(tmpfile, Version("1.3.2"), {})
        res = m(check_cb, generate_cb)
        assert res

    def test_generate_mapping_fail(self, tmpfile, caplogger):
        ddb = Database(provider="sqlite", filename=str(tmpfile))
        Schema(ddb).version = "0.5.0"

        def check_cb(check_db):
            with db_session:
                check_db.execute("select * from NewTable").fetchall()
            return True

        def generate_cb(generate_db):
            raise IndexError()

        m = MakeMigrations(tmpfile, Version("1.3.2"), {})
        assert not m(check_cb, generate_cb)
        assert "IndexError" in caplogger.read()
