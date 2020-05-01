from pathlib import Path

from pony.orm import Database, db_session

def init_models():
    from package.database.models import db
    return db

def ensure_database_directory(loc):
    if not isinstance(loc, Path):
        loc = Path(loc)
    if not loc.parent.exists():
        loc.parent.mkdir(parents=True)
    return loc


def init_bind(db, provider="sqlite", filename=":memory:", create_db=False, **kwargs):
    if filename != ":memory:":
        filename = ensure_database_directory(filename)
    db.bind(provider=provider, filename=str(filename), create_db=create_db, **kwargs)
    db.generate_mapping(create_tables=True)


def init_database(**kwargs):
    import package.database
    package.database.db = init_models()
    # db =
    init_bind(package.database.db, **kwargs)
    return package.database.db
