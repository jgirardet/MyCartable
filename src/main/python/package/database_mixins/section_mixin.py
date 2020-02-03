from PySide2.QtCore import Slot
from package.constantes import FILES
from pony.orm import db_session


class SectionMixin:
    @Slot(int, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            print(section)
            if section:
                res = section.to_dict(with_collections=True)
                if res["classtype"] == "ImageSection":
                    res["path"] = str(FILES / res["path"])
        return res
