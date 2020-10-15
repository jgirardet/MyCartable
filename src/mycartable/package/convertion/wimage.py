from PySide2.QtCore import QByteArray, QBuffer
from PySide2.QtGui import QImage


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
        print(self, other)
        print("eq", isinstance(other, QImage), self.format(), other.format())
        if isinstance(other, QImage) and self.format() != other.format():
            other = other.convertToFormat(self.format())
            print("other apres", other)
        return super().__eq__(other)
