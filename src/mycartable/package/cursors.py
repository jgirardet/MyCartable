from typing import Dict, Optional, Union

from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QPixmap, QColor, QPainter, QCursor
from mycartable.conversion import WImage

TOOL_ICON = {
    "trait": "trait",
    "text": "abcd",
    "rect": "rect",
    "fillrect": "fillrect",
    "ellipse": "ellipse",
    "arrow": "arrow-right",
    "point": "newTextSection",
    "floodfill": "floodfill",
}


def build_one_image_cursor(toolname: str, color: Optional[QColor] = None) -> QCursor:
    hot_x = 8
    hot_y = 8
    target_x = 0
    target_y = 0
    tool_x = 15
    tool_y = 15

    if toolname == "text":
        hot_x = 8 + 15
        hot_y = 8
        target_x = 15
        target_y = 0
        tool_x = 0
        tool_y = 15

    tool = QPixmap(":/icons/" + TOOL_ICON[toolname])
    target = QPixmap(":/icons/target")
    if color:
        target = WImage(target.toImage())
        target.change_color(color)
        target = QPixmap(target)
    res = QPixmap(30, 30)
    res.fill(QColor("transparent"))
    p = QPainter(res)

    p.drawPixmap(QPoint(target_x, target_y), target.scaledToWidth(15))
    p.drawPixmap(QPoint(tool_x, tool_y), tool.scaledToWidth(15))

    p.end()
    # res.save("/tmp/cursor_" + toolname + ".png")
    return QCursor(res, hot_x, hot_y)


def build_all_image_cursor() -> Dict[str, QCursor]:
    return {toolname: build_one_image_cursor(toolname) for toolname in TOOL_ICON}


#
# if __name__ == "__main__":
#     from PySide2.QtGui import QGuiApplication
#     from package import qrc
#
#     g = QGuiApplication([])
#     c = build_one_image_cursor("trait")
