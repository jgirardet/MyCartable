from pathlib import Path

from PySide2.QtCore import Slot
from package.utils import get_new_filename
from pony.orm import db_session
from PIL import Image


class ImageSectionMixin:

    """
    Annotations
    """

    @Slot("QVariantMap", result="QVariantList")
    def addAnnotation(self, content):
        with db_session:
            section = int(content.pop("section"))
            item = getattr(self.db, content["classtype"])(**content, section=section)
            dico = item.to_dict()
            style = dico.pop("style")
            return [dico, style]

    @Slot(int)
    def deleteAnnotation(self, annotation_id):
        with db_session:
            self.db.Annotation[annotation_id].delete()

    @Slot(int, result="QVariantList")
    def loadAnnotations(self, section):

        with db_session:
            obj = self.db.ImageSection[section]
            res = [p.to_dict() for p in obj.annotations]
            res2 = []
            for r in res:
                style = r.pop("style")
                res2.append([r, style])
            return res2

    @Slot(int, "QVariantMap", result="QVariantMap")
    def updateAnnotation(self, annotation_id, dico):
        with db_session:
            item = self.db.Annotation[annotation_id]
            if "style" in dico:
                style = dico.pop("style")
                item.style.set(**style)
            item.set(**dico)
            return item.to_dict(exclude=["style"])

    """
        IMAGES
    """

    def get_new_image_path(self, ext):
        return Path(str(self.annee_active), get_new_filename(ext)).as_posix()

    def store_new_file(self, filepath):
        res_path = str(self.get_new_image_path(filepath.suffix))
        new_file = self.files / res_path
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_bytes(filepath.read_bytes())
        return res_path

    @Slot(int, int, result=bool)
    def pivoterImage(self, sectionId, sens):
        with db_session:
            item = self.db.ImageSection[sectionId]
            file = self.files / item.path
            im = Image.open(file)
            sens_rotate = Image.ROTATE_270 if sens else Image.ROTATE_90
            im.transpose(sens_rotate).save(file)
            return True
