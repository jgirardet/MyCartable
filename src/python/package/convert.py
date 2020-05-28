import os
import uuid
from io import StringIO
from operator import attrgetter, methodcaller
from subprocess import run, CalledProcessError

from pathlib import Path
import sys
import logging

from PySide2.QtCore import QDir, QRectF, Qt, QPoint, QRect, QStandardPaths, QLine, QSize
from PySide2.QtGui import QImage, QPainter, QColor, QBrush
from mako.lookup import TemplateLookup
from mako.runtime import Context
from package import DATA, BINARY
from package.constantes import BASE_FONT, ANNOTATION_TEXT_BG_OPACITY
from package.database import db
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


"""

                       Files other than Impress documents are opened in        
                       default mode , regardless of previous mode.             
   --convert-to OutputFileExtension[:OutputFilterName] \                      
     [--outdir output_dir] [--convert-images-to]                               
                       Batch convert files (implies --headless). If --outdir   
                       isn't specified, then current working directory is used 
                       as output_dir. If --convert-images-to is given, its     
                       parameter is taken as the target filter format for *all*
                       images written to the output format. If --convert-to is 
                       used more than once, the last value of                  
                       OutputFileExtension[:OutputFilterName] is effective. If 
                       --outdir is used more than once, only its last value is 
                       effective. For example:                                 
                   --convert-to pdf *.odt                                      
                   --convert-to epub *.doc                                     
                   --convert-to pdf:writer_pdf_Export --outdir /home/user *.doc
                   --convert-to "html:XHTML Writer File:UTF8" \             
                                --convert-images-to "jpg" *.doc              
                   --convert-to "txt:Text (encoded):UTF8" *.doc              
   --print-to-file [--printer-name printer_name] [--outdir output_dir]         
                       Batch print files to file. If --outdir is not specified,
                       then current working directory is used as output_dir.   
                       If --printer-name or --outdir used multiple times, only 
                       last value of each is effective. Also, {Printername} of 
                       --pt switch interferes with --printer-name.             
  
"""


class LibreOfficeConverter:
    def __init__(self):
        pass


def create_lookup():
    lookup = TemplateLookup()
    for file in QDir(":/templates").entryInfoList():
        lookup.put_string(file.fileName(), read_qrc(file.absoluteFilePath()))
    return lookup


html_lookup = create_lookup()


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
                cel_dict["font-size"] = cel.style.pointSize
                if cel.style.underline:
                    cel_dict["text-transfomation"] = "underline"
                elif cel.style.strikeout:
                    cel_dict["text-transfomation"] = "line-through"
                else:
                    cel_dict["text-transfomation"] = "none"

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
    main_page = html_lookup.get_template("base.html")
    context_vars = create_context_var(section_id, tmpdir)
    # print(context_vars)
    buf = StringIO()
    ctx = Context(buf, **context_vars)
    main_page.render_context(context=ctx)
    output_html = Path(tmpdir, uuid.uuid4().hex + ".html")
    output_html.write_text(buf.getvalue())
    return output_html


def create_images_with_annotation(image_section, tmpdir):
    image = QImage()
    painter = QPainter()
    # olf = QFile(str(FILES / image_section["path"]))
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
    new_path = str(Path(tmpdir) / (uuid.uuid4().hex + ".png"))
    image.save(new_path)
    return new_path


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
