from PySide2.QtGui import QTextCharFormat, QTextBlockFormat, QBrush, QColor

BF_H1 = {
    "headingLevel": 1,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 10,
    "rightMargin": 10,
    "indent": 0,
    # "foreground": "red",
    # "background": "white",
}

BF_H2 = {
    "headingLevel": 2,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 15,
    "rightMargin": 10,
    "indent": 0,
    # "foreground": "blue",
    # "background": "white",
}

BF_H3 = {
    "headingLevel": 3,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 20,
    "rightMargin": 10,
    "indent": 0,
    # "foreground": "green",
    # "background": "white",
}
BF_P = {
    "headingLevel": 0,
    "topMargin": 10,
    "bottomMargin": 10,
    "leftMargin": 5,
    "rightMargin": 10,
    "indent": 0,
    # "foreground": "green",
    # "background": "yellow",
}


def buildBlockFormat(format):
    bf = QTextBlockFormat()
    for k, v in format.items():
        fn_string = "set" + k[0].upper() + k[1:]
        fn = getattr(bf, fn_string)

        if k in ("foreground", "background"):
            v = QBrush(QColor(v))
        fn(v)

    return bf


H1 = buildBlockFormat(BF_H1)
H2 = buildBlockFormat(BF_H2)
H3 = buildBlockFormat(BF_H3)
P = buildBlockFormat(BF_P)

BlockFormats = {1: H1, 2: H2, 3: H3, "p": P}
