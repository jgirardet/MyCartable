from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QTextCharFormat, QColor, QBrush

CF_H1 = {
    "fontWeight": QFont.Black,
    "fontPointSize": 20,
    "fontUnderline": True,
    "underlineColor": "red",
    "underlineStyle": QTextCharFormat.SingleUnderline,
    "foreground": "blue",
    "background": "gray",
}
CF_H2 = {
    "fontWeight": QFont.Bold,
    "fontPointSize": 15,
    "fontUnderline": True,
    "underlineColor": "red",
    "underlineStyle": QTextCharFormat.SingleUnderline,
    "foreground": "red",
    "background": "white",
}
CF_H3 = {
    "fontWeight": QFont.SemiCondensed,
    "fontPointSize": 12,
    "fontUnderline": True,
    "underlineColor": "green",
    "underlineStyle": QTextCharFormat.SingleUnderline,
    "foreground": "green",
    "background": "white",
}
# "Font": ,
# "FontCapitalization": ,
# "FontFamilies": ,
# "FontFamily": ,
# "FontFixedPitch":
# "FontHintingPreference":
# "FontItalic":
# "FontKerning":
# "FontLetterSpacing":
# "FontLetterSpacingType":
# "FontOverline":
# "FontStretch":
# "FontStrikeOut":
# "FontStyleHint":
# "FontStyleName":
# "FontStyleStrategy":
# "FontWordSpacing":
# "TableCellColumnSpan":
# "TableCellRowSpan":
# "TextOutline":
# "ToolTip":
# "VerticalAlignment": ,


def buildBlockFormat(format):
    cf = QTextCharFormat()
    for k, v in format.items():
        fn_string = "set" + k[0].upper() + k[1:]
        fn = getattr(cf, fn_string)
        if k in ("foreground", "underlineColor", "background"):
            v = QColor(v)
        if k in ("foreground", "background"):
            v = QBrush(v)
        fn(v)

    return cf


H1c = buildBlockFormat(CF_H1)
H2c = buildBlockFormat(CF_H2)
H3c = buildBlockFormat(CF_H3)

CharFormats = {1: H1c, 2: H2c, 3: H3c}  # , "p": P}

#
# for x in CF_H1.keys():
#     print(getattr(H1c, x)())
