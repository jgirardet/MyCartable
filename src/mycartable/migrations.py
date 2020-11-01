from pathlib import Path
from typing import Union

from package.migrate import MakeMigrations
from pony.orm import Database, db_session

migrations_history = {
    "1.3.0": [
        'ALTER TABLE Annotation ADD "points" TEXT',
        'ALTER TABLE Section ADD "height" INTEGER',
        'ALTER TABLE Section ADD "titre" TEXT',
    ]
}


def make_migrations(filename: Union[str, Path]):
    from package.database.models import schema_version

    mk = MakeMigrations(filename, schema_version, migrations_history)
    return mk(check_cb=check_migrations, generate_cb=generate_new_mapping)


def generate_new_mapping(db: Database):
    from package.database.base_db import init_models

    init_models(db)


def check_migrations(db: Database):
    with db_session:
        db.execute("select points from Annotation")
        db.execute("select height from Section")
        db.execute("select titre from Section")
        db.execute("select key from Configuration")
        db.execute("select texte from ZoneFrise")
        db.execute("select style from ZoneFrise")
    return True
