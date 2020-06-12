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

    imageChanged = Signal()

    def get_new_image_path(self, ext):
        return Path(str(self.annee_active), get_new_filename(ext)).as_posix()

    def store_new_file(self, filepath, ext=None):
        if isinstance(filepath, str):
            filepath = Path(filepath).resolve()
        if isinstance(filepath, Path):  # pragma: no branch
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

    annotationTextBGOpacityChanged = Signal()

    @Property(float, notify=annotationTextBGOpacityChanged)
    def annotationTextBGOpacity(self):
        return ANNOTATION_TEXT_BG_OPACITY
