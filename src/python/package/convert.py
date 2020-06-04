import os
import tempfile
import uuid
from io import StringIO
from operator import attrgetter, methodcaller
from subprocess import run, CalledProcessError

from pathlib import Path
import sys
import logging

from PySide2.QtCore import (
    QDir,
    QRectF,
    Qt,
    QPoint,
    QRect,
    QStandardPaths,
    QLine,
    QSize,
    QBuffer,
)
from PySide2.QtGui import QImage, QPainter, QColor, QBrush
from bs4 import NavigableString, BeautifulSoup
from mako.lookup import TemplateLookup
from mako.runtime import Context
from package import DATA, BINARY
from package.constantes import BASE_FONT, ANNOTATION_TEXT_BG_OPACITY
from package.database import db
from package.database.factory import f_section, f_textSection, f_page, f_imageSection
from package.database.sections import (
    ImageSection,
    TableauSection,
    Annotation,
    AnnotationText,
    TableauCell,
)
from package.database.structure import Page
from package.files_path import FILES
from package.utils import read_qrc
from pony.orm import Set, db_session

LOG = logging.getLogger(__name__)
import qrc

from package.ui_manager import DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR


def get_binary_path(name):
    name = name + ".exe" if sys.platform == "win32" else name
    exec_path = BINARY / name
    return exec_path


def get_command_line_pdftopng(pdf, png_root, resolution):
    cmd = [
        get_binary_path("pdftopng"),
        "-r",
        resolution,
        pdf,
        png_root,
    ]
    return [str(i) for i in cmd]


def collect_files(root: Path, pref="", ext: str = ""):
    res = sorted(root.glob(f"{pref}*{ext}"), key=lambda p: p.name)
    return res


def run_convert_pdf(pdf, png_root, prefix="xxx", resolution=200, timeout=30):
    root = Path(png_root)
    if not root.is_dir():
        root.mkdir(parents=True)

    expected_out = root / prefix

    cmd = get_command_line_pdftopng(pdf, str(expected_out), resolution=resolution)

    try:
        run(cmd, timeout=timeout, check=True, capture_output=True)
    except CalledProcessError as err:
        LOG.error(err.stderr)
        return []
    except TimeoutError as err:
        LOG.error(err.stderr)
        return []

    files = collect_files(root, pref=prefix, ext=".png")
    return files


class LibreOfficeConverter:
    def __init__(self):
        pass


def create_lookup():
    lookup = TemplateLookup()
    for file in QDir(":/templates").entryInfoList():
        lookup.put_string(file.fileName(), read_qrc(file.absoluteFilePath()))
    return lookup


templates = create_lookup()


def create_context_var(section_id, tmpdir):
    page = Page[section_id].to_dict()
    sections = []
    for sec in Page[section_id].content:
        # print(section)
        # breakpoint()
        section = sec.to_dict()
        if section["classtype"] == "ImageSection":
            path = create_images_with_annotation(section, tmpdir)
            section["path"] = Path(path).as_uri()
        elif section["classtype"] == "EquationSection":
            section["content"] = section["content"].replace(" ", "\u2000").split("\n")

        elif section["classtype"] == "TableauSection":
            _cells = []
            for cel in sec.cells.order_by(TableauCell.x, TableauCell.y):
                cel_dict = cel.to_dict()
                cel_dict["color"] = cel.style.fgColor.name()
                cel_dict["background-color"] = (
                    cel.style.bgColor.name()
                    if cel.style.bgColor.name() != "#000000"
                    else "transparent"
                )
                # cel_dict["font-size"] = " font-size"=cel.style.pointSize
                if cel.style.underline:
                    cel_dict["text-decoration"] = " text-decoration=underline:"
                elif cel.style.strikeout:
                    cel_dict["text-decoration"] = " text-decoration=line-through:"
                else:
                    cel_dict["text-decoration"] = ""

                _cells.append(cel_dict)
            section["cells"] = _cells
        elif section["classtype"] == "MultiplicationSection":
            start = (1 + sec.n_chiffres) * sec.columns
            section["line_1"] = list(range(start, start + sec.columns))

        sections.append(section)
    css = read_qrc(":/css/export.css")
    return {"page": page, "sections": sections, "css": css}


@db_session
def convert_page_to_html(section_id, tmpdir):
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    main_page = templates.get_template("base.html")
    context_vars = create_context_var(section_id, tmpdir)
    # print(context_vars)
    buf = StringIO()
    ctx = Context(buf, **context_vars)
    main_page.render_context(context=ctx)
    output_html = Path(tmpdir, uuid.uuid4().hex + ".html")
    output_html.write_text(buf.getvalue())
    return output_html


@db_session
def convert_page_to_odt(section_id, tmpdir):
    QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    main_page = templates.get_template("base.fodt")
    context_vars = create_context_var(section_id, tmpdir)
    buf = StringIO()
    ctx = Context(buf, **context_vars)
    main_page.render_context(context=ctx)
    output_html = Path(tmpdir, uuid.uuid4().hex + ".fodt")
    output_html.write_text(buf.getvalue())
    return output_html


def create_images_with_annotation(image_section, tmpdir=None):
    image = QImage()
    painter = QPainter()
    image.load(str(FILES / image_section["path"]))

    painter.begin(image)
    for annotation_id in image_section["annotations"]:
        annotation = Annotation[annotation_id].to_dict()
        if annotation["classtype"] == "AnnotationText":
            draw_annotation_text(annotation, image, painter)
        elif annotation["classtype"] == "AnnotationDessin":
            width = annotation["width"] * image.width()
            height = annotation["height"] * image.height()
            x = annotation["x"] * image.width()
            y = annotation["y"] * image.height()
            sx = annotation["startX"] * width
            ex = annotation["endX"] * width
            sy = annotation["startY"] * height
            ey = annotation["endY"] * height
            pz = annotation["pointSize"]

            if sx <= ex:
                sx += pz / 2
                ex -= pz / 2
            else:
                sx -= pz / 2
                ex += pz / 2

            if sx <= ey:
                sy += pz / 2
                ey -= pz / 2
            else:
                sy -= pz / 2
                ey += pz / 2

            pen = painter.pen()
            pen.setWidth(annotation["pointSize"])
            pen.setColor(annotation["fgColor"])
            painter.setPen(pen)
            painter.setOpacity(0.2 if annotation["tool"] == "fillrect" else 1)
            painter.setRenderHint(QPainter.Antialiasing)
            startPoint = QPoint(x + sx, y + sy)
            endPoint = QPoint(x + ex, y + ey)
            if annotation["tool"] == "trait":
                painter.drawLine(startPoint, endPoint)
            elif annotation["tool"] == "fillrect":
                painter.fillRect(QRect(startPoint, endPoint), annotation["bgColor"])
            elif annotation["tool"] == "rect":
                painter.drawRect(QRect(startPoint, endPoint))
            elif annotation["tool"] == "ellipse":
                painter.drawEllipse(QRect(startPoint, endPoint))

    painter.end()
    if tmpdir:
        new_path = str(Path(tmpdir) / (uuid.uuid4().hex + ".png"))
        image.save(new_path)
        return new_path

    else:
        buf = QBuffer()
        buf.open(QBuffer.ReadWrite)
        image.save(buf, "PNG")
        buf.seek(0)
        res = buf.readAll().toBase64()
        buf.close()
        return res


def draw_annotation_text(annotation: dict, image: QImage, painter: QPainter):

    # d'abord font params
    font = painter.font()
    font.setPixelSize(
        image.height()
        / (annotation["pointSize"] or DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR)
    )
    font.setUnderline(annotation["underline"])
    if not annotation.get("family", None):  # get considère empty "" comme true
        font.setFamily(BASE_FONT)
    painter.setFont(font)

    # Ensuite le crayon
    pen = painter.pen()
    pen.setColor(annotation["fgColor"])
    painter.setPen(pen)

    # On evalue la taille de et la position de l'annotation
    size = painter.fontMetrics().size(0, annotation["text"])
    rect = QRect(
        QPoint(annotation["x"] * image.width(), annotation["y"] * image.height()), size
    )

    #
    painter.setOpacity(ANNOTATION_TEXT_BG_OPACITY)
    painter.fillRect(rect, annotation["bgColor"])
    painter.setOpacity(1)

    painter.drawText(
        rect, annotation["text"],
    )


#
# ano = {
#     "id": 1,
#     "x": 0.13990825688073394,
#     "y": 0.18775510204081633,
#     "classtype": "AnnotationText",
#     "text": "fezfze\nffzefze",
#     "styleId": 9046,
#     "family": "",
#     "underline": False,
#     "pointSize": None,
#     "strikeout": False,
#     "weight": None,
#     "bgColor": QColor.fromRgbF(0.000000, 1.000000, 0.000000, 1.000000),
#     "fgColor": QColor.fromRgbF(0.000000, 0.000000, 1.000000, 1.000000),
# }
# img = "/home/jimmy/dev/cacahuete/MyCartable/tests/resources/sc1.png"

# create_images_with_annotation(img)


def simple_p(value):
    return f"""<text:p text:style-name="Standard">{value}</text:p>"""


def new_automatic_text(style_str):
    item_style = [x.split(":") for x in style_str.replace(" ", "")[:-1].split(";")]
    style_name = uuid.uuid4().hex
    res = f"""<style:style style:name="{style_name}" style:family="text"> <style:text-properties """
    for k, v in item_style:
        if k == "color":
            res = res + f''' fo:color="{QColor(v).name()}"'''
        elif k == "text-decoration":
            res = (
                res
                + f''' style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"'''
            )
            # new_prop.setAttribute("textunderlinestyle", "solid")
    res = res + """/></style:style>"""
    return style_name, res


def span_text(value: NavigableString):
    # for member in value.split(";")[:-1]:
    style_str = value.attrs.get("style", None)
    new_style = None
    if style_str:
        name, new_style = new_automatic_text(style_str)
        span_res = f"""<text:span text:style-name="{name}">{value.text}</text:span>"""
    else:
        span_res = value.text
    return span_res, new_style


def new_p(ptag):
    res = [f"""<text:p text:style-name="Standard">"""]
    automatic = []
    for elem in ptag.contents:
        if not elem.name:
            res.append(elem)
        elif elem.name == "span":
            string, style = span_text(elem)
            res.append(string)
            if style:
                automatic.append(style)
    res.append("</text:p>")
    return "".join(res), "\n".join(automatic)


def new_h(htag):
    level = htag.name[-1]
    res = f"""<text:h text:style-name="Heading_20_{level}" text:outline-level="{level}">{htag.text}</text:h>"""
    return res


def text_section(section):
    soup = BeautifulSoup(section.text, "html.parser")
    str_res = []
    automatic_res = []
    for paragraphe in soup.body.contents:
        if paragraphe.name.startswith("h"):
            str_res.append(new_h(paragraphe))
        elif paragraphe.name == "p":
            new_text, new_style = new_p(paragraphe)
            str_res.append(new_text)
            automatic_res.append(new_style)

    return "\n".join(str_res), "\n".join(automatic_res)


def image_section(section_e):
    section = section_e.to_dict()
    content = create_images_with_annotation(section)
    res = f"""<text:p text:style-name="Standard">
            <draw:frame draw:style-name="fr1" draw:name="{uuid.uuid4().hex}" text:anchor-type="paragraph" svg:width="17cm" svg:height="9.562cm" draw:z-index="0">
                <draw:image loext:mime-type="image/png">
                <office:binary-data>{content.data().decode()}</office:binary-data>
                </draw:image>
            </draw:frame>
        </text:p>"""
    return res


def build_body(page_id):
    # page = Page[page_id].to_dict()
    # context_vars = create_context_var(page_id, tmpdir)
    tags = []
    automatic_res = []
    page = Page[page_id]
    for section in page.content:
        if section.classtype == "TextSection":
            new_tags, automatic_tags_style = text_section(section)
            automatic_res.append(automatic_tags_style)

        elif section.classtype == "ImageSection":
            new_tags = image_section(section)

        tags.append(new_tags)
    tmpl = templates.get_template("body.xml")
    body = "\n".join(tags)
    return (
        tmpl.render(titre=page.titre, body=body),
        "\n".join(automatic_res),
    )


def build_automatic_styles(automatic_styles):
    tmpl = templates.get_template("automatic-styles.xml")
    return tmpl.render(automatic_styles=automatic_styles)


def build_styles():
    tmpl = templates.get_template("styles.xml")
    return tmpl.render()


def build_master_styles():
    tmpl = templates.get_template("master-styles.xml")
    return tmpl.render()


@db_session
def merge_all_xml(page_id):

    body, automatic_data = build_body(page_id)
    automatic_styles = build_automatic_styles(automatic_data)
    master_styles = build_master_styles()
    styles = build_styles()

    tmpl = templates.get_template("base.xml")
    res = tmpl.render(
        body=body,
        automatic_styles=automatic_styles,
        master_styles=master_styles,
        styles=styles,
    )
    output_html = Path("/tmp", "AAAAA" + ".fodt")
    # output_html = Path("/tmp", uuid.uuid4().hex + ".fodt")
    output_html.write_text(res)
    return output_html


from package.database import init_database

init_database()
page = f_page()
sec = f_textSection(
    page=page.id,
    text="""<body><p><span>ligne normale</span></p><h1>titre</h1><h2>titre seconde</h2><p><span>debut de ligne </span><span style=" color:#ff0000;">rouge</span><span> suite de ligne</span></p><h3>titre seconde</h3><h4>titre seconde</h4><p><span>du</span><span style=" text-decoration:underline; color:#0048ba;"> style en fin </span><span>de </span><span style=" color:#800080;">lingne</span></p><p><span>debu</span><span style=" text-decoration:underline; color:#006a4e;">t de ligne </span><span style=" text-decoration:underline; color:#006a4e;">rou</span><span style=" color:#ff0000;">ge</span><span> suite de ligne</span></p></body>""",
)
img = f_imageSection(page=page.id)
tp = tempfile.TemporaryDirectory()
res = merge_all_xml(page.id)
import subprocess

subprocess.run(["xdg-open", str(res)])
# print(res)
