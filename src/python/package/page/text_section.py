import io
import re
from dataclasses import dataclass

from PySide2 import QtCore
from PySide2.QtCore import QObject, Signal, Property, Slot, QFile, QUrl, QIODevice, Qt
from PySide2.QtGui import (
    QTextDocument,
    QTextCharFormat,
    QTextCursor,
    QBrush,
    QColor,
)
from PySide2.QtWidgets import QApplication
from bs4 import BeautifulSoup
from package.page.blockFormat import P, BlockFormats
from package.page.charFormat import CharFormats
from pony.orm import db_session, make_proxy
from package.database import db


DEFAULT_STYLE_SHEET = """
body {
	color: #363636;
	background-color: #E6E6E6;
	font-family: Verdana;
	font-size: 20pt;
	font-weight: 200;
}

h1 {
	font-size: 30pt;
	color: #D40020;
	font-weight: 600;
	text-decoration: underline;
	text-transform: uppercase;
}

h2 {
	font-size: 25pt;
	color: #006A4E;
	font-weight: 600;
	text-decoration: underline;
}

h3 {
	font-size: 25pt;
	color: #0048BA;
	font-weight: 400;
	text-decoration: underline;
}

h4 {
	color: #363636;
	font-size: 20pt;
	font-weight: 400;
	text-decoration: underline;
}

p {
    color: #363636;
	font-size: 20pt;
	font-weight: 100;
}
"""


class TextSectionEditor(QTextDocument):
    def __init__(self, sectionId, content, pos, selectionStart, selectionEnd):
        super().__init__()
        self.sectionId = sectionId
        self.pos = pos
        self.setDefaultStyleSheet(DEFAULT_STYLE_SHEET)
        self.setHtml(content)
        self.s_start = selectionStart
        self.s_end = selectionEnd

        self.cur = QTextCursor(self)
        self.cur.setPosition(self.pos)
        self.result = {"text": "", "cursorPosition": self.pos, "eventAccepted": False}

    def onKey(self, event):
        self.key = event["key"]
        self.key_text = event["text"]
        self.modifiers = event["modifiers"]

        if False:
            pass
        else:
            # self.result["text"] = TextSectionParser(self.toHtml()).build_html()
            # self.result["text"] = self.toHtml()
            # self.event(ac)
            return self.result

    @property
    def len(self):
        return self.characterCount()

    def onChange(self):
        self.result["text"] = self.toHtml()
        self.result["eventAccepted"] = False
        return self.result

    def onLoad(self):
        # res1 = TextSectionParser(self.toHtml()).build_html()
        # res2 = QTextDocument()
        # res2.setHtml(res1)
        # self.result["text"] = TextSectionParser(self.toHtml()).build_html()
        self.result["text"] = self.toHtml()
        self.result["cursorPosition"] = self.len
        self.result["eventAccepted"] = True
        return self.result

    @db_session
    def update_ddb(self, formatted):
        pass
        # sauve
        # with db_session:
        #     obj = self.db.Section.get(id=sectionId)
        #     obj.set(content=new_lines, curseur=new_curseur)
        # self.equationChanged.emit()


QT_DEFAULT_BLOCK = {
    "margin-top": "0px",
    "margin-bottom": "0px",
    "margin-left": "0px",
    "margin-right": "0px",
    "-qt-block-indent": "0",
    "text-indent": "0px",
    "line-height": "100%",
}

_CSS_BASE = {
    "body": {
        "color": "#363636",
        "background-color": "#E6E6E6",
        "font-family": "Verdana",
        "font-size": "20pt",
        "font-weight": "96",
    },
    "h1": {
        "font-size": "30pt",
        "color": "#D40020",
        "font-weight": "600",
        "text-decoration": "underline",
        "text-transform": "uppercase",
    },
    "h2": {
        "font-size": "25pt",
        "color": "#006A4E",
        "font-weight": "600",
        "text-decoration": "underline",
    },
    "h3": {
        "font-size": "25pt",
        "color": "#0048BA",
        "font-weight": "400",
        "text-decoration": "underline",
    },
    "h4": {
        "color": "#363636",
        "font-size": "medium",
        "font-weight": "400",
        "text-decoration": "underline",
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
# print(CSS_BASE)


def build_css_string(dico):
    return "".join([" " + k + ":" + v + ";" for k, v in dico.items()])


def build_css_block(source=CSS_BASE):
    target = []
    for tag, items in source.items():
        target.append(f"{tag} {{{build_css_string(items)}}}")
    return "".join(target)


class TextSectionParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    def write_span(self, span, attrs):
        return f"  <span{self._write_style_block(attrs)}>{span.string}</span>"

    #
    # def write_block(self, name, attrs):
    #     return f"<{name}{self._write_style_block(attrs)}>"
    #
    def _write_style_block(self, attrs):
        style = build_css_string(attrs)
        return f' style="{style}' if style else ""

    def build_body(self):
        res = ["<body>"]
        for tag in self.soup.body:
            if tag == "\n":
                continue
            elif tag.name in ["h1", "h2", "h3", "h4"]:
                res.append(f" <{tag.name}>{tag.string}</{tag.name}>")
            elif tag.name == "p":
                res.append(" <p>")
                res.extend(self.extract_spans(tag))
                res.append(" </p>")
            else:
                raise TypeError(f"le type de tag '{tag.name}' n'est pas reconnu")
        res.append("</body>")
        return "\n".join(res)

    def extract_params(self, actual):
        """extrait les attributs non standards ou différents"""
        res = {}

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
            new_span_attrs = self.extract_params(span.attrs["style"])

            res.append(self.write_span(span, new_span_attrs))
        return res


# a = TextSectionParser(FRAG, 26)
# # print(a.build_body())
# print(a.build_html())
# a = TextSectionParser(FRAG_CONTROL, 26)
# print(a.build_html())
#
def test_frag():
    x = BeautifulSoup(FRAG, "lxml").prettify()
    y = BeautifulSoup(FRAG_CONTROL, "lxml").prettify()
    for a, b in zip(x.splitlines(), y.splitlines()):
        print(a)
        print(b)
        assert a == b


#
def test_frag_parse():
    x = TextSectionParser(FRAG_CONTROL, 26).build_html()
    y = TextSectionParser(FRAG_CONTROL, 26).build_html()
    for a, b in zip(x.splitlines(), y.splitlines()):
        print(a)
        print(b)
        assert a == b


# test_frag()
# test_frag_parse()
#
# q = QTextDocument()
# q.setHtml(TextSectionParser(FRAG_CONTROL, 26).build_html())
# print(TextSectionParser(FRAG_CONTROL, 26).build_html())
# print(q.toHtml())

fhtml = """<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Verdana'; font-size:20pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">abdcdvezfzef</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">ghijkl mnopqrs </p></body></html>"""


fhtml2 = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Verdana'; font-size:12pt; font-weight:400; font-style:normal;" bgcolor="#e6e6e6">
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:96; color:#363636;">ligne normale</span></p>
<h1 style=" margin-top:18px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:30pt; font-weight:600; text-decoration: underline; color:#d40020; text-transform:uppercase;">titre</span></h1>
<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:25pt; font-weight:600; text-decoration: underline; color:#006a4e;">titre seconde</span></h2>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:96; color:#363636;">debut de ligne </span><span style=" font-size:20pt; font-weight:96; color:#ff0000;">rouge</span><span style=" font-size:20pt; font-weight:96; color:#363636;"> suite de ligne</span></p>
<h3 style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:25pt; text-decoration: underline; color:#0048ba;">titre seconde</span></h3>
<h4 style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; text-decoration: underline; color:#363636;">titre seconde</span></h4>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:96; color:#363636;">du style en fin de </span><span style=" font-size:20pt; font-weight:96; color:#800080; text-decoration: underline;">lingne</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:96; color:#363636;">debut de ligne </span><span style=" font-size:20pt; font-weight:96; color:#ff0000;">rouge</span><span style=" font-size:20pt; font-weight:96; color:#363636;"> suite de ligne</span></p></body></html>
"""
# a = TextSectionParser(fhtml2, 12, {"text": "a", "key": Qt.Key_A, "modifiers": []})
# for i in range(len(a.body.text)):
#     print(i, a.get_tag_by_position(i))
# # a.get_tag_by_position(12)


a = TextSectionParser(fhtml2)
print(a.build_body())
