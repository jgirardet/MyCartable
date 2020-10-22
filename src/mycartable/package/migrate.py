"""
Ici sont expliquées les migrations chaque changement dans la ddb.
"""
from pathlib import Path
from typing import Union

from package.database.base_db import Schema
from package.utils import Version
from pony.orm import Database

"""
type:
    1 ajout d'une foreignKey : Optional <=> Optional:
        1 Si nouvelle table : ajouter la relation dans la nouvelle table via:
        new_field_de_new_class =  Optional("OldClasse", column="new_field_de_new_class")
        Du coup rien à faire de plus
        - Si 2 anciennes table: ???
        
"""


migrations_list = {"1.3.0": {"type": "1.1"}}


def get_db_version(file: Union[Database, str, Path]):
    schema = Schema(file=file)
    version = schema.version
    if version == Version(
        "0"
    ):  # absence de version on considère 1.2.2 (début migration)
        return Version("1.2.2")
    else:
        return version
