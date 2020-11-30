from PySide2.QtCore import QPoint
from PySide2.QtGui import QImage, QColor
from package.convertion.wimage import WImage
from package.cursors import build_all_image_cursor, build_one_image_cursor


def test_hotspots():
    c = build_one_image_cursor("trait")
    assert c.hotSpot() == QPoint(8, 8)
    c = build_one_image_cursor("text")
    assert c.hotSpot() == QPoint(23, 8)


def test_color():
    c = build_one_image_cursor("fillrect", QColor("purple"))
    im = c.pixmap().toImage()
    assert im.pixelColor(7, 3) == QColor("purple")
