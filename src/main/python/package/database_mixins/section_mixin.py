import shutil
from pathlib import Path

from PySide2.QtCore import Slot, QUrl, Signal
from package.constantes import FILES
from pony.orm import db_session
import logging
from datetime import datetime

LOG = logging.getLogger(__name__)


class SectionMixin:

    sectionAdded = Signal(int)
    sectionRemoved = Signal(int)

    @Slot(int, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            if section:
                res = section.to_dict(with_collections=True)
                # add if when other types
                # if res["classtype"] == "ImageSection":
                res["path"] = str(FILES / res["path"])
        return res

    @Slot(int, "QVariantMap", result=int)
    def addSection(self, page_id, content):
        classtype = content.pop("classtype", None)
        if not classtype:
            return 0
        elif classtype == "ImageSection":
            path = content.pop("path", None)
            if not path:
                return 0
            path = path.path() if isinstance(path, QUrl) else path
            content["path"] = FILES / str(datetime.utcnow())
            if Path(path).is_file():
                shutil.copy2(path, content["path"])
            else:
                return 0

        with db_session:
            item = getattr(self.db, classtype)(page=page_id, **content)
            print(item)
        self.sectionAdded.emit(item.position)
        return item.id

    @Slot(int, int)
    def removeSection(self, sectionId, index):
        print(sectionId, index)
        with db_session:
            item = self.db.Section.get(id=sectionId)
            if item:
                pos = item.position
                item.delete()
        # on sort de la session avant d'emit pour que toutes modif/hook pris en compte
        self.sectionRemoved.emit(index)
