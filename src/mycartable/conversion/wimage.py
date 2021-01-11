import uuid
from PyQt5.QtCore import QByteArray, QBuffer
from PyQt5.QtGui import QImage, QColor


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
        res = f"""<text:p text:style-name="Standard">
            <draw:frame draw:style-name="fr1" draw:name="{uuid.uuid4().hex}" text:anchor-type="paragraph" svg:width="{int(width)}mm"  svg:height="{int(height)}mm" draw:z-index="0">
                <draw:image loext:mime-type="image/png">
                    <office:binary-data>{self.to_base64().decode()}</office:binary-data>
                </draw:image>
            </draw:frame>
        </text:p>"""
        return res

    def change_color(self, after: QColor):
        for x in range(self.width()):
            for y in range(self.height()):
                if self.pixelColor(x, y).alpha():
                    self.setPixelColor(x, y, after)
