from pathlib import Path

from PIL.Image import Image
from PySide2.QtCore import Signal, Property, Slot, QPointF, QPoint, Qt, QUrl
from PySide2.QtGui import QColor, QCursor
from PySide2.QtQuick import QQuickItem
from mycartable.package.constantes import ANNOTATION_TEXT_BG_OPACITY
from mycartable.package.convertion.wimage import WImage
from mycartable.package.cursors import build_one_image_cursor
from mycartable.package.files_path import FILES
from mycartable.package.utils import get_new_filename
from pony.orm import db_session

from .section import Section


class ImageSection(Section):
    entity_name = "ImageSection"

    imageSectionSignal = Signal()
    annotationTextBGOpacityChanged = Signal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(self._data)

    """
    Python Code
    """

    def create_empty_image(self, width: int, height: int) -> str:
        im = Image.new("RGBA", (width, height), "white")
        res_path = self.get_new_image_path(".png")
        new_file = self.files / res_path
        new_file.parent.mkdir(parents=True, exist_ok=True)
        im.save(new_file)
        return str(res_path)

    @staticmethod
    def get_new_image_path(ext):
        return Path(str(self.annee_active), get_new_filename(ext)).as_posix()

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

    @classmethod
    def new(cls, **kwargs):
        path = kwargs.pop("path", None)
        if not path:
            return
        p_path = (
            Path(path.toLocalFile())
            if isinstance(path, QUrl)
            else Path(path).absolute()
        )
        if not p_path.is_file():
            return

        if p_path.suffix == ".pdf":
            # umplement PDF section ?
            # runner = qrunnable(self.addSectionPDF, page_id, p_path)
            return
        kwargs["path"] = str(ImageSection.store_new_file(p_path))

    """
    Qt Propoerty
    """

    @Property(float, notify=annotationTextBGOpacityChanged)
    def annotationTextBGOpacity(self):
        return ANNOTATION_TEXT_BG_OPACITY

    @Property(str, notify=imageSectionSignal)
    def path(self):
        print(self._data)
        return self._data["path"]

    """
    Qt Slots
    """

    @Slot(str, QColor, QPointF, result=bool)
    def floodFill(self, sectionId: str, color: QColor, point: QPointF):
        with db_session:
            item = self.db.ImageSection[sectionId]
            file = self.files / item.path
        im = WImage(str(file))
        point = QPoint(point.x() * im.width(), point.y() * im.height())
        im.flood_fill(color, point)
        return im.save(str(file))

    @Slot(str, int, result=bool)
    def pivoterImage(self, sectionId, sens):
        with db_session:
            item = self.db.ImageSection[sectionId]
            file = self.files / item.path
            im = Image.open(file)
            sens_rotate = Image.ROTATE_270 if sens else Image.ROTATE_90
            im.transpose(sens_rotate).save(file)
            self.imageSectionSignal.emit()
            return True

    @Slot(QQuickItem, str)
    @Slot(QQuickItem)
    def setImageSectionCursor(self, qk: QQuickItem, tool: str = ""):
        tool = tool or self.ui.annotationCurrentTool
        if tool == "default":
            qk.setCursor(QCursor(Qt.ArrowCursor))
            return
        elif tool == "dragmove":
            qk.setCursor(QCursor(Qt.DragMoveCursor))
            return
        color = QColor(self.ui.annotationDessinCurrentStrokeStyle)
        if color != "black":
            cur = build_one_image_cursor(tool, color)
        else:
            cur = self.ui.image_cursors[tool]
        qk.setCursor(cur)
