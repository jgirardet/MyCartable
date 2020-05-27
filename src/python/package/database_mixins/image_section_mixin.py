import urllib.request
from io import BytesIO
from pathlib import Path

from PySide2.QtCore import Slot, QUrl, QAbstractListModel, Property
from PySide2.QtCore import Slot, Signal
from package.constantes import ANNOTATION_TEXT_BG_OPACITY
from package.convert import run_convert_pdf
from package.files_path import filesify
from package.utils import get_new_filename
from pony.orm import db_session, select
from PIL import Image


class ImageSectionMixin:

    """
    Annotations
    """

    imageChanged = Signal()

    @Slot("QVariantMap", result="QVariantList")
    def addAnnotation(self, content):
        with db_session:
            section = int(content.pop("section"))
            item = getattr(self.db, content["classtype"])(**content, section=section)
            dico = item.to_dict()
            style = dico.pop("style")
            return [dico, style]
        # ne pas emetre imageChanged ici, sinon emet pour empty trucs

    @Slot(int)
    def deleteAnnotation(self, annotation_id):
        with db_session:
            item = self.db.Annotation[annotation_id]
            item.delete()

            # tweak du au fait que le qml aojute et supprime une annoation si création n'aboutie pas
            if isinstance(item, self.db.AnnotationText) and not item.text:
                return
            elif (
                isinstance(item, self.db.Stabylo)
                and not item.relativeWidth
                and not item.relativeHeight
            ):
                return
            self.imageChanged.emit()

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
            self.imageChanged.emit()

            return item.to_dict(exclude=["style"])

    """
        IMAGES
    """

    def get_new_image_path(self, ext):
        return Path(str(self.annee_active), get_new_filename(ext)).as_posix()

    def store_new_file(self, filepath, ext=None):
        if isinstance(filepath, str):
            filepath = Path(filepath).resolve()
        if isinstance(filepath, Path):
            ext = ext or filepath.suffix
            res_path = self.get_new_image_path(ext)
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
            self.imageChanged.emit()
            return True

    @Slot(int, result="QVariantList")
    def getDessinModel(self, sectionId):
        print(sectionId)
        with db_session:
            query = select(
                p for p in self.db.AnnotationDessin if p.section.id == sectionId
            )
            res = [p.to_dict() for p in query]
            print(res)
            return res

    annotationTextBGOpacityChanged = Signal()

    @Property(float, notify=annotationTextBGOpacityChanged)
    def annotationTextBGOpacity(self):
        return ANNOTATION_TEXT_BG_OPACITY

    # @dessinOpacity.setter
    # def dessinOpacity_set(self, value: int):
    #     self._dessinOpacity = value
    #     self.dessinOpacityChanged.emit()

    # @Slot(int, "QVariantMap")
    # def newDessin(self, sectionId, datas):
    #     # les positions relatives
    #     print("dans new dessin", datas)
    #     datas["startX"] /= datas["width"]
    #     datas["endX"] /= datas["width"]
    #     datas["startY"] /= datas["height"]
    #     datas["endY"] /= datas["height"]
    #     with db_session:
    #         dessin = self.db.AnnotationDessin(
    #             section=sectionId,
    #             startX=datas["startX"],
    #             endX=datas["endX"],
    #             startY=datas["startY"],
    #             endY=datas["endY"],
    #             tool=datas["tool"],
    #             style={
    #                 "fgColor": datas["strokeStyle"],
    #                 "bgColor": datas["fillStyle"],
    #                 "pointSize": datas["lineWidth"],
    #             },
    #         )
    #         print(dessin.to_dict())
