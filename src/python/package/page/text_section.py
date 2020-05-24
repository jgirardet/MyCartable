import html
import re

from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QBrush,
    QColor,
    Qt,
    QTextBlock,
    QTextBlockFormat,
    QTextFragment,
    QTextDocumentFragment,
    QFont,
)
from PySide2.QtWidgets import QApplication
from bs4 import BeautifulSoup
from package.page.blockFormat import P, BlockFormats
from package.page.charFormat import CharFormats, Pc
from pony.orm import db_session, make_proxy
from package.database import db


_CSS_BASE = {
    "body": {
        "color": "#363636",
        "background-color": "#E6E6E6",
        "font-family": "Verdana",
        "font-size": "20pt",
        "font-weight": "96",
        "margin-top": "12px",
    },
    "h1": {
        "font-size": "30pt",
        "color": "#D40020",
        "font-weight": "600",
        "text-decoration": "underline",
        "text-transform": "uppercase",
        "margin-top": "18px",
    },
    "h2": {
        "font-size": "25pt",
        "color": "#006A4E",
        "font-weight": "600",
        "text-decoration": "underline",
        "margin-top": "16px",
    },
    "h3": {
        "font-size": "25pt",
        "color": "#0048BA",
        "font-weight": "400",
        "text-decoration": "underline",
        "margin-top": "14px",
    },
    "h4": {
        "color": "#363636",
        "font-size": "20pt",
        "font-weight": "400",
        "text-decoration": "underline",
        "margin-top": "18px",
    },
    "p": {},
}


def lowerise(source):
    target = {}
    # lowerise les cles mais pas les values
    for k, v in source.items():
        k = k.lower()
        if isinstance(v, str):
            target[k] = v
        elif isinstance(v, dict):
            target[k] = lowerise(v)
    return target


CSS_BASE = lowerise(_CSS_BASE)


def build_css_string(dico):
    return "".join([" " + k + ":" + v + ";" for k, v in dico.items()])


def build_css(source=CSS_BASE):
    target = []
    for tag, items in source.items():
        target.append(f"{tag} {{{build_css_string(items)}}}")
    return "".join(target)


CSS = build_css(CSS_BASE)


def build_bockCharFormat_from_css(css):
    res = []
    ordre = ["p", "h1", "h2", "h3", "h4"]
    for item in ordre:
        datas = css[item]
        cf = QTextCharFormat()
        cf.setForeground(
            QBrush(QColor(datas.get("color", None) or css["body"]["color"]))
        )
        cf.setBackground(
            QBrush(
                QColor(
                    datas.get("background-color", None)
                    or css["body"]["background-color"]
                )
            )
        )
        pt = datas.get("font-size", None) or css["body"]["font-size"]
        pt = float(pt.rstrip("pt"))
        cf.setFontPointSize(pt)

        if "text-decoration" in datas:
            cf.setFontUnderline(True)
        if "font-weight" in datas:
            cf.setFontWeight(
                int(datas["font-weight"]) / 8
            )  # cssweight = 8 * QFont.wieight
        if "text-transform" in datas:
            if datas["text-transform"] == "uppercase":
                cf.setFontCapitalization(QFont.AllUppercase)
            elif datas["text-transform"] == "lowercase":
                cf.setFontCapitalization(QFont.AllLowercase)

        res.append(cf)
    return res


def build_blockFormat_from_css(css):
    res = []
    ordre = ["p", "h1", "h2", "h3", "h4"]
    for item in ordre:
        cf = QTextBlockFormat()
        datas = css[item]

        if item == "p":
            cf.setHeadingLevel(0)
        else:
            cf.setHeadingLevel(int(item[1]))

        mt = datas.get("margin-top", None) or css["body"]["margin-top"]
        mt = float(mt.rstrip("px"))
        cf.setTopMargin(mt)

        res.append(cf)
    return res


BLOCK_CHAR_FORMAT = build_bockCharFormat_from_css(CSS_BASE)
BLOCK_FORMAT = build_blockFormat_from_css(CSS_BASE)


class BlockFormat_:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        if isinstance(item, str):
            if item == "p":
                level = 0
            else:
                level = int(item[1])
            return self.data[level]
        elif isinstance(item, int):
            return self.data[item]


BlockCharFormat = BlockFormat_(build_bockCharFormat_from_css(CSS_BASE))
BlockFormat = BlockFormat_(build_blockFormat_from_css(CSS_BASE))


RE_AUTOPARAGRAPH_DEBUT = re.compile(r"^(#{1,6})\s\S.+\S$")
RE_AUTOPARAGRAPH_FIN = re.compile(r"^\S+\s(#{1,6})$")


class TextSectionEditor(QTextDocument):
    def __init__(self, sectionId, content="", pos=0, selectionStart=0, selectionEnd=0):
        super().__init__()
        self.sectionId = sectionId
        self.setDefaultStyleSheet(CSS)
        self.setHtml(content)
        self.s_start = selectionStart
        self.s_end = selectionEnd

        self.cur = QTextCursor(self)
        self.cur.setPosition(pos)
        self.result = {"text": "", "cursorPosition": self.pos, "eventAccepted": False}
        self.pending = False

    @property
    def len(self):
        return self.characterCount()

    @property
    def pos(self):
        return self.cur.position()

    def onChange(self):

        self._update_ddb()
        self.setResponse(True)
        return self.result

    def onKey(self, event):
        self.key = event["key"]
        self.key_text = event["text"]
        self.modifiers = event["modifiers"]

        if self.key == Qt.Key_Return:
            self.do_return()
        else:
            self.setResponse(False)

        if self.pending:
            self._update_ddb()
        return self.result

    @db_session
    def onLoad(self):
        item = db.Section[self.sectionId]
        if item:
            self.setHtml(item.text)
            self.setResponse(True, cur=self.len)
        return self.result

    def do_return(self):
        block = self.findBlock(self.pos)
        if self.modifiers == Qt.ControlModifier:
            self._appendEmptyBlock()
        elif self.modifiers == Qt.ShiftModifier:
            self._insertEmptyBlock()
        elif block.blockFormat().headingLevel():
            self._appendEmptyBlock()
        else:
            if self._headerAutoFormat():
                return
            else:
                self.setResponse(False)

    def setResponse(self, accepted, text=None, cur=None):
        self.result["text"] = text or self.toHtml()
        self.result["cursorPosition"] = cur or self.cur.position()
        self.result["eventAccepted"] = accepted

    def _appendEmptyBlock(
        self, section="p", pre_move=QTextCursor.EndOfBlock, set_response=True
    ):
        self.cur.movePosition(pre_move)
        self.cur.insertBlock(BlockFormat[section], BlockCharFormat[section])
        self.cur.insertFragment(QTextDocumentFragment.fromPlainText(""))
        self.pending = True
        if set_response:
            self.setResponse(True)

    def _insertEmptyBlock(
        self, section="p", pre_move=QTextCursor.StartOfBlock, set_response=True
    ):
        old = self.cur.blockFormat().headingLevel()
        self._appendEmptyBlock(pre_move=pre_move, set_response=False)
        self._set_block_style(old)
        self.cur.movePosition(QTextCursor.PreviousBlock)
        self._set_block_style(section)
        self.pending = True
        if set_response:
            self.setResponse(True)

    def _headerAutoFormat(self):

        # on check les expressions régulières suivantes:
        #   #, ##, ###, ####, #####
        line = self.cur.block().text()
        matched = RE_AUTOPARAGRAPH_DEBUT.search(line)
        matched_at_start = False
        if not matched:
            matched = RE_AUTOPARAGRAPH_FIN.search(line)
            if not matched:
                return False
        else:
            matched_at_start = True

        # strip les # et applique les styles par défault
        level = len(matched.groups()[0])
        if matched_at_start:
            text = self.cur.block().text()[level + 1 :]
        else:
            text = self.cur.block().text()[: -(level + 1)]

        self.cur.beginEditBlock()
        self.cur.select(QTextCursor.LineUnderCursor)
        self.cur.setCharFormat(BlockCharFormat[level])
        self.cur.insertText(text)
        self.cur.setBlockFormat(BlockFormat[level])
        self.cur.endEditBlock()

        self._appendEmptyBlock()
        self.pending = True
        self.setResponse(True)
        return True

    def _set_block_style(self, level):
        self.cur.setBlockFormat(BlockFormat[level])
        self.cur.setBlockCharFormat(BlockCharFormat[level])

    @db_session
    def _update_ddb(self):
        obj = db.Section[self.sectionId]
        new_body = TextSectionFormatter(self.toHtml()).build_body()
        obj.set(text=new_body)
        return new_body


class TextSectionFormatter:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    def write_span(self, span, attrs):
        # print(span)
        # breakpoint()
        return (
            f"<span{self._write_style_block(attrs)}>{self.format_string(span)}</span>"
        )

    def _write_style_block(self, attrs):
        style = build_css_string(attrs)
        return f' style="{style}"' if style else ""

    def format_string(self, tag):
        if tag.string:
            string = html.escape(tag.string)
        else:
            if tag.name == "p":
                string = "<br/>"
            else:
                string = ""

        return string

    def build_body(self):
        res = ["<body>"]
        for tag in self.soup.body:
            if tag == "\n":
                continue
            elif tag.name in ["h1", "h2", "h3", "h4"]:
                res.append(f"<{tag.name}>{self.format_string(tag)}</{tag.name}>")
            elif tag.name == "p":
                res.append("<p>")
                res.extend(self.extract_spans(tag))
                res.append("</p>")
            else:
                raise TypeError(f"le type de tag '{tag.name}' n'est pas reconnu")
        res.append("</body>")
        return "".join(res)

    def extract_params(self, actual):
        """extrait les attributs non standards ou différents"""
        res = {}
        if not actual:
            return res
        for member in actual.split(";")[:-1]:
            attr, value = member.replace(" ", "").split(":")
            value = value.lower()
            if attr not in CSS_BASE["p"] and attr not in CSS_BASE["body"]:
                res[attr] = value
            elif (
                value != CSS_BASE["p"].get(attr, "").lower()
                and value != CSS_BASE["body"].get(attr, "").lower()
            ):
                res[attr] = value
        return res

    def extract_spans(self, tag):
        res = []
        for span in tag:
            if isinstance(span, str):
                res.append(span)
                continue

            new_span_attrs = self.extract_params(span.attrs.get("style", {}))

            res.append(self.write_span(span, new_span_attrs))
        return res
