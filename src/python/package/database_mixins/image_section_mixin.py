from pathlib import Path

from PySide2.QtCore import Slot
from package.convert import run_convert_pdf
from package.utils import get_new_filename
from pony.orm import db_session
import tempfile


class ImageSectionMixin:
    @Slot("QVariantMap", result=int)
    def addAnnotation(self, content):
        item_id = 0
        with db_session:
            section = int(content.pop("section"))
            item = getattr(self.db, content["classtype"])(**content, section=section)

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
            res = [p.to_dict() for p in obj.annotations]
            return res

    @Slot(int, "QVariantMap")
    def updateAnnotation(self, annotation_id, dico):
        with db_session:
            item = self.db.Annotation[annotation_id]
            res = {}
            if dico["type"] == "color":
                res["color"] = dico["value"].rgba()
                if item.classtype == "AnnotationText":
                    res["underline"] = False

            elif dico["type"] == "underline":
                res["color"] = dico["value"].rgba()
                res["underline"] = True
            else:
                res[dico["type"]] = dico["value"]

            item.set(**res)

    def get_new_image_path(self, ext):
        return Path(str(self.annee_active), get_new_filename(ext)).as_posix()

    def store_new_file(self, filepath):
        res_path = str(self.get_new_image_path(filepath.suffix))
        new_file = self.files / res_path
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_bytes(filepath.read_bytes())
        return res_path
