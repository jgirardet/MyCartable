from __future__ import annotations
from functools import lru_cache
from typing import Tuple

from mycartable.types import SubTypeAble
from mycartable.types.bridge import Bridge


class Section(SubTypeAble, Bridge):

    entity_name = "Section"

    @staticmethod
    @lru_cache
    def available_subclass() -> Tuple[Section]:
        from . import ImageSection, TextSection

        return Section, TextSection, ImageSection
