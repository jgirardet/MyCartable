from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image
from PySide2.QtCore import Signal, Property, Slot, QPointF, QPoint, Qt, QUrl, QObject
from PySide2.QtGui import QColor, QCursor
from PySide2.QtQuick import QQuickItem
from mycartable.conversion.pdf import PDFSplitter

from .annotation import AnnotationModel
from mycartable.constantes import ANNOTATION_TEXT_BG_OPACITY
from mycartable.conversion import WImage
from mycartable.package.cursors import build_one_image_cursor, build_all_image_cursor
from mycartable.files_path import FILES
from mycartable.package.utils import get_new_filename, pathize
from mycartable.types.dtb import DTB
from pony.orm import db_session

from .section import Section


class ImageSection(Section):
    entity_name = "ImageSection"
    ALL_IMAGE_CURSORS = None

    annotationTextBGOpacityChanged = Signal()

    """
    Python Code
    """

    def __init__(self, data: dict = {}, parent=None):
        super().__init__(data=data, parent=parent)
        self._model = AnnotationModel(self)

    @classmethod
    def new(cls, parent=None, **kwargs) -> Optional[ImageSection]:
        if path := kwargs.get("path", None):  # cas filename
            p_path = pathize(path)
            if not p_path.is_file():
                return
            elif p_path.suffix == ".pdf":  # si pdf
                return cls._new_image_from_pdf(p_path, **kwargs)

            else:  # sinon image standard
                kwargs = cls._new_image_base(p_path, **kwargs)
        elif "height" in kwargs and "width" in kwargs:  # cas image vide
            kwargs = cls._new_image_vide(**kwargs)
        else:  # rien de prévu, on fai trien
            return
        return super().new(parent=parent, **kwargs)

    @property
    def absolute_path(self) -> Path:
        return FILES / self.path

    """
    Image utility
    """

    @staticmethod
    def create_empty_image(width: int, height: int) -> str:
        im = Image.new("RGBA", (width, height), "white")
        res_path = ImageSection.get_new_image_path(".png")
        new_file = FILES / res_path
        new_file.parent.mkdir(parents=True, exist_ok=True)
        im.save(new_file)
        return str(res_path)

    @staticmethod
    def get_new_image_path(ext):
        with db_session:
            annee = DTB().getConfig("annee")
        return Path(str(annee), get_new_filename(ext)).as_posix()

    @staticmethod
    def store_new_file(filepath, ext=None):
        if isinstance(filepath, str):
            filepath = Path(filepath).resolve()
        if isinstance(filepath, Path):  # pragma: no branch
            ext = ext or filepath.suffix
            res_path = ImageSection.get_new_image_path(ext)
            new_file = FILES / res_path
            new_file.parent.mkdir(parents=True, exist_ok=True)
            new_file.write_bytes(filepath.read_bytes())
            return res_path

    @staticmethod
    def _new_image_base(p_path: Path, **kwargs) -> dict:
        kwargs["path"] = str(ImageSection.store_new_file(p_path))
        return kwargs

    @staticmethod
    def _new_image_vide(**kwargs) -> dict:
        kwargs["classtype"] = "ImageSection"
        new_image = ImageSection.create_empty_image(
            kwargs.pop("width"), kwargs.pop("height")
        )
        kwargs["path"] = new_image
        return kwargs

    @staticmethod
    def _new_image_from_pdf(p_path: Path, **kwargs):
        kwargs.pop("path")
        new_sections = []
        splitter = PDFSplitter()
        with tempfile.TemporaryDirectory() as temp_path:
            res = splitter(p_path, Path(temp_path))
            for counter, pdf_page in enumerate(res):
                content = kwargs.copy()
                if "position" in content:
                    content["position"] += counter
                new_sec = ImageSection.new(path=pdf_page, **content)
                new_sections.append(new_sec)
        return new_sections

    """
    Qt Propoerty
    """

    @Property(float, notify=annotationTextBGOpacityChanged)
    def annotationTextBGOpacity(self):
        return ANNOTATION_TEXT_BG_OPACITY

    @Property(str, constant=True)
    def path(self):
        return self._data["path"]

    @Property(QUrl, constant=True)
    def url(self):
        return QUrl.fromLocalFile(str(self.absolute_path))

    modelChanged = Signal()

    @Property(QObject, constant=True)
    def model(self):
        return self._model

    """
    Qt Slots
    """

    @Slot(str, QColor, QPointF, result=bool)
    def floodFill(self, sectionId: str, color: QColor, point: QPointF):
        im = WImage(str(self.absolute_path))
        point = QPoint(point.x() * im.width(), point.y() * im.height())
        im.flood_fill(color, point)
        return im.save(str(self.absolute_path))

    @Slot(int, result=bool)
    def pivoterImage(self, sens):
        with db_session:
            im = Image.open(self.absolute_path)
            sens_rotate = Image.ROTATE_270 if sens else Image.ROTATE_90
            im.transpose(sens_rotate).save(self.absolute_path)
            # todo: self.imageSectionSignal.emit()
            return True

    @Slot(QQuickItem, str, QColor)
    def setImageSectionCursor(self, qk: QQuickItem, tool: str, color: QColor):
        if tool == "default":
            qk.setCursor(QCursor(Qt.ArrowCursor))
            return
        elif tool == "dragmove":
            qk.setCursor(QCursor(Qt.DragMoveCursor))
            return
        if color != "black":
            cur = build_one_image_cursor(tool, color)
        else:
            if self.ALL_IMAGE_CURSORS is None:
                type(self).ALL_IMAGE_CURSORS = build_all_image_cursor()
            cur = self.ALL_IMAGE_CURSORS[tool]
        qk.setCursor(cur)
