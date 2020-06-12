import tempfile
from pathlib import Path

from PySide2.QtCore import Slot, QUrl, Signal
from package.convert import run_convert_pdf
from package.files_path import FILES
from package.exceptions import MyCartableOperationError
from pony.orm import db_session
import logging


LOG = logging.getLogger(__name__)


class SectionMixin:

    sectionAdded = Signal(int, int)  # position nombre
    sectionRemoved = Signal(int)

    @Slot(int, "QVariantMap", result=int)
    def addSection(self, page_id, content):
        classtype = content.pop("classtype", None)
        if not classtype:
            return 0

        elif classtype == "ImageSection":
            if not "path" in content or not content["path"]:
                return 0
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
                return 0

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
                return 0

        with db_session:
            try:
                item = getattr(self.db, classtype)(page=page_id, **content)
            except MyCartableOperationError as err:
                LOG.error(err)
                self.ui.sendToast.emit(str(err))
                return 0
        self.sectionAdded.emit(item.position, 1)
        return item.id

    def addSectionPDF(self, page_id, path):

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
            return first.id

    @Slot(int, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            if section:
                res = section.to_dict()
                if res["classtype"] == "ImageSection":
                    res["path"] = QUrl.fromLocalFile(str(FILES / res["path"]))
                    # LOG.debug("loading Section: %s", res)
            else:
                LOG.error(f"La section {section_id} n'existe pas")
        return res
