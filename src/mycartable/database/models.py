from pony.orm import Database

from .structure import class_structure
from .sections import class_section
from .style import class_style
from .lexique import class_lexique

schema_version = "1.4.0"


def import_models(db: Database):
    class_style(db)
    class_structure(db)
    class_section(db)
    class_lexique(db)

    return db
