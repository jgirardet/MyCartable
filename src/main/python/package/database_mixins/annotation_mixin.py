from PySide2.QtCore import Property, Signal, QObject, Slot
from pony.orm import db_session


class AnnotationMixin:
    # annotationCreated = Signal(dict)
    #
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
