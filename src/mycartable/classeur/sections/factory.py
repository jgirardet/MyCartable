from .section import Section
from mycartable.types.dtb import DTB

from .text import TextSection
from .image import ImageSection


class SectionFactory:

    SECTIONS = {"TextSection": TextSection, "ImageSection": ImageSection}

    @classmethod
    def get(cls, item_id: str) -> Section:
        f"""
        Get a new instance of Section depending classtype
        :param item_id: item to take in database
        :return: instance of  or None
        """
        if data := DTB().getDB("Section", item_id):
            return cls.SECTIONS[data["classtype"]].get(data)

    @classmethod
    def new(cls, page_id: str, classtype: str, **params: dict) -> Section:
        f"""
        Create new instance of Section depending classtype
        :param item_id: item to take in database
        :return: instance of  or None
        """
        params["page"] = page_id
        return cls.SECTIONS[classtype].new(**params)

    # @classmethod
    # def new(cls, classtype: str, ):
