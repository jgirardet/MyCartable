import pytest
from package.database import ensure_database_directory, init_bind, init_database
from pony.orm import Database, db_session


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


def test_init_bind_file_and_parent_dir_does_not_exists(tmp_path):
    ddb = Database()
    file = tmp_path / "some" / "sub" / "sub" / "dir" / "some_file"
    init_bind(ddb, filename=file, create_db=True)


def test_init_database(tmpfilename):
    d = init_database(filename=tmpfilename, create_db=True)
    assert "Page" in d.entities