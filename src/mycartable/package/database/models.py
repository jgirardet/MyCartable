from pony.orm import Database


from .structure import class_structure
from .sections import class_section
from .utilisateur import class_utilisateur
from .style import class_style

__version__ = "1.2.3"


def import_models(db: Database):
    class_style(db)
    class_structure(db)
    class_section(db)
    class_utilisateur(db)

    return db
