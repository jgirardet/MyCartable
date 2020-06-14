import html
import re
from contextlib import contextmanager
import logging

from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QBrush,
    QColor,
    Qt,
    QTextBlockFormat,
    QTextDocumentFragment,
    QFont,
)
from bs4 import BeautifulSoup
from package.utils import KeyW
from pony.orm import db_session
from package.database import db


LOG = logging.getLogger(__name__)

RED = "#D40020"
BLUE = "#0048BA"
GREEN = "#006A4E"
BLACK = "#363636"

_CSS_BASE = {
    "body": {
        "color": BLACK,
        "background-color": "#E6E6E6",
        "font-family": "Verdana",
        "font-size": "20pt",
        "font-weight": "96",
        "margin-top": "12px",
    },
    "h1": {
        "font-size": "30pt",
        "color": RED,
        "font-weight": "600",
        "text-decoration": "underline",
        "text-transform": "uppercase",
        "margin-top": "18px",
        "margin-left": "10px",
        "margin-right": "10px",
    },
    "h2": {
        "font-size": "25pt",
        "color": GREEN,
        "font-weight": "600",
        "text-decoration": "underline",
        "margin-top": "16px",
        "margin-left": "10px",
        "margin-right": "10px",
    },
    "h3": {
        "font-size": "25pt",
        "color": BLUE,
        "font-weight": "400",
        "text-decoration": "underline",
        "margin-top": "14px",
        "margin-left": "10px",
        "margin-right": "10px",
    },
    "h4": {
        "color": BLACK,
        "font-size": "20pt",
        "font-weight": "400",
        "text-decoration": "underline",
        "margin-top": "18px",
        "margin-left": "10px",
        "margin-right": "10px",
    },
    "p": {
        "color": BLACK,
        "background-color": "#E6E6E6",
        "font-family": "Verdana",
        "font-size": "20pt",
        "font-weight": "96",
        "margin-top": "12px",
        "margin-left": "10px",
        "margin-right": "10px",
    },
}


def lowerise(source):
    target = {}
    # lowerise les cles mais pas les values
    for k, v in source.items():
        k = k.lower()
        if isinstance(v, str):
            target[k] = v
        elif isinstance(v, dict):  # pragma: no branch
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
        if "font-weight" in datas:  # pragma: no branch
            cf.setFontWeight(
                int(datas["font-weight"]) / 8
            )  # cssweight = 8 * QFont.wieight
        if "text-transform" in datas:
            if datas["text-transform"] == "uppercase":  # pragma: no branch
                cf.setFontCapitalization(QFont.AllUppercase)
            # elif datas["text-transform"] == "lowercase":
            #     cf.setFontCapitalization(QFont.AllLowercase)

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
        #
        mt = datas.get("margin-left", None)
        mt = float(mt.rstrip("px"))
        cf.setLeftMargin(mt)
        mt = datas.get("margin-right", None)
        mt = float(mt.rstrip("px"))
        cf.setRightMargin(mt)

        res.append(cf)
    return res


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
        else:
            raise KeyError("int ou string")


blockCharFormat = BlockFormat_(build_bockCharFormat_from_css(CSS_BASE))
blockFormat = BlockFormat_(build_blockFormat_from_css(CSS_BASE))


RE_AUTOPARAGRAPH_DEBUT = re.compile(r"^(#{1,6})\s\S+$")
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
    def s_len(self):
        return abs(self.s_end - self.s_start)

    @property
    def pos(self):
        return self.cur.position()

    def onChange(self):

        self._update_ddb()
        self.setResponse(True)
        return self.result

    @db_session
    def onLoad(self):
        item = db.Section[self.sectionId]
        if item:
            self.setHtml(item.text)
            self.setResponse(True, cur=self.len)
        return self.result

    def onMenu(self, style={}, **kwargs):
        backup = [self.pos, self.s_start, self.s_end]

        for k, v in style.items():
            # un peut répétition mais uniquement sur des if alors ...
            if k == "fgColor":
                self._set_fg_color(v)
            elif k == "underline":
                self._set_underline(style["underline"])

            self.cur.setPosition(backup[0])
            self.s_start = backup[1]
            self.s_end = backup[2]

        if self.pending:
            # else:
            self._update_ddb()
        else:
            self.setResponse(False)
        return self.result

    def onKey(self, event):

        # on met en premier ceux à qui il faut passer l'event

        if event["key"] == Qt.Key_Return:
            self.do_key_return(event)

        elif event["modifiers"] == Qt.ControlModifier:
            self.do_control_modifier(event)

        else:
            self.setResponse(False)

        if self.pending:
            self._update_ddb()
        return self.result

    def do_control_modifier(self, event):
        if event == KeyW.KEY_1:
            self.do_key_1()

        elif event == KeyW.KEY_2:
            self.do_key_2()

        elif event == KeyW.KEY_3:
            self.do_key_3()

        elif event == KeyW.KEY_4:
            self.do_key_4()

        elif event["key"] == Qt.Key_U:
            self.do_key_u()

    def do_key_1(self):
        self._set_fg_color(BLACK)

    def do_key_2(self):
        self._set_fg_color(BLUE)

    def do_key_3(self):
        self._set_fg_color(GREEN)

    def do_key_4(self):
        self._set_fg_color(RED)

    def do_key_return(self, event):
        block = self.findBlock(self.pos)
        if event["modifiers"] == Qt.ControlModifier:
            self._appendEmptyBlock()
        elif event["modifiers"] == Qt.ShiftModifier:
            self._insertEmptyBlock()
        elif block.blockFormat().headingLevel():
            self._appendEmptyBlock()
        else:
            if self._headerAutoFormat():
                return
            else:
                self.setResponse(False)

    def do_key_u(self):
        self._set_underline("toggle")

    def setResponse(self, accepted, text=None, cur=None):
        self.result["text"] = text or self.toHtml()
        self.result["cursorPosition"] = cur or self.cur.position()
        self.result["eventAccepted"] = accepted

    def _appendEmptyBlock(
        self, section="p", pre_move=QTextCursor.EndOfBlock, set_response=True
    ):
        self.cur.movePosition(pre_move)
        self.cur.insertBlock(blockFormat[section], blockCharFormat[section])
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
        self.cur.setCharFormat(blockCharFormat[level])
        self.cur.insertText(text)
        self.cur.setBlockFormat(blockFormat[level])
        self.cur.endEditBlock()

        self._appendEmptyBlock()
        self.pending = True
        self.setResponse(True)
        return True

    @contextmanager
    def _merge_char_format(self):
        self._select_word_or_selection()
        f: QTextCharFormat = QTextCharFormat()
        yield f
        self.cur.mergeCharFormat(f)
        self.pending = True
        self.setResponse(True, cur=max(self.pos, self.s_start, self.s_end))

    def _select_word_or_selection(self):
        if self.s_start < self.pos:
            self.cur.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, self.s_len)
        elif self.s_end > self.pos:
            self.cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.s_len)
        else:
            self.cur.select(QTextCursor.WordUnderCursor)

    def _set_block_style(self, level):
        self.cur.setBlockFormat(blockFormat[level])
        self.cur.setBlockCharFormat(blockCharFormat[level])

    def _set_fg_color(self, color):
        with self._merge_char_format() as f:
            f.setForeground(QBrush(QColor(color)))

    def _set_underline(self, value):
        with self._merge_char_format() as f:
            if value == "toggle":
                value = not self.cur.charFormat().fontUnderline()
            f.setFontUnderline(value)

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
