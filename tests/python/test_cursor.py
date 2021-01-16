from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from mycartable.cursors import build_one_image_cursor


def test_hotspots(qapp):
    c = build_one_image_cursor("trait")
    assert c.hotSpot() == QPoint(8, 8)
    c = build_one_image_cursor("text")
    assert c.hotSpot() == QPoint(23, 8)


def test_color(qapp):
    c = build_one_image_cursor("fillrect", QColor("purple"))
    im = c.pixmap().toImage()
    assert im.pixelColor(7, 3) == QColor("purple")
