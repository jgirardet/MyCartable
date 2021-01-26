from __future__ import annotations

import tempfile
from functools import lru_cache, partial
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtProperty,
    pyqtSlot,
    QPointF,
    Qt,
    QUrl,
    QObject,
)
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtQuick import QQuickItem
from mycartable.conversion.pdf import PDFSplitter

from .annotation import AnnotationModel
from mycartable.defaults.constantes import ANNOTATION_TEXT_BG_OPACITY
from mycartable.cursors import build_one_image_cursor, build_all_image_cursor
from mycartable.utils import get_new_filename, pathize
from mycartable.types.dtb import DTB
from pony.orm import db_session

from .section import Section, SectionBaseCommand


@lru_cache
def import_FILES():
    from mycartable.defaults.files_path import FILES

    return FILES


class ImageSection(Section):
    entity_name = "ImageSection"
    ALL_IMAGE_CURSORS = None

    annotationCurrentToolChanged = pyqtSignal()
    annotationDessinCurrentStrokeStyleChanged = pyqtSignal()
    annotationDessinCurrentToolChanged = pyqtSignal()
    annotationDessinCurrentLineWidthChanged = pyqtSignal()
    annotationTextBGOpacityChanged = pyqtSignal()
    commandDone = pyqtSignal()

    """
    Python Code
    """

    def __init__(self, data: dict = {}, parent=None, **kwargs):
        super().__init__(data=data, parent=parent, **kwargs)
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
        return import_FILES() / self.path

    """
    Image utility
    """

    @staticmethod
    def create_empty_image(width: int, height: int) -> str:
        im = Image.new("RGBA", (width, height), "white")
        res_path = ImageSection.get_new_image_path(".png")
        new_file = import_FILES() / res_path
        new_file.parent.mkdir(parents=True, exist_ok=True)
        im.save(new_file)
        return str(res_path)

    def _floodFill(self, color: QColor, point: QPointF):
        image = Image.open(self.absolute_path)
        pos = (point.x() * image.width, point.y() * image.height)
        ImageDraw.floodfill(image, xy=pos, value=color.getRgb(), thresh=50)
        image.save(self.absolute_path)

    @staticmethod
    def get_new_image_path(ext):
        with db_session:
            annee = DTB().getConfig("annee")
        return Path(str(annee), get_new_filename(ext)).as_posix()

    def _pivoterImage(self, sens):
        with db_session:
            im = Image.open(self.absolute_path)
            sens_rotate = Image.ROTATE_270 if sens else Image.ROTATE_90
            im.transpose(sens_rotate).save(self.absolute_path)

    @staticmethod
    def store_new_file(filepath, ext=None):
        if isinstance(filepath, str):
            filepath = Path(filepath).resolve()
        if isinstance(filepath, Path):  # pragma: no branch
            ext = ext or filepath.suffix
            res_path = ImageSection.get_new_image_path(ext)
            new_file = import_FILES() / res_path
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

    @pyqtProperty(str, notify=annotationCurrentToolChanged)
    def annotationCurrentTool(self):
        return self._dtb.getConfig("annotationCurrentTool")

    @annotationCurrentTool.setter
    def annotationCurrentTool(self, value: str):
        self._dtb.setConfig("annotationCurrentTool", value)
        self.annotationCurrentToolChanged.emit()

    @pyqtProperty(int, notify=annotationDessinCurrentLineWidthChanged)
    def annotationDessinCurrentLineWidth(self):
        return self._dtb.getConfig("annotationDessinCurrentLineWidth")

    @annotationDessinCurrentLineWidth.setter
    def annotationDessinCurrentLineWidth(self, value: int):
        self._dtb.setConfig("annotationDessinCurrentLineWidth", value)
        self.annotationDessinCurrentLineWidthChanged.emit()

    @pyqtProperty(QColor, notify=annotationDessinCurrentStrokeStyleChanged)
    def annotationDessinCurrentStrokeStyle(self):
        return QColor(self._dtb.getConfig("annotationDessinCurrentStrokeStyle"))

    @annotationDessinCurrentStrokeStyle.setter
    def annotationDessinCurrentStrokeStyle(self, value: str):
        self._dtb.setConfig("annotationDessinCurrentStrokeStyle", value.name())
        self.annotationDessinCurrentStrokeStyleChanged.emit()

    @pyqtProperty(str, notify=annotationDessinCurrentToolChanged)
    def annotationDessinCurrentTool(self):
        return self._dtb.getConfig("annotationDessinCurrentTool")

    @annotationDessinCurrentTool.setter
    def annotationDessinCurrentTool(self, value: str):
        self._dtb.setConfig("annotationDessinCurrentTool", value)
        self.annotationDessinCurrentToolChanged.emit()

    @pyqtProperty(float, notify=annotationTextBGOpacityChanged)
    def annotationTextBGOpacity(self):
        return ANNOTATION_TEXT_BG_OPACITY

    @pyqtProperty(str, constant=True)
    def path(self):
        return self._data["path"]

    @pyqtProperty(QUrl, constant=True)
    def url(self):
        return QUrl.fromLocalFile(str(self.absolute_path))

    @pyqtProperty(QObject, constant=True)
    def model(self):
        return self._model

    """
    Qt pyqtSlots
    """

    @pyqtSlot(QColor, QPointF)
    def floodFill(self, color: QColor, point: QPointF):
        self.undoStack.push(
            UpdateImageSectionCommand(
                section=self,
                undo_text="remplir",
                callable=self._floodFill,
                call_args=[color, point],
            )
        )

    @pyqtSlot(int)
    def pivoterImage(self, sens):
        self.undoStack.push(
            UpdateImageSectionCommand(
                section=self,
                undo_text="pivoter",
                callable=self._pivoterImage,
                call_args=[sens],
            )
        )

    @pyqtSlot(QQuickItem, str, QColor)
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


class UpdateImageSectionCommand(SectionBaseCommand):
    section: ImageSection

    def __init__(self, *, callable, call_args=[], call_kwargs={}, **kwargs):
        super().__init__(**kwargs)
        self.image_bytes = self.section.absolute_path.read_bytes()
        self.apply = partial(callable, *call_args, **call_kwargs)

    def redo_command(self):
        self.apply()
        self.section.commandDone.emit()

    def undo_command(self):
        im = Image.open(BytesIO(self.image_bytes))
        im.save(self.section.absolute_path)
        self.section.commandDone.emit()
