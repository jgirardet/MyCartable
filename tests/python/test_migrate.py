import pytest
from package.database import init_database
from package.database.base_db import Schema
from package.migrate import get_db_version
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
