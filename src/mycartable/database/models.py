from pony.orm import Database


from .structure import class_structure
from .sections import class_section
from .style import class_style

schema_version = "1.3.0"


def import_models(db: Database):
    class_style(db)
    class_structure(db)
    class_section(db)

    return db
