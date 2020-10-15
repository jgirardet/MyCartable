import pytest
from package.migrate import backup_database
from pony.orm import Database, PrimaryKey, Required, Optional, db_session


def test_1_3_0():
    """testé à la main sur 1.2.2"""
