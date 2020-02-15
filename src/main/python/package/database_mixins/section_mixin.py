import shutil
from pathlib import Path

from PySide2.QtCore import Slot
from package.constantes import FILES
from pony.orm import db_session
import logging

LOG = logging.getLogger(__name__)


class SectionMixin:
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
            try:
                path = Path(content.pop("path", None))
            except TypeError as err:
                LOG.error("%s", err)
                return 0

            if path.is_file():
                shutil.copy2(path, FILES / path.name)
            else:
                return 0

        with db_session:
            item = getattr(self.db, classtype)(page=page_id, **content)
        return item.id
