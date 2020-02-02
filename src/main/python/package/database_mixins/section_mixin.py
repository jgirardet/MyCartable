from PySide2.QtCore import Slot
from package.constantes import FILES
from pony.orm import db_session


class SectionMixin:
    @Slot("QVariantMap", result=int)
    def addAnnotation(self, content):
        item_id = 0
        if hasattr(self.db, content["classtype"]):
            with db_session:
                section = int(content.pop("section"))
                item = getattr(self.db, content["classtype"])(
                    **content, section=section
                )

            item_id = item.id

        return item_id

    @Slot(int)
    def deleteAnnotation(self, annotation_id):
        with db_session:
            self.db.AnnotationBase[annotation_id].delete()

    @Slot(int, result="QVariantList")
    def loadAnnotations(self, section):
        with db_session:
            obj = self.db.Section[section]
            return [p.to_dict() for p in obj.annotations]

    @Slot(int, result="QVariantMap")
    def loadSection(self, section_id):
        res = {}
        with db_session:
            section = self.db.Section.get(id=section_id)
            if section:
                res = section.to_dict()
                if res["contentType"] == "image":
                    res["content"] = str(FILES / res["content"])
        return res

    @Slot(int, str)
    def updateAnnotationText(self, annotation_id, value):
        with db_session:
            self.db.AnnotationText[annotation_id].text = value
