from __future__ import annotations
from functools import lru_cache
from typing import Tuple

from mycartable.types import SubTypeAble
from mycartable.types.bridge import Bridge

"""
Pour créer une nouvelle section :
- fichier séparé (penser à entity_name
- ajouter import dans section.__init__
- ajouter les property/slots et autres
- ajouter dans Section.available_sublasss
- ajouter dans test_section.sub_classes
- ajouter dans test_page.test_data_role
- ajouter dans test_addSection_XXX
"""


class Section(SubTypeAble, Bridge):

    entity_name = "Section"

    @staticmethod
    @lru_cache
    def available_subclass() -> Tuple[Section]:
        from . import (
            ImageSection,
            TextSection,
            EquationSection,
            OperationSection,
            AdditionSection,
            SoustractionSection,
            MultiplicationSection,
            DivisionSection,
            TableauSection,
            FriseSection,
        )

        return (
            Section,
            TextSection,
            ImageSection,
            EquationSection,
            OperationSection,
            AdditionSection,
            SoustractionSection,
            MultiplicationSection,
            DivisionSection,
            TableauSection,
            FriseSection,
        )
