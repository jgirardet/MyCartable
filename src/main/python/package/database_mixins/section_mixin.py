from pathlib import Path

from PySide2.QtCore import Slot, QUrl, Signal
from package.constantes import FILES
from package.exceptions import MyCartableOperationError
from pony.orm import db_session
import logging

LOG = logging.getLogger(__name__)


class SectionMixin:

    sectionAdded = Signal(int)
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
            if isinstance(path, QUrl):
                print(path, "Qurl simple")
                print(path.toLocalFile(), "to local file")
                print(Path(path.toLocalFile()), "Path to local file")
            path = (
                Path(path.toLocalFile())
                if isinstance(path, QUrl)
                else Path(path).absolute()
            )
            print(path)
            print(str(path))
            print(path.resolve())
            if path.is_file():
                content["path"] = str(self.get_new_image_path(path.suffix))
                new_file = self.files / content["path"]
                new_file.parent.mkdir(parents=True, exist_ok=True)
                new_file.write_bytes(path.read_bytes())
            else:
                return 0

        with db_session:
            try:
                item = getattr(self.db, classtype)(page=page_id, **content)
            except MyCartableOperationError as err:
                LOG.error(err)
                self.ui.sendToast.emit(str(err))
                return 0
        self.sectionAdded.emit(item.position)
        return item.id

    @Slot(int, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            if section:
                res = section.to_dict(with_collections=True)
                if res["classtype"] == "ImageSection":
                    res["path"] = str(FILES / res["path"])
                    LOG.debug("loading Section: %s", res)

        return res

    @Slot(int, int)
    def removeSection(self, sectionId, index):
        with db_session:
            item = self.db.Section.get(id=sectionId)
            if item:
                item.delete()
        # on sort de la session avant d'emit pour que toutes modif/hook pris en compte
        self.sectionRemoved.emit(index)
