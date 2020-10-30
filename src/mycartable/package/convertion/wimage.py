import uuid

from PySide2.QtCore import QByteArray, QBuffer, QPoint
from PySide2.QtGui import QImage, QColor, QPainter


class WImage(QImage):
    def to_base64(self) -> bytes:
        """image in base64 encode format"""
        ba = QByteArray()
        bu = QBuffer(ba)
        bu.open(QBuffer.ReadWrite)
        self.save(bu, "PNG")
        imb_b64 = ba.toBase64().data()
        bu.close()
        return imb_b64

    def __eq__(self, other):
        if isinstance(other, QImage) and self.format() != other.format():
            other = other.convertToFormat(self.format())
        return super().__eq__(other)

    def to_odf(self):
        width = self.widthMM()
        height = self.heightMM()
        # self.save("/tmp/odtfrise.png")
        res = f"""<text:p text:style-name="Standard">
            <draw:frame draw:style-name="fr1" draw:name="{uuid.uuid4().hex}" text:anchor-type="paragraph" svg:width="{int(width)}mm"  svg:height="{int(height)}mm" draw:z-index="0">
                <draw:image loext:mime-type="image/png">
                    <office:binary-data>{self.to_base64().decode()}</office:binary-data>
                </draw:image>
            </draw:frame>
        </text:p>"""
        return res

    def flood_fill(self, color: QColor, point: QPoint):
        """flood fill algo from
        https://www.learnpyqt.com/blog/implementing-qpainter-flood-fill-pyqt5pyside/"""
        # tested in section_mixin
        x = point.x()
        y = point.y()
        w, h = self.width(), self.height()
        s = self.bits().tobytes()
        have_seen = set()
        queue = [(x, y)]

        def get_pixel(x, y):
            i = (x + (y * w)) * 4
            return s[i : i + 4]

        target_color = get_pixel(x, y)

        def get_cardinal_points(have_seen, center_pos):
            points = []
            cx, cy = center_pos
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                xx, yy = cx + x, cy + y
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in have_seen:
                    points.append((xx, yy))
                    have_seen.add((xx, yy))
            return points

        p = QPainter(self)
        p.setPen(QColor(color))
        while queue:
            x, y = queue.pop()
            if get_pixel(x, y) == target_color:
                p.drawPoint(QPoint(x, y))
                queue.extend(get_cardinal_points(have_seen, (x, y)))
