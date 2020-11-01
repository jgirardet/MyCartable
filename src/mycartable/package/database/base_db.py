import io
from contextlib import contextmanager
from pathlib import Path
from typing import Union, List

from loguru import logger
from package.utils import Version
from pony.orm import Database
from pony.orm import db_session as pony_db_session


def init_models(db: Database):
    from package.database.models import import_models

    return import_models(db)


def ensure_database_directory(loc):
    if not isinstance(loc, Path):
        loc = Path(loc)
    if not loc.parent.exists():
        loc.parent.mkdir(parents=True)
    return loc


def init_bind(db, provider="sqlite", filename=":memory:", create_db=False, **kwargs):
    if filename != ":memory:":
        filename = ensure_database_directory(filename)
    logger.info(f"Database file path is {filename}")
    # try:
    db.bind(provider=provider, filename=str(filename), create_db=create_db, **kwargs)
    db.generate_mapping(create_tables=True)
    # except Exception as err:
    #     logger.exception(err)


def init_database(db: Database, **kwargs):
    activedb = init_models(db)
    init_bind(activedb, **kwargs)
    return activedb


@contextmanager
def db_session(db: Database, **kwargs):
    with pony_db_session(**kwargs):
        yield db
    db.disconnect()


class Schema:
    def __init__(
        self,
        file: Union[str, Path, Database] = None,
    ):

        if not isinstance(file, Database):
            file = Database(provider="sqlite", filename=str(file))
        self.db = file
        self.db.disconnect()

    @property
    def schema(self) -> str:
        query = "select * from sqlite_master"
        query_result: List
        with db_session(self.db):
            query_result = self.db.execute(query).fetchall()
        lines = io.StringIO()

        for i in query_result:
            if i[4]:
                print(i[4], file=lines)
        lines.seek(0)
        schem = lines.read().replace(
            "\nCREATE", ";\nCREATE"
        )  # easier to test or execute
        return schem

    @property
    def framgments(self):
        return set(self.schema.replace("\n", "").replace("  ", " ").split(";"))

    @property
    def version(self) -> Version:
        with db_session(self.db):
            v_int = self.db.execute("PRAGMA user_version").fetchone()[0]
        return Version(v_int)

    @version.setter
    def version(self, version: Union[Version, int, str]):
        if isinstance(version, (int, str)):
            version = Version(version)
        with db_session(self.db):
            self.db.execute(f"PRAGMA user_version({version.to_int()})")

    def to_file(self, path: Path):
        path.write_text(self.schema)

    @property
    def formatted(self):
        """
        format le schéma pour comparaison
        """
        schema = self.schema.replace("\n", "").replace(";", ";\n").replace("  ", " ")
        return schema
