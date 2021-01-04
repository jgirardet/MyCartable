from .base_db import (
    ensure_database_directory,
    init_bind,
    init_database,
)

db = None

from .mixins import PositionMixin, ColorMixin


def getdb():
    return db
