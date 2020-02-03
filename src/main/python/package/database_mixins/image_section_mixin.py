from PySide2.QtCore import Slot
from pony.orm import db_session


class ImageSectionMixin:
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
            self.db.Annotation[annotation_id].delete()

    @Slot(int, result="QVariantList")
    def loadAnnotations(self, section):
        with db_session:
            obj = self.db.ImageSection[section]
            return [p.to_dict() for p in obj.annotations]

    @Slot(int, str)
    def updateAnnotationText(self, annotation_id, value):
        with db_session:
            self.db.AnnotationText[annotation_id].text = value
