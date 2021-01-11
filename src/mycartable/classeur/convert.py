import json
import math
import os
import re
import subprocess
import uuid
from functools import partial, lru_cache
from pathlib import Path

from PyQt5 import sip
from PyQt5.QtQuick import QQuickItem
from typing import Tuple

from PyQt5.QtCore import (
    QBuffer,
    QDir,
    QPoint,
    QRect,
    QTemporaryFile,
    QPointF,
    QUrl,
    QTimer,
    QRectF,
    QSizeF,
)
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFontDatabase,
    QImage,
    QPainterPath,
    QDesktopServices,
)
from bs4 import NavigableString, BeautifulSoup
from mako.lookup import TemplateLookup

from mycartable.defaults.configuration import KEEP_UPDATED_CONFIGURATION
from mycartable.types.dtb import DTB
from mycartable.defaults.constantes import (
    ANNOTATION_TEXT_BG_OPACITY,
    MONOSPACED_FONTS,
)
from mycartable.conversion import Grabber
from mycartable.database import getdb
from mycartable.utils import read_qrc
from mycartable import LINUX, WIN
from pony.orm import db_session

from loguru import logger


db = getdb()

MARGINS = {"bottom": 1, "top": 1, "left": 2, "right": 2}
HEADER = {"height": 1}


class Converter:
    def __init__(self, page):
        self.titre = page.titre
        self.id = page.id

    def _export(self, format, ext, open_file=True):
        filename = escaped_filename(self.titre, ext)
        new_file = soffice_convert(self.id, format, filename)
        if open_file:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(new_file)))

    def export_to_pdf(self, **kwargs):
        p = partial(self._export, "pdf:writer_pdf_Export", ".pdf", **kwargs)
        QTimer.singleShot(0, p)

    def export_to_odt(self, **kwargs):
        p = partial(self._export, "odt", ".odt", **kwargs)
        QTimer.singleShot(0, p)


def find_soffice(ui=None):
    if LINUX:
        if Path("/usr/bin/soffice").is_file():
            logger.debug(f"soffice found at '/usr/bin/soffice'")
            return "/usr/bin/soffice"
        else:
            res = (
                subprocess.run(
                    ["which", "soffice"],
                    capture_output=True,
                )
                .stdout.decode()
                .strip()
            )
            if res:
                logger.debug(f"soffice found at {res}")
                return res
    elif WIN:  # pragma: no cover
        if Path("C:\\Program Files\\LibreOffice\\program\\soffice.exe").is_file():
            return "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
        else:
            res = (
                subprocess.run(
                    ["where", "/R", os.environ.get("PROGRAMFILES", ""), "soffice.exe"],
                    capture_output=True,
                )
                .stdout.decode()
                .strip()
            )
            if res:
                logger.debug(f"soffice found at {res}")
                return res
    if ui:
        ui.sendToast.emit("Libreoffice non trouvé sur le système")
    raise EnvironmentError("Libreoffice non trouvé")


def soffice_convert(page_id, format, new_filename, ui=None):
    res = build_odt(page_id)
    ext = "." + format.split(":")[0]
    soffice = find_soffice(ui)
    from mycartable.defaults.files_path import TMP

    temp = QTemporaryFile(str(TMP / uuid.uuid4().hex))
    temp.open()
    p = Path(temp.fileName())
    p.write_bytes(res.encode())
    proc = subprocess.run(
        [soffice, "--headless", "--convert-to", format, str(p)],
        cwd=p.parent,
        capture_output=True,
    )
    converted = p.parent / (p.stem + ext)
    new_path = Path(p.parent, new_filename)
    converted.replace(new_path)
    temp.close()
    return new_path


def escaped_filename(nom, ext):
    nom = (
        nom.replace("é", "e")
        .replace("è", "e")
        .replace("à", "a")
        .replace("ê", "e")
        .replace("â", "a")
        .replace("ç", "c")
        .replace("ù", "u")
    )
    temp = re.sub(r"[\s]", "_", nom.encode("ascii", "ignore").decode("ascii"))
    return re.sub(r"[\W]", "", temp) + ext


@lru_cache
def create_lookup():
    lookup = TemplateLookup()
    import mycartable.qrc

    for file in QDir(":/templates").entryInfoList():
        lookup.put_string(file.fileName(), read_qrc(file.absoluteFilePath()))
    return lookup


def create_images_with_annotation(image_section, tmpdir=None):
    image = QImage()
    painter = QPainter()
    from mycartable.defaults.files_path import FILES

    image.load(str(FILES / image_section["path"]))

    painter.begin(image)
    dtb = DTB()
    for annotation_id in image_section["annotations"]:
        annotation = dtb.getDB("Annotation", annotation_id["id"])
        if annotation["classtype"] == "AnnotationText":
            draw_annotation_text(annotation, image, painter)
        elif annotation["classtype"] == "AnnotationDessin":  # pragma: no branch
            draw_annotation_dessin(annotation, image, painter)

    painter.end()
    if tmpdir:
        new_path = str(Path(tmpdir) / (uuid.uuid4().hex + ".png"))
        image.save(new_path)
        return new_path

    else:
        return image


def draw_annotation_text(annotation: dict, image: QImage, painter: QPainter):
    # d'abord font params
    font = painter.font()
    style = annotation["style"]
    font.setPixelSize(
        image.height()
        / (
            style["pointSize"]
            or KEEP_UPDATED_CONFIGURATION["annotationCurrentTextSizeFactor"]
        )
    )
    font.setUnderline(style["underline"])
    # get considère empty "" comme true
    if not style.get("family", None):  # pragma: no branch
        font_name = DTB().getConfig("fontMain")
        font.setFamily(font_name)  # pragma: no cover
    painter.setFont(font)

    # Ensuite le crayon
    pen = painter.pen()
    pen.setColor(style["fgColor"])
    painter.setPen(pen)

    # On evalue la taille de et la position de l'annotation
    size = painter.fontMetrics().size(0, annotation["text"])
    rect = QRectF(
        QPoint(annotation["x"] * image.width(), annotation["y"] * image.height()),
        QSizeF(size),
    )

    #
    painter.setOpacity(ANNOTATION_TEXT_BG_OPACITY)
    painter.fillRect(rect, style["bgColor"])
    painter.setOpacity(1)

    painter.drawText(
        rect,
        annotation["text"],
    )


def draw_annotation_dessin(annotation: dict, image: QImage, painter: QPainter) -> None:
    style = annotation["style"]
    width = annotation["width"] * image.width()
    height = annotation["height"] * image.height()
    x = annotation["x"] * image.width()
    y = annotation["y"] * image.height()
    sx = annotation["startX"] * width
    ex = annotation["endX"] * width
    sy = annotation["startY"] * height
    ey = annotation["endY"] * height
    pz = style["pointSize"]

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
    pen.setWidth(style["pointSize"] / 2)
    pen.setColor(style["fgColor"])
    painter.setPen(pen)
    painter.setOpacity(0.2 if annotation["tool"] == "fillrect" else 1)
    painter.setOpacity(style["weight"] / 10)
    painter.setRenderHint(QPainter.Antialiasing)
    startPoint = QPoint(x + sx, y + sy)
    endPoint = QPoint(x + ex, y + ey)
    if annotation["tool"] == "trait":
        painter.drawLine(startPoint, endPoint)
    # elif annotation["tool"] == "fillrect":
    #     painter.fillRect(QRect(startPoint, endPoint), annotation["fgColor"])
    elif annotation["tool"] == "rect":
        painter.drawRect(QRect(startPoint, endPoint))
        painter.fillRect(QRect(startPoint, endPoint), style["bgColor"])

    elif annotation["tool"] == "ellipse":  # pragma: no branch
        painter.drawEllipse(QRect(startPoint, endPoint))

    elif annotation["tool"] == "arrow":
        path = QPainterPath()
        path.moveTo(startPoint)
        path.lineTo(endPoint)
        arrowSize = pen.width() * 3
        drawArrowhead(path, startPoint, endPoint, arrowSize)
        painter.fillPath(path, style["fgColor"])
        painter.drawPath(path)

    elif annotation["tool"] == "point":
        points = [
            QPointF(p["x"] * width, p["y"] * height)
            for p in json.loads(annotation["points"])
        ]
        pen = painter.pen()
        pen.setWidth(pen.width() * 4)
        painter.setPen(pen)
        painter.drawPolyline(*points)


def drawArrowhead(path: QPainterPath, depuis: QPoint, to: QPoint, radius: int):
    x_center = to.x()
    y_center = to.y()

    angle: float
    x: float
    y: float

    # path.beginPath()

    angle = math.atan2(to.y() - depuis.y(), to.x() - depuis.x())
    x = radius * math.cos(angle) + x_center
    y = radius * math.sin(angle) + y_center
    point1 = QPoint(x, y)
    path.moveTo(x, y)

    angle += (1.0 / 3.0) * (2 * math.pi)
    x = radius * math.cos(angle) + x_center
    y = radius * math.sin(angle) + y_center
    point2 = QPoint(x, y)
    path.lineTo(x, y)

    angle += (1.0 / 3.0) * (2 * math.pi)
    x = radius * math.cos(angle) + x_center
    y = radius * math.sin(angle) + y_center
    point3 = QPoint(x, y)
    path.lineTo(x, y)
    path.lineTo(point1.x(), point1.y())

    return [point1, point2, point3]


def escape(text):
    tab = "<text:tab/>"
    lb = "<text:line-break/>"
    sp = "<text:s/>"
    return text.replace("\t", tab).replace("\n", lb).replace(" ", sp)


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
    res = res + """/></style:style>"""
    return style_name, res


def span_text(value: NavigableString):
    style_str = value.attrs.get("style", None)
    new_style = None
    if style_str:
        name, new_style = new_automatic_text(style_str)
        span_res = (
            f"""<text:span text:style-name="{name}">{escape(value.text)}</text:span>"""
        )
    else:
        span_res = escape(value.text)
    return span_res, new_style


def new_p(ptag):
    res = [f"""<text:p text:style-name="Standard">"""]
    automatic = []
    for elem in ptag.contents:
        if not elem.name:
            res.append(escape(elem))
        elif elem.name == "span":
            string, style = span_text(elem)
            res.append(string)
            if style:
                automatic.append(style)
    res.append("</text:p>")
    return "".join(res), "\n".join(automatic)


def new_h(htag):
    level = htag.name[-1]
    res = f"""<text:h text:style-name="Heading_20_{level}" text:outline-level="{level}">{escape(htag.text)}</text:h>"""
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


def get_image_size(image):
    margin_horiz = (MARGINS["left"] + MARGINS["right"]) * 10
    margin_vert = (MARGINS["bottom"] + MARGINS["top"] + HEADER["height"]) * 10
    width_mm_dispo = 210 - margin_horiz - 5
    height_mm_dispo = 297 - margin_vert - 5  # 5 = marge de sécurité
    if image.widthMM() > width_mm_dispo:
        # on adapte width si dépasse
        width = width_mm_dispo
        height = image.heightMM() * width_mm_dispo / image.widthMM()
        if height > height_mm_dispo:
            # si pas suffisance pour la hauteur on réadapte les 2
            width = width * height_mm_dispo / height
            height = height_mm_dispo
    elif image.heightMM() > height_mm_dispo:
        # width déà ok, donc on rgèle simplement height
        height = height_mm_dispo
        width = image.widthMM() * height_mm_dispo / image.heightMM()
    else:
        # les 2 sont ok
        width = image.widthMM()
        height = image.heightMM()

    return width, height


def image_section(section_e: "ImageSection") -> Tuple[str, str]:
    section = section_e.to_dict()
    image = create_images_with_annotation(section)
    width, height = get_image_size(image)
    buf = QBuffer()
    buf.open(QBuffer.ReadWrite)
    image.save(buf, "PNG")
    buf.seek(0)
    content = buf.readAll().toBase64()
    buf.close()
    res = f"""<text:p text:style-name="Standard">
<draw:frame draw:style-name="fr1" draw:name="{uuid.uuid4().hex}" text:anchor-type="paragraph" svg:width="{int(width)}mm"  svg:height="{int(height)}mm" draw:z-index="0">
    <draw:image loext:mime-type="image/png">
<office:binary-data>{content.data().decode()}</office:binary-data>
            </draw:image>
        </draw:frame>
    </text:p>"""
    return res, ""


def operation_table_style(section, cell_width=1):
    style_name = f"table-{uuid.uuid4()}"
    total = section.columns * cell_width
    res = f"""<style:style style:name="{style_name}" style:family="table">
    <style:table-properties style:width="{total}cm" fo:margin-top="0.3cm" fo:margin-bottom="0.3cm" 
    table:align="left" style:may-break-between-rows="false"/>
  </style:style>"""
    return style_name, res


def operation_table_style_column(table_style_name, cell_width=1):
    style_name = f"{table_style_name}.Col"
    res = f"""<style:style style:name="{style_name}" style:family="table-column">
    <style:table-column-properties style:column-width="{cell_width}cm"/>
    </style:style>"""
    return style_name, res


def operation_table_style_row(table_style_name):
    style_name = f"{table_style_name}.Row"
    res = f"""<style:style style:name="{style_name}" style:family="table-row">
            <style:table-row-properties fo:background-color="transparent">
                <style:background-image/>
            </style:table-row-properties>
        </style:style>"""
    return style_name, res


def addition_retenue_style_paragraph(table_style_name):
    style_name = f"{table_style_name}_p_retenue"
    res = f"""<style:style style:name="{style_name}" style:family="paragraph" style:parent-style-name="Standard">
   <style:paragraph-properties fo:text-align="center"/>
   <style:text-properties fo:color="#D40020"  fo:font-size="10pt"/>
   </style:style>"""
    return style_name, res


def addition_base_style_paragraph(table_style_name):
    style_name = f"{table_style_name}_p_base"
    res = f"""<style:style style:name="{style_name}" style:family="paragraph" style:parent-style-name="Standard">
    <style:text-properties  fo:font-size="12pt"/>
   <style:paragraph-properties fo:text-align="center"/>
   </style:style>"""
    return style_name, res


def addition_base_style(table_style_name):
    style_name = f"{table_style_name}.A1"
    res = f"""<style:style style:name="{style_name}" style:family="table-cell">
   <style:table-cell-properties fo:padding="0.097cm" fo:border="none"/>
  </style:style>"""
    return style_name, res


def addition_total_style(table_style_name):
    style_name = f"{table_style_name}.A4"
    res = f"""<style:style style:name="{style_name}" style:family="table-cell">
   <style:table-cell-properties fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="1pt solid #000000" fo:border-bottom="none"/>
  </style:style>"""
    return style_name, res


def addition_section(section):
    res = []
    automatic_res = []
    table_style_name, automatic_style = operation_table_style(section)
    automatic_res.append(automatic_style)
    column_style_name, automatic_style = operation_table_style_column(table_style_name)
    automatic_res.append(automatic_style)
    row_style_name, automatic_style = operation_table_style_row(table_style_name)
    automatic_res.append(automatic_style)
    addition_base_style_name, automatic_style = addition_base_style(table_style_name)
    automatic_res.append(automatic_style)
    addition_total_style_name, automatic_style = addition_total_style(table_style_name)
    automatic_res.append(automatic_style)
    addition_retenue_style_name, automatic_style = addition_retenue_style_paragraph(
        table_style_name
    )
    automatic_res.append(automatic_style)
    (
        addition_base_style_name_paragraph,
        automatic_style,
    ) = addition_base_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)

    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_style_name}">
    <table:table-column table:style-name="{column_style_name}" table:number-columns-repeated="{section.columns}"/>"""
    )

    for l in range(section.rows):
        lignes = [f"""<table:table-row  table:style-name="{row_style_name}">"""]
        if l == section.rows - 1:
            cell_style = addition_total_style_name
        else:
            cell_style = addition_base_style_name

        format_cell_style = (
            addition_retenue_style_name
            if l == 0
            else addition_base_style_name_paragraph
        )

        for c in range(section.columns):
            index = l * section.columns + c
            cell = f"""<table:table-cell table:style-name="{cell_style}" office:value-type="string">
              <text:p text:style-name="{format_cell_style}">{section.datas[index]}</text:p>
             </table:table-cell>"""
            lignes.append(cell)
        lignes.append("""</table:table-row>""")
        res.append("\n".join(lignes))

    res.append("""</table:table>""")

    return "\n".join(res), "\n".join(automatic_res)


def soustraction_retenue_gauche_style_paragraph(table_style_name):
    style_name = f"{table_style_name}_p_retenue_gauche"
    res = f"""<style:style style:name="{style_name}" style:family="paragraph" style:parent-style-name="Standard">
   <style:text-properties fo:font-size="12pt" fo:color="#D40020" style:text-position="sub 66%"/>
   <style:paragraph-properties fo:text-align="right"/>
   </style:style>"""
    return style_name, res


def soustraction_retenue_droite_style_paragraph(table_style_name):
    style_name = f"{table_style_name}_p_retenue_droite"
    res = f"""<style:style style:name="{style_name}" style:family="paragraph" style:parent-style-name="Standard">
   <style:text-properties fo:color="#D40020"  fo:font-size="12pt" style:text-position="sub 66%"/>
   <style:paragraph-properties fo:text-align="left"/>
   </style:style>"""
    return style_name, res


def soustraction_section(section):
    res = []
    automatic_res = []
    cell_width = 0.5
    table_style_name, automatic_style = operation_table_style(section, cell_width)
    automatic_res.append(automatic_style)
    column_style_name, automatic_style = operation_table_style_column(
        table_style_name, cell_width
    )
    automatic_res.append(automatic_style)
    row_style_name, automatic_style = operation_table_style_row(table_style_name)
    automatic_res.append(automatic_style)
    addition_base_style_name, automatic_style = addition_base_style(table_style_name)
    automatic_res.append(automatic_style)
    addition_total_style_name, automatic_style = addition_total_style(table_style_name)
    automatic_res.append(automatic_style)
    (
        soustraction_retenue_gauche_style_name,
        automatic_style,
    ) = soustraction_retenue_gauche_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)
    (
        soustraction_retenue_droite_style_name,
        automatic_style,
    ) = soustraction_retenue_droite_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)
    (
        addition_base_style_name_paragraph,
        automatic_style,
    ) = addition_base_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)

    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_style_name}">
        <table:table-column table:style-name="{column_style_name}" table:number-columns-repeated="{section.columns}"/>"""
    )

    for l in range(section.rows):
        lignes = [f"""<table:table-row  table:style-name="{row_style_name}">"""]
        if l == 2:
            cell_style = addition_total_style_name
        else:
            cell_style = addition_base_style_name

        for c in range(section.columns):
            if not section.virgule:
                modulo = (c - 2) % 3
            else:
                modulo = (
                    (c - 2) % 3
                    if c < section.virgule
                    else (c - section.virgule + 1) % 3
                )
            if not c or c == section.virgule:
                format_cell_style = addition_base_style_name_paragraph
            elif modulo == 1:
                format_cell_style = soustraction_retenue_droite_style_name
            elif modulo == 2:
                format_cell_style = soustraction_retenue_gauche_style_name
            else:
                format_cell_style = addition_base_style_name_paragraph

            index = l * section.columns + c
            cell = f"""<table:table-cell table:style-name="{cell_style}" office:value-type="string">
                  <text:p text:style-name="{format_cell_style}">{section.datas[index]}</text:p>
                 </table:table-cell>"""
            lignes.append(cell)
        lignes.append("""</table:table-row>""")
        res.append("\n".join(lignes))

    res.append("""</table:table>""")

    return "\n".join(res), "\n".join(automatic_res)


def multiplication_section(section):
    res = []
    automatic_res = []
    table_style_name, automatic_style = operation_table_style(section)
    automatic_res.append(automatic_style)
    column_style_name, automatic_style = operation_table_style_column(table_style_name)
    automatic_res.append(automatic_style)
    row_style_name, automatic_style = operation_table_style_row(table_style_name)
    automatic_res.append(automatic_style)
    addition_base_style_name, automatic_style = addition_base_style(table_style_name)
    automatic_res.append(automatic_style)
    addition_total_style_name, automatic_style = addition_total_style(table_style_name)
    automatic_res.append(automatic_style)
    addition_retenue_style_name, automatic_style = addition_retenue_style_paragraph(
        table_style_name
    )
    automatic_res.append(automatic_style)
    (
        addition_base_style_name_paragraph,
        automatic_style,
    ) = addition_base_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)

    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_style_name}">
        <table:table-column table:style-name="{column_style_name}" table:number-columns-repeated="{section.columns}"/>"""
    )
    from mycartable.classeur import Section

    q_sec = Section.get(section.id)
    for l in range(section.rows):
        lignes = [f"""<table:table-row  table:style-name="{row_style_name}">"""]
        if l == section.rows - 1 or l == q_sec.model.n_chiffres + 2:
            cell_style = addition_total_style_name
        else:
            cell_style = addition_base_style_name

        format_cell_style = (
            addition_retenue_style_name
            if l < q_sec.model.n_chiffres or l == section.rows - 2
            else addition_base_style_name_paragraph
        )

        for c in range(section.columns):
            index = l * section.columns + c
            cell = f"""<table:table-cell table:style-name="{cell_style}" office:value-type="string">
                  <text:p text:style-name="{format_cell_style}">{section.datas[index]}</text:p>
                 </table:table-cell>"""
            lignes.append(cell)
        lignes.append("""</table:table-row>""")
        res.append("\n".join(lignes))

    res.append("""</table:table>""")

    return "\n".join(res), "\n".join(automatic_res)


def divsion_table_style(section, cell_width, droite_width):
    total = section.columns * cell_width + droite_width
    style_name = f"division-table-{uuid.uuid4()}"
    res = f"""<style:style style:name="{style_name}" style:family="table">
        <style:table-properties style:width="{total}cm" 
        table:align="left" style:may-break-between-rows="false"/>
      </style:style>"""
    return style_name, res


def division_table_style_column_dividende(section, table_style_name, cell_width):
    style_name = f"{table_style_name}.Dividende"
    total = section.columns * cell_width
    res = f"""<style:style style:name="{style_name}" style:family="table-column">
    <style:table-column-properties style:column-width="{total}cm"/>
    </style:style>"""
    return style_name, res


def division_table_style_column_droite(table_style_name, droite_width):
    style_name = f"{table_style_name}.Droite"
    res = f"""<style:style style:name="{style_name}" style:family="table-column">
    <style:table-column-properties style:column-width="{droite_width}cm"/>
    </style:style>"""
    return style_name, res


def division_dividende_style(table_style_name):
    style_name = f"{table_style_name}.CellDividende"
    res = f"""<style:style style:name="{style_name}" style:family="table-cell">
   <style:table-cell-properties fo:padding="0.097cm" fo:border-left="none" fo:border-top="none" fo:border-right="2pt solid #000000" fo:border-bottom="none"/>
  </style:style>"""
    return style_name, res


def division_section(section):
    res = []
    automatic_res = []

    # style de la structure générale
    cell_width = 0.35
    droite_width = 4
    table_division_name_base, automatic_style = divsion_table_style(
        section, cell_width, droite_width
    )
    automatic_res.append(automatic_style)
    dividende_style_name, automatic_style = division_table_style_column_dividende(
        section, table_division_name_base, cell_width
    )
    automatic_res.append(automatic_style)
    droite_style_name, automatic_style = division_table_style_column_droite(
        table_division_name_base, droite_width
    )
    automatic_res.append(automatic_style)
    base_style_name, automatic_style = addition_base_style(table_division_name_base)
    automatic_res.append(automatic_style)
    total_style_name, automatic_style = addition_total_style(table_division_name_base)
    automatic_res.append(automatic_style)
    dividende_style, automatic_style = division_dividende_style(
        table_division_name_base
    )
    automatic_res.append(automatic_style)

    # style du tableau dividende
    table_style_name, automatic_style = operation_table_style(section, cell_width)
    automatic_res.append(automatic_style)
    column_style_name, automatic_style = operation_table_style_column(
        table_style_name, cell_width
    )
    automatic_res.append(automatic_style)
    row_style_name, automatic_style = operation_table_style_row(table_style_name)
    automatic_res.append(automatic_style)
    addition_base_style_name, automatic_style = addition_base_style_paragraph(
        table_style_name
    )
    automatic_res.append(automatic_style)
    # addition_total_style_name, automatic_style = addition_total_style(table_style_name)
    # automatic_res.append(automatic_style)
    (
        soustraction_retenue_gauche_style_name,
        automatic_style,
    ) = soustraction_retenue_gauche_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)
    (
        soustraction_retenue_droite_style_name,
        automatic_style,
    ) = soustraction_retenue_droite_style_paragraph(table_style_name)
    automatic_res.append(automatic_style)

    # debut de structure générale
    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_division_name_base}">
    <table:table-column table:style-name="{dividende_style_name}"/>
    <table:table-column table:style-name="{droite_style_name}"/>
    <table:table-row>
     <table:table-cell table:style-name="{dividende_style}" table:number-rows-spanned="2" office:value-type="string">"""
    )

    # creation du tableau dividende
    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_style_name}">
            <table:table-column table:style-name="{column_style_name}" table:number-columns-repeated="{section.columns}"/>"""
    )
    for l in range(section.rows):
        lignes = [f"""<table:table-row  table:style-name="{row_style_name}">"""]
        if l and not l % 2:
            cell_style = total_style_name
        else:
            cell_style = addition_base_style_name
        # format_cell_style = (
        #     addition_retenue_style_name
        #     if l < section.n_chiffres or l == section.rows - 2
        #     else addition_base_style_name_paragraph
        # )

        for c in range(section.columns):
            modulo = c % 3
            if modulo == 1:
                format_cell_style = addition_base_style_name
            elif modulo == 2:
                format_cell_style = soustraction_retenue_droite_style_name
            else:
                format_cell_style = soustraction_retenue_gauche_style_name
            index = l * section.columns + c
            cell = f"""<table:table-cell table:style-name="{cell_style}" office:value-type="string">
                  <text:p text:style-name="{format_cell_style}">{section.datas[index]}</text:p>
                 </table:table-cell>"""
            lignes.append(cell)
        lignes.append("""</table:table-row>""")
        res.append("\n".join(lignes))
    res.append("""</table:table>""")

    # fin de la structure générale
    res.append(
        f"""</table:table-cell>
     <table:table-cell table:style-name="{base_style_name}" office:value-type="string">
      <text:p text:style-name="{addition_base_style_name}">{section.diviseur}</text:p>
     </table:table-cell>
    </table:table-row>
    <table:table-row>
     <table:covered-table-cell/>
     <table:table-cell table:style-name="{total_style_name}" office:value-type="string">
      <text:p text:style-name="{addition_base_style_name}">{section.quotient}</text:p>
     </table:table-cell>
    </table:table-row>
   </table:table>"""
    )

    return "\n".join(res), "\n".join(automatic_res)


def create_cell(cell: dict, table_style_name):
    style = cell["style"]
    bgcolor = style["bgColor"].name()
    if bgcolor == "#000000":
        bgcolor = "transparent"
    fgcolor = style["fgColor"].name()
    fontsize = style["pointSize"] or 14
    fontsize -= 6  # mieux en papier
    underline = (
        f''' style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"'''
        if style["underline"]
        else ""
    )
    style_name = f"{table_style_name}.{cell['y']}.{cell['x']}"
    auto_style_cell = f"""<style:style style:name="{style_name}" style:family="table-cell">
       <style:table-cell-properties fo:background-color="{bgcolor}" fo:padding="0.097cm" fo:border="1pt solid"/>
      </style:style>"""

    para_name = f"{style_name}.para"
    auto_style_paragraph = f"""<style:style style:name="{para_name}" style:family="paragraph" style:parent-style-name="Standard">
       <style:text-properties fo:font-size="{fontsize}" fo:color="{fgcolor}" {underline} />
       <style:paragraph-properties fo:text-align="left"/>
       </style:style>"""

    new_cell = f"""<table:table-cell table:style-name="{style_name}" office:value-type="string">
                  <text:p text:style-name="{para_name}">{escape(cell["texte"])}</text:p>
                 </table:table-cell>"""
    cell_width = len(cell["texte"]) * fontsize / 28.34646 / 1.55 or 0.4
    cell_height = (1 + cell["texte"].count("\n")) * fontsize / 28.34646 or 2
    return new_cell, auto_style_cell, auto_style_paragraph, cell_width, cell_height


def tableau_style_column(table_style_name, index, width):
    style_name = f"{table_style_name}.Col.{index}"
    res = f"""<style:style style:name="{style_name}" style:family="table-column">
    <style:table-column-properties style:column-width="{width}cm"/>
    </style:style>"""
    return style_name, res


def tableau_style_row(table_style_name, index, width):
    style_name = f"{table_style_name}.Row.{index}"
    res = f"""<style:style style:name="{style_name}" style:family="table-row">
    <style:table-row-properties style:min-row-height="{width}cm"/>
    </style:style>"""
    # <style:table-row-properties style:min-row-height="{width}cm" style:row-height="{width}cm"/>
    return style_name, res


def tableau_table_style(style_name, total):
    res = f"""<style:style style:name="{style_name}" style:family="table">
        <style:table-properties style:width="{total}cm" 
        table:align="left" style:may-break-between-rows="false"/>
      </style:style>"""
    return res


def tableau_section(section):
    res = []
    automatic_res = []
    colonnes_max = {}
    lignes_max = {}
    cells = []
    column_styles = []
    row_styles = []

    # tout d'abord le nom du sytle du tableau
    table_style_name = f"table-{uuid.uuid4()}"

    # on cree les cells en même temps que les style
    for cell in section.get_cells():
        (
            new_cell,
            auto_style_cell,
            auto_style_paragraph,
            cell_width,
            cell_height,
        ) = create_cell(cell, table_style_name)
        colonnes_max[cell["x"]] = max(cell_width, colonnes_max.get(cell["x"], 0))
        lignes_max[cell["y"]] = max(cell_height, lignes_max.get(cell["y"], 0))
        automatic_res.append(auto_style_cell)
        automatic_res.append(auto_style_paragraph)
        cells.append(new_cell)

    # style du tableau général
    table_width = sum(colonnes_max.values())
    tableau_style = tableau_table_style(table_style_name, table_width)
    automatic_res.append(tableau_style)

    # styles des columns
    for index, mx in colonnes_max.items():
        column_style_name, automatic_style = tableau_style_column(
            table_style_name, index, mx
        )
        automatic_res.append(automatic_style)
        column_styles.append(column_style_name)

    # styles des rows
    for index, mx in lignes_max.items():
        row_style_name, automatic_style = tableau_style_row(table_style_name, index, mx)
        automatic_res.append(automatic_style)
        row_styles.append(row_style_name)

    # construction du tableau
    res.append(
        f"""<table:table table:name="{uuid.uuid4()}" table:style-name="{table_style_name}">"""
    )
    for col_style in column_styles:
        res.append(f"""<table:table-column table:style-name="{col_style}"/>""")
    for n, row_style in enumerate(row_styles):
        res.append(f"""<table:table-row  table:style-name="{row_style}">""")
        for i in range(n * section.colonnes, (n + 1) * section.colonnes):
            res.append(cells[i])
        res.append("""</table:table-row>""")
    res.append("""</table:table>""")
    return "\n".join(res), "\n".join(automatic_res)


def equation_section(section):
    font = ""
    for f in QFontDatabase().families():
        if f in MONOSPACED_FONTS:
            font = f
            # break
    if not font:
        raise SystemError("Pas de Font mono retrouvée")

    para_name = f"{uuid.uuid4()}-equation"
    auto_style = f"""<style:style style:name="{para_name}" style:family="paragraph" style:parent-style-name="Standard">
    <style:text-properties style:font-name="{font}" fo:font-size="12pt"/>
    </style:style>"""

    res = (
        f"""<text:p text:style-name="{para_name}">{escape(section.content)}</text:p>"""
    )

    return res, auto_style


def frise_section(section):
    # from . import Section
    #
    # instance = Section.get(section.id)
    return grab_section(section)  # , {"height": instance.height})


class SectionGrabber(Grabber):
    def __init__(self, section: "SectionDatabase", params: dict = {}):
        url = QUrl("qrc:///qml/page/BasePageDelegate.qml")
        self.qq = QQuickItem(width=1200, height=1200)
        from . import Section

        instance = Section.get(section.id)
        sip.transferto(instance, instance)
        base_params = {
            "section": instance,
            "referent": self.qq,
            "index": 1,
            **params,
        }
        super().__init__(url, base_params)
        self.qq.setParent(self)
        instance.setParent(self)


def grab_section(section, initial_prop={}):
    grab = SectionGrabber(section, initial_prop)
    if img := grab():
        return img.to_odf(), ""
    else:
        return "", ""


def build_body(page_id: int) -> Tuple[str, str]:
    tags = []
    automatic_res = []
    from mycartable.database import getdb

    db = getdb()
    page = db.Page[page_id]
    for section in page.content:
        new_tags = ""
        automatic_tags_style = ""
        if section.classtype == "TextSection":
            new_tags, automatic_tags_style = text_section(section)

        elif section.classtype == "ImageSection":
            new_tags, automatic_tags_style = image_section(section)

        elif section.classtype == "AdditionSection":
            new_tags, automatic_tags_style = addition_section(section)

        elif section.classtype == "SoustractionSection":
            new_tags, automatic_tags_style = soustraction_section(section)

        elif section.classtype == "MultiplicationSection":
            new_tags, automatic_tags_style = multiplication_section(section)

        elif section.classtype == "DivisionSection":
            new_tags, automatic_tags_style = division_section(section)

        elif section.classtype == "TableauSection":
            new_tags, automatic_tags_style = tableau_section(section)

        elif section.classtype == "EquationSection":
            new_tags, automatic_tags_style = equation_section(section)

        elif section.classtype == "FriseSection":
            new_tags, automatic_tags_style = frise_section(section)

        if automatic_tags_style:
            automatic_res.append(automatic_tags_style)

        if new_tags:
            tags.append(new_tags)
            tags.append(f"""<text:p text:style-name="Standard"/>""")
    tmpl = create_lookup().get_template("body.xml")
    body = "\n".join(tags)
    return (
        tmpl.render(titre=escape(page.titre), body=body),
        "\n".join(automatic_res),
    )


def build_automatic_styles(automatic_styles: str) -> str:
    tmpl = create_lookup().get_template("automatic-styles.xml")
    return tmpl.render(
        automatic_styles=automatic_styles, margins=MARGINS, header=HEADER
    )


def build_styles() -> str:
    tmpl = create_lookup().get_template("styles.xml")
    return tmpl.render()


def build_master_styles() -> str:
    tmpl = create_lookup().get_template("master-styles.xml")
    db = DTB()
    nom = db.getConfig("nom")
    prenom = db.getConfig("prenom")
    niveau = db.getDB("Annee", db.getConfig("annee"))["niveau"]
    return tmpl.render(nom=nom, prenom=prenom, classe=niveau)


@db_session
def build_odt(page_id: int) -> str:
    body, automatic_data = build_body(page_id)
    automatic_styles = build_automatic_styles(automatic_data)
    master_styles = build_master_styles()
    styles = build_styles()

    tmpl = create_lookup().get_template("base.xml")
    res = tmpl.render(
        body=body,
        automatic_styles=automatic_styles,
        master_styles=master_styles,
        styles=styles,
    )
    return res
