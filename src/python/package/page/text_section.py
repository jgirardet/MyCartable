import io
import re
from dataclasses import dataclass

from PySide2 import QtCore
from PySide2.QtCore import QObject, Signal, Property, Slot, QFile, QUrl, QIODevice
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
import cssutils

FRAG = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Verdana'; font-size:12pt; font-weight:400; font-style:normal;" bgcolor="#e6e6e6">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:100%;"><span style=" font-size:20pt; color:#363636;">ligne normale </span></p>
<h1 style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:100%;"><span style=" font-size:35pt; font-weight:600; text-decoration: underline; color:#ff0000; text-transform:uppercase;">titre</span><span style=" font-size:20pt; color:#363636;"> </span></h1>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:100%;"><span style=" font-size:20pt; color:#363636;">du style en fin de </span><span style=" font-size:20pt; color:#800080;">lingne</span><span style=" font-size:20pt; color:#363636;"> </span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:100%;"><span style=" font-size:20pt; color:#363636;">debut de ligne </span><span style=" font-size:20pt; color:#ff0000;">rouge</span><span style=" font-size:20pt; color:#363636;"> suite de ligne </span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:100%;"><span style=" font-size:4pt; color:#0000ff;">bleu </span><span style=" font-size:20pt; color:#ffa500;">bleu debut </span><span style=" font-size:4pt; color:#0000ff;">debut </span><span style=" font-size:20pt; color:#363636;">debut de ligne </span><span style=" font-size:20pt; color:#ff0000;">rouge</span><span style=" font-size:20pt; color:#363636;"> suite de ligne </span></p></body></html>"""
RESET_CSS = """html,body,div,span,applet,object,iframe,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,abbr,acronym,address,big,cite,code,del,dfn,em,img,ins,kbd,q,s,samp,small,strike,strong,sub,sup,tt,var,b,u,i,center,dl,dt,dd,ol,ul,li,fieldset,form,label,legend,table,caption,tbody,tfoot,thead,tr,th,td,article,aside,canvas,details,embed,figure,figcaption,footer,header,hgroup,menu,nav,output,ruby,section,summary,time,mark,audio,video { margin: 0; padding: 0; border: 0; font-size: 100%; font: inherit; vertical-align: baseline;}
article,aside,details,figcaption,figure,footer,header,hgroup,menu,nav,section { display: block;}
body { line-height: 1;}
ol,ul { list-style: none;}
blockquote,q { quotes: none;}
table { border-collapse: collapse; border-spacing: 0;}"""


CSS_BASE = {
    "html": {},
    "body": {
        "style": {
            "color": "#363636",
            "background-color": "#E6E6E6",
            "font-family": "Verdana",
            "font-size": "20pt",
            "font-weight": "400",
            "font-style": "normal",
        },
        "span": {},
    },
    "h1": {
        "style": {
            "font-size": "35pt",
            "color": "#FF0000",
            "font-weight": "600",
            "text-decoration": "underline",
            "text-transform": "uppercase",
        },
        "span": {},
    },
    "p": {"style": {}, "span": {}},
}
# "font-family": "Verdana;"
# "font-size": "35pt;"
# "letter-spacing": "1pt;"
# "word-spacing": "2pt;"
# "color": "#FF0000;"
# "font-weight": "700;"
# "text-decoration": "underline;"
# "text-transform": "capitalize;"
# }


def build_css_string(dico):
    return "".join([k + ":" + v + ";" for k, v in dico.items()])


def build_css():
    res = []
    for tag, props in CSS_BASE.items():
        res.append(f"{tag} {{{build_css_string(props)}}}")
    return RESET_CSS + "\n" + "\n".join(res)


QT_DEFAULT_BLOCK = {
    "margin-top": "0px",
    "margin-bottom": "0px",
    "margin-left": "0px",
    "margin-right": "0px",
    "-qt-block-indent": "0",
    "text-indent": "0px",
    "line-height": "100%",
}

EXPECTED_TAGS = {
    "html": {},
    "body": {},
    "h1": {"style": QT_DEFAULT_BLOCK, "span": CSS_BASE["h1"]["style"],},
    "p": {
        "style": QT_DEFAULT_BLOCK,
        "span": {
            "font-size": CSS_BASE["body"]["style"]["font-size"],
            "color": CSS_BASE["body"]["style"]["color"],
        },
    },
}


class TextSectionParser:
    def __init__(self, html, pos):
        self.html = BeautifulSoup(html, "lxml").html
        self.body = self.html.body
        self.pos = pos
        self.res = ""

    def write_span(self, span, attrs):
        return f"\t<span{self._write_style_block(attrs)}>{span.string}</span>"

    def write_block(self, name, attrs):
        return f"<{name}{self._write_style_block(attrs)}>"

    def _write_style_block(self, attrs):
        style = build_css_string(attrs)
        return f" style={style}" if style else ""

    def extract_tree_params(self):
        res = []
        for tag in self.body:
            if tag == "\n":
                continue
            elif tag.name in ["p", "h1"]:
                new_p_attrs = self.extract_params(
                    tag.attrs["style"], EXPECTED_TAGS[tag.name]["style"]
                )
                res.append(self.write_block(tag.name, new_p_attrs))
                res.extend(self.extract_spans(tag))
                res.append(f"</{tag.name}>")
            else:
                raise TypeError(f"le type de tag '{tag.name}' n'est pas reconnu")
        return "\n".join(res)

    def extract_params(self, actual, expected):
        """extrait les attributs non standards ou différents"""
        res = {}
        # breakpoint()

        for member in actual.split(";")[:-1]:
            attr, value = member.strip().split(":")
            if attr not in expected:
                res[attr] = value
            elif value != expected[attr]:
                res[attr] = value
        return res

    def extract_spans(self, tag):
        res = []
        for span in tag:
            if span == tag.contents[-1] and not span.stripped_strings:
                breakpoint()
                continue
            new_span_attrs = self.extract_params(
                span.attrs["style"], EXPECTED_TAGS[tag.name]["span"]
            )
            res.append(self.write_span(span, new_span_attrs))
        return res


a = TextSectionParser(FRAG, 26)
print(a.extract_tree_params())
