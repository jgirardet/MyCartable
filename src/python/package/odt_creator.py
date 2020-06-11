import tempfile
import uuid
from pathlib import Path

from PySide2.QtGui import QColor
from bs4 import BeautifulSoup, NavigableString
from odf.opendocument import OpenDocumentText, load
from odf.style import (
    Style,
    TextProperties,
    ParagraphProperties,
    PageLayoutProperties,
    PageLayout,
    MasterPage,
)
from odf.text import P, H, Span
from odf.draw import Image, Frame, G, Page

# from package.convert import create_images_with_annotation
from package.page.text_section import _CSS_BASE
import subprocess

#
# class OdtCreator:
#     def __init__(self):
#         self.doc = OpenDocumentText()
#         self.availables_styles = ["p", "h1", "h2", "h3", "h4"]
#         self.styles = {}
#         self.text_properties = {}
#         self.page_layout = self.build_layout()
#         self.build_styles()
#         self.doc.masterstyles.addElement(
#             MasterPage(name="masterStandard", pagelayoutname="page_layout")
#         )
#
#     def add_h(self, level, content):
#         level_str = "h" + str(level) if isinstance(level, int) else level
#         text = H(stylename=self.styles[level_str], outlinelevel=str(level))
#         text.addText(content)
#         self.doc.text.addElement(text)
#
#     def add_p(self, content):
#         text = P(stylename=self.styles["p"])
#         text.addText(content)
#         self.doc.text.addElement(text)
#         return text
#
#     def get_span_from_html_span(self, text: NavigableString):
#         style_str = text.attrs.get("style", None)
#         if not style_str:
#             return text.text
#         new_style = Style(name=uuid.uuid4().hex, family="text")
#         new_prop = TextProperties()
#
#         for member in style_str.split(";")[:-1]:
#             attr, value = member.replace(" ", "").split(":")
#             attr = attr.lower()
#             if attr == "color":
#                 new_prop.setAttribute("color", QColor(value).name())
#             if attr == "text-decoration":
#                 new_prop.setAttribute("textunderlinestyle", "solid")
#
#         new_style.addElement(new_prop)
#         self.doc.automaticstyles.addElement(new_style)
#         res = Span(stylename=new_style, text=text.text)
#         return res
#
#     def build_layout(self):
#
#         p = PageLayoutProperties(
#             pagewidth="21.001cm",
#             pageheight="29.7cm",
#             printorientation="portrait",
#             margintop="0.5cm",
#             marginbottom="2cm",
#             marginleft="1cm",
#             marginright="1cm",
#             writingmode="lr-tb",
#         )
#         pagelayout = PageLayout(name="page_layout")
#         pagelayout.addElement(p)
#         self.doc.automaticstyles.addElement(pagelayout)
#         return pagelayout
#
#     def build_paragraph_style(self, level):
#         name = level + "_style"
#         st = Style(name=name, family="paragraph")
#         st.addElement(self.build_text_properties(level))
#         st.addElement(self.build_paragraph_properties(level))
#         self.styles[level] = st
#         self.doc.styles.addElement(st)
#
#     def build_paragraph_properties(self, level):
#         base = dict(_CSS_BASE["body"])
#         base.update(_CSS_BASE[level])
#
#         return ParagraphProperties(
#             attributes={
#                 "margintop": base.get("margin-top", "0"),
#                 "marginbottom": base.get("margin-bottom", "0"),
#                 # "marginleft": base.get("margin-left", "0"),
#                 # "marginright": base.get("margin-right", "0"),
#             }
#         )
#
#     def build_text_properties(self, level):
#         base = dict(_CSS_BASE["body"])
#         base.update(_CSS_BASE[level])
#
#         textunderlinestyle = (
#             "solid" if base.get("text-decoration", None) == "underline" else "none"
#         )
#
#         res = TextProperties(
#             attributes={
#                 "fontname": base["font-family"],
#                 "fontfamily": base["font-family"],
#                 "fontstylename": "Normal",
#                 "fontpitch": "variable",
#                 "fontsize": base["font-size"],
#                 "fontweight": base["font-weight"],
#                 "textunderlinestyle": textunderlinestyle,
#                 "color": base["color"],
#                 "texttransform": base.get("text-transform", "none"),
#             }
#         )
#         self.text_properties[level] = res
#         return res
#
#     def build_styles(self):
#         for st in self.availables_styles:
#             self.build_paragraph_style(st)
#
#     def convert_text_section(self, section):
#         soup = BeautifulSoup(section["text"], "html.parser")
#         for part in soup.contents:
#             if part.name.startswith("h"):
#                 self.add_h(part.name, part.text)
#             elif part.name == "p":
#                 new_text = self.add_p("")
#                 if len(part) == 1:
#                     self.add_p(part.text)
#                 else:
#                     for words in part:
#                         if words.name == "span":
#                             span = self.get_span_from_html_span(words)
#                             if isinstance(span, str):
#                                 new_text.addText(span)
#                             else:
#                                 new_text.addElement(span)
#                         else:
#                             new_text.addText(words)
#
#     # def convert_image_section(self, section):
#     #     with tempfile.TemporaryDirectory() as t:
#     #         path = create_images_with_annotation(section, t)
#
#     def save(self):
#         self.doc.save("/home/jimmy/bla.odt")
#
#
# html = """<p><span>ligne normale</span></p><h1>titre</h1><h2>titre seconde</h2><p><span>debut de ligne </span><span style=" color:#ff0000;">rouge</span><span> suite de ligne</span></p><h3>titre seconde</h3><h4>titre seconde</h4><p><span>du sty</span><span style=" text-decoration:underline; color:#0048ba;">le en fin</span><span> de </span><span style=" color:#800080;">lingne</span></p><p><span>debut de ligne </span><span style=" color:#ff0000;">rouge</span><span> suite de ligne</span></p>"""
#
#
# x = OdtCreator()
#
# x.convert_text_section({"text": html})
#
# z = x.doc.addPicture("/tmp/tmp0rp99okt/adc867203c6b4696b4a7fc8208b368ce.png")
# print(z)
# # photostyle = Style(name="MyMaster-photo", family="graphic")
# # x.doc.styles.addElement(photostyle)
#
# # photoframe = Frame(
# #     stylename=photostyle, width="25cm", height="18.75cm", x="1.5cm", y="2.5cm"
# # )
# i = Image(href=z)
# f = Frame(
#     # name="image1",
#     anchortype="paragraph",
#     # relwidth="100%",
#     # relheight="scale",
#     # zindex="0",
# )
# f.addElement(i)
# p = P()
# p.addElement(f)
# x.doc.text.addElement(p)

# x.save()

# fodt = "/home/jimmy/dev/MyCartable/src/data/templates/odt.fodt"
# from lxml import etree
#
# r = etree.XML(Path(fodt).read_bytes())
# x = r.find('.//style:style[@style:name="Text_20_body"]', r.nsmap)
# subprocess.run(
#     "xdg-open /home/jimmy/dev/MyCartable/src/data/templates/odt.fodt".split()
# )
