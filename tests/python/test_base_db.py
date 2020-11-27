import pytest
from mycartable.package.database.base_db import Schema
from mycartable.package.database.models import schema_version
from mycartable.package.utils import Version
from package.database import init_bind
from pony.orm import Database


def test_init_bind_memory():
    ddb = Database()
    init_bind(ddb)


def test_init_bind_file_exists(tmpfile):
    ddb = Database()
    init_bind(ddb, filename=tmpfile)


def test_init_bind_file_exists_with_string(tmpfile):
    ddb = Database()
    init_bind(ddb, filename=str(tmpfile))


def test_init_bind_file_no_exists_no_createdb(tmpfilename):
    ddb = Database()
    with pytest.raises(OSError):
        init_bind(ddb, filename=tmpfilename)


def test_init_bind_file_not_exists_create_db(tmpfilename):
    ddb = Database()
    init_bind(ddb, filename=tmpfilename, create_db=True)


def test_init_bind_create_file_add_schema_version(tmpfilename):
    ddb = Database()
    init_bind(ddb, filename=tmpfilename, create_db=True)
    s = Schema(ddb)
    assert s.version == Version(schema_version)


def test_init_bind_file_and_parent_dir_does_not_exists(tmp_path):
    ddb = Database()
    file = tmp_path / "some" / "sub" / "sub" / "dir" / "some_file"
    init_bind(ddb, filename=file, create_db=True)
