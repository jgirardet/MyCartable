from PySide2.QtGui import QTextCharFormat, QTextBlockFormat, QBrush, QColor

BF_H1 = {
    "headingLevel": 1,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 0,
    "rightMargin": 0,
    "indent": 0,
}

BF_H2 = {
    "headingLevel": 2,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 0,
    "rightMargin": 0,
    "indent": 1,
}

BF_H3 = {
    "headingLevel": 3,
    "topMargin": 0,
    "bottomMargin": 0,
    "leftMargin": 0,
    "rightMargin": 0,
    "indent": 2,
}
BF_P = {
    "headingLevel": 0,
    "topMargin": 0,
    "bottomMargin": 0,
    "leftMargin": 0,
    "rightMargin": 0,
    "indent": 0,
}


def buildBlockFormat(format):
    bf = QTextBlockFormat()
    for k, v in format.items():
        fn_string = "set" + k[0].upper() + k[1:]
        fn = getattr(bf, fn_string)
        fn(v)

    return bf


H1 = buildBlockFormat(BF_H1)
H2 = buildBlockFormat(BF_H2)
H3 = buildBlockFormat(BF_H3)
P = buildBlockFormat(BF_P)

BlockFormats = {1: H1, 2: H2, 3: H3, "p": P}
