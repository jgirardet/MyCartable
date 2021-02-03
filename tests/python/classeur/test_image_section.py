import shutil
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from PyQt5.QtCore import QPointF, Qt, QUrl
from PyQt5.QtGui import QColor, QImage, QCursor
from PyQt5.QtQuick import QQuickItem
from PyQt5.QtWidgets import QUndoStack
from mycartable.classeur.sections.annotation import AnnotationModel
from mycartable.defaults.configuration import KEEP_UPDATED_CONFIGURATION
from mycartable.types import DTB
from mycartable.classeur import ImageSection, Page, Classeur
from mycartable.cursors import build_one_image_cursor
from mycartable.defaults.files_path import FILES
from pony.orm import db_session


@pytest.mark.freeze_time("2344-9-21 7:48:5")
@patch(
    "mycartable.utils.uuid.uuid4",
    new=lambda: uuid.UUID("d9ca35e1-0b4b-4d42-9f0d-aa07f5dbf1a5"),
)
def test_new_Image(fk, resources, bridge):
    img = resources / "sc1.png"
    p = fk.f_page()
    DTB().setConfig("annee", 2011)
    # with Path
    image = ImageSection.new(parent=bridge, **{"page": p.id, "path": img})
    assert image.path == "2011/2344-09-21-07-48-05-d9ca3.png"
    # with QUrl
    image = ImageSection.new(
        parent=bridge, **{"page": p.id, "path": QUrl.fromLocalFile(str(img.resolve()))}
    )
    assert image.path == "2011/2344-09-21-07-48-05-d9ca3.png"
    # file no existe
    image = ImageSection.new(
        parent=bridge, **{"page": p.id, "path": QUrl.fromLocalFile("/aa/ff")}
    )
    assert image is None
    # file no path
    image = ImageSection.new(parent=bridge, **{"page": p.id})
    assert image is None


@pytest.mark.freeze_time("2344-9-21 7:48:5")
@patch(
    "mycartable.utils.uuid.uuid4",
    new=lambda: uuid.UUID("d9ca35e1-0b4b-4d42-9f0d-aa07f5dbf1a5"),
)
def test_new_ImageVide(fk, resources):
    img = resources / "sc1.png"
    p = fk.f_page()
    DTB().setConfig("annee", 2011)
    image = ImageSection.new(
        parent=None,
        undoStack=QUndoStack(),
        **{"page": p.id, "width": 40, "height": 400, "classtype": "ImageSectionVide"}
    )
    assert image.path == "2011/2344-09-21-07-48-05-d9ca3.png"
    im = Image.open(image.absolute_path)
    assert im.height == 400
    assert im.width == 40


# def test_check_args():
# check_args(ImageSection.pivoterImage, [int], bool)


def test_absolute_path_qmlpath_path(fk):
    i = fk.f_imageSection(td=True)
    img = ImageSection.get(i, parent=None, undoStack=QUndoStack())
    assert img.path == i["path"]
    assert img.absolute_path == FILES / i["path"]
    assert img.url == QUrl.fromLocalFile(str(Path(img.absolute_path).absolute()))


def test_model(fk):
    i = fk.f_imageSection(td=True)
    img = ImageSection.get(i, parent=None, undoStack=QUndoStack())
    assert isinstance(img.model, AnnotationModel)


@pytest.mark.freeze_time("2344-9-21 7:48:5")
def test_new_image_path(fk):
    with patch(
        "mycartable.utils.uuid.uuid4",
        new=lambda: uuid.UUID("d9ca35e1-0b4b-4d42-9f0d-aa07f5dbf1a5"),
    ):
        with db_session:
            fk.db.Configuration.add("annee", 2019)
        assert (
            ImageSection.get_new_image_path(".jpg")
            == "2019/2344-09-21-07-48-05-d9ca3.jpg"
        )

        with db_session:
            fk.db.Configuration.add("annee", 2018)
        assert (
            ImageSection.get_new_image_path(".gif")
            == "2018/2344-09-21-07-48-05-d9ca3.gif"
        )


@pytest.mark.parametrize(
    "name, new_value",
    [
        ("annotationCurrentTool", "new_tool"),
        ("annotationDessinCurrentLineWidth", "99"),
        ("annotationDessinCurrentTool", "new_tool"),
    ],
)
def test_annotation_properties(fk, bridge, qtbot, name, new_value):
    i = fk.f_imageSection(td=True)
    img = ImageSection.get(i, parent=bridge)
    assert getattr(img, name) == KEEP_UPDATED_CONFIGURATION[name]
    setattr(img, name, new_value)
    with db_session:
        assert fk.db.Configuration.option(name) == new_value


@pytest.mark.parametrize(
    "name, new_value",
    [
        ("annotationDessinCurrentStrokeStyle", QColor("purple")),
    ],
)
def test_annotation_propertiesQColor(fk, bridge, qtbot, name, new_value):
    i = fk.f_imageSection(td=True)
    img = ImageSection.get(
        i,
        parent=bridge,
    )
    assert getattr(img, name).name() == KEEP_UPDATED_CONFIGURATION[name]
    setattr(img, name, new_value)
    with db_session:
        assert fk.db.Configuration.option(name) == new_value.name()


def test_store_new_file_pathlib(resources):
    obj = resources / "sc1.png"
    res = ImageSection.store_new_file(obj)
    assert (FILES / res).read_bytes() == obj.read_bytes()


def test_store_new_file_str(resources):
    obj = resources / "sc1.png"
    res = ImageSection.store_new_file(str(obj))
    assert (FILES / res).read_bytes() == obj.read_bytes()


def test_create_empty_image():
    res = ImageSection.create_empty_image(300, 500)
    im = Image.new("RGBA", (300, 500), "white")
    saved = Image.open(FILES / res)
    assert list(im.getdata()) == list(saved.getdata())


def test_pivoter_image(new_res, fk, qtbot, bridge):
    file = new_res("test_pivoter.png")
    img = Image.open(file)
    assert img.height == 124
    assert img.width == 673

    f = fk.f_imageSection(path=str(file))
    p = Page.get(f.page.id, parent=bridge)
    isec = p.get_section(0)
    isec.pivoterImage(1)
    img = Image.open(file)
    assert img.height == 673
    assert img.width == 124
    assert p.undoStack.undoText() == "pivoter"

    with qtbot.waitSignal(isec.commandDone):
        p.undoStack.undo()
    img = Image.open(file)
    assert img.height == 124
    assert img.width == 673
    with qtbot.waitSignal(isec.commandDone):
        p.undoStack.redo()
    img = Image.open(file)
    assert img.height == 673
    assert img.width == 124


trait_600_600 = "data:image/png;base64,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"
trait_600_600_as_png = "2019/2019-05-21-12-00-01-349bd.png"


def test_annotationTextBGOpacity(fk, bridge):
    isec = ImageSection.get(fk.f_imageSection().id, parent=bridge)
    assert isec.annotationTextBGOpacity == 0.5


@pytest.mark.parametrize(
    "pos, img_res",
    [
        (QPointF(0.10, 0.10), "floodfill_blanc_en_bleu.png"),
        (QPointF(0.80, 0.80), "floodfill_rouge_en_bleu.png"),
    ],
)
def test_flood_fill(fk, resources, qtbot, tmp_path, pos, img_res, bridge):
    fp = tmp_path / "f1.png"
    shutil.copy(resources / "floodfill.png", fp)
    f = fk.f_imageSection(path=str(fp))
    p = Page.get(f.page.id, parent=bridge)
    isec = p.get_section(0)
    isec.floodFill(QColor("blue"), pos)
    lhs = QImage(str(isec.absolute_path))
    rhs = QImage(str(resources / img_res))
    assert lhs == rhs
    assert p.undoStack.undoText() == "remplir"
    with qtbot.waitSignal(isec.commandDone):
        p.undoStack.undo()
    lhs = QImage(str(isec.absolute_path))
    rhs = QImage(str(fp))
    assert lhs == rhs
    with qtbot.waitSignal(isec.commandDone):
        p.undoStack.redo()
    lhs = QImage(str(isec.absolute_path))
    rhs = QImage(str(resources / img_res))
    assert lhs == rhs


def test_image_selection_curosr(fk, bridge, qtbot):
    qk = QQuickItem()
    isec = ImageSection.get(fk.f_imageSection().id, parent=bridge)
    # defaut
    isec.setImageSectionCursor(qk, "text", QColor("black"))
    assert (
        qk.cursor().pixmap().toImage()
        == build_one_image_cursor("text").pixmap().toImage()
    )
    # color
    isec.setImageSectionCursor(qk, "text", QColor("blue"))
    assert (
        qk.cursor().pixmap().toImage()
        == build_one_image_cursor("text", QColor("blue")).pixmap().toImage()
    )

    # with tool
    isec.setImageSectionCursor(qk, "fillrect", QColor("red"))
    assert (
        qk.cursor().pixmap().toImage()
        == build_one_image_cursor("fillrect", QColor("red")).pixmap().toImage()
    )

    # default
    isec.setImageSectionCursor(qk, "default", "black")
    assert qk.cursor() == QCursor(Qt.ArrowCursor)

    # dragmove
    isec.setImageSectionCursor(qk, "dragmove", "black")
    assert qk.cursor() == QCursor(Qt.DragMoveCursor)
