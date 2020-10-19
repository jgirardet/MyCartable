import tempfile
from pathlib import Path

from PySide2.QtCore import Slot, QUrl, Signal, QThreadPool
from package.convert import split_pdf_to_png
from package.files_path import FILES
from package.exceptions import MyCartableOperationError
from package.utils import qrunnable
from pony.orm import db_session
from loguru import logger


class SectionMixin:

    sectionAdded = Signal(int, int)  # position nombre
    sectionRemoved = Signal(int)

    @Slot(str, "QVariantMap", result=str)
    def addSection(self, page_id, content):
        classtype = content.pop("classtype", None)
        if not classtype:
            return ""

        elif classtype == "ImageSection":
            if not "path" in content or not content["path"]:
                return ""
            path = content.pop("path")
            path = (
                Path(path.toLocalFile())
                if isinstance(path, QUrl)
                else Path(path).absolute()
            )
            if path.is_file():
                if path.suffix == ".pdf":
                    runner = qrunnable(self.addSectionPDF, page_id, path)
                    return

                content["path"] = str(self.store_new_file(path))
            else:
                return ""
        elif classtype == "ImageSectionVide":
            classtype = "ImageSection"
            new_image = self.create_empty_image(
                content.pop("width"), content.pop("height")
            )
            content["path"] = new_image

        elif classtype == "OperationSection":
            string = content["string"]
            if "+" in string:
                classtype = "AdditionSection"
            elif "-" in string:
                classtype = "SoustractionSection"
            elif "*" in string:
                classtype = "MultiplicationSection"
            elif "/" in string:
                classtype = "DivisionSection"
            else:
                return ""

        with db_session:
            try:
                item = getattr(self.db, classtype)(page=page_id, **content)
            except MyCartableOperationError as err:
                logger.exception(err)
                self.ui.sendToast.emit(str(err))
                return ""
        self.sectionAdded.emit(item.position, 1)
        return str(item.id)

    def addSectionPDF(self, page_id, path) -> str:

        first = None
        with tempfile.TemporaryDirectory() as temp_path:
            res = split_pdf_to_png(path, Path(temp_path))
            for page in res:
                content = {"classtype": "ImageSection"}
                content["path"] = self.store_new_file(page)
                with db_session:
                    item = self.db.ImageSection(page=page_id, **content)
                if not first:
                    first = item
            print(first.position, len(res))
            self.sectionAdded.emit(first.position, len(res))

    @Slot(str, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            if section:
                res = section.to_dict()
                if res["classtype"] == "ImageSection":
                    res["path"] = QUrl.fromLocalFile(str(FILES / res["path"]))
                logger.debug(f"loading Section: {res}")
            else:
                logger.error(f"La section {section_id} n'existe pas")
        return res

    @db_session
    @Slot(str, str, "QVariantMap", result="QVariantMap")
    def setDB(self, entity: str, sectionId: str, params: dict) -> dict:
        """
        Modify a row in database.
        :param entity: str. Entity Name
        :param sectionId: str. Id (pk) of item
        :param params: dict. paremeter to edit in  row.
        :return: True if ok, else False
        """
        if entity := getattr(self.db, entity):  # pragma: no branch
            if item := entity.get(id=sectionId):  # pragma: no branch
                item.set(**params)
                return item.to_dict()
        return {}

    @db_session
    @Slot(str, "QVariantMap", result="QVariantMap")
    def addDB(self, entity: str, params: dict) -> dict:
        """
        Add a row in database.
        :param entity: str. Entity Name
        :param params: dict. paremeter to create row.
        :return: dict.
        """
        if entity := getattr(self.db, entity):  # pragma: no branch
            if item := entity(**params):  # pragma: no branch
                return item.to_dict()
        return {}

    @db_session
    @Slot(str, str, result=bool)
    def delDB(self, entity: str, sectionId: str) -> bool:
        """
        Database delete call
        :param entity: str. Entity Name
        :param sectionId: str. Id (pk) of item
        :return: True if delete, False if nothing or fail
        """
        if entity := getattr(self.db, entity):  # pragma: no branch
            if item := entity.get(id=sectionId):  # pragma: no branch
                item.delete()
                return True
        return False
