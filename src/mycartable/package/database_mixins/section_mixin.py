import tempfile
from pathlib import Path

from PySide2.QtCore import Slot, QUrl, Signal
from package.convert import run_convert_pdf
from package.files_path import FILES
from package.exceptions import MyCartableOperationError
from pony.orm import db_session
from loguru import logger


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
                    return self.addSectionPDF(page_id, path)
                content["path"] = str(self.store_new_file(path))
            else:
                return ""

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
            res = run_convert_pdf(path, temp_path)
            for page in res:
                content = {"classtype": "ImageSection"}
                content["path"] = self.store_new_file(page)
                with db_session:
                    item = self.db.ImageSection(page=page_id, **content)
                if not first:
                    first = item
            self.sectionAdded.emit(first.position, len(res))
            return str(first.id)

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
