import json

import pytest

from PySide2.QtCore import Qt, QModelIndex, QJsonDocument
from PySide2.QtGui import QColor
from fixtures import check_super_init
from factory import (
    f_annotationText,
    f_annotationDessin,
    f_imageSection,
)
from package.database.sections import AnnotationText, ImageSection, AnnotationDessin
from package.page.annotation_model import AnnotationModel
from pony.orm import db_session
from pony.orm.core import EntityProxy

from fixtures import check_args


@pytest.fixture
def am(ddbr):
    def factory(nb, genre=None):
        p = f_imageSection()
        a = AnnotationModel()
        annots = []
        if isinstance(genre, tuple):
            for i in genre:
                if i == "t":
                    x = f_annotationText(section=p.id)
                    annots.append(x)
                elif i == "d":
                    x = f_annotationDessin(section=p.id)
                    annots.append(x)
        else:
            for i in range(nb):
                x = f_annotationText(section=p.id)
                annots.append(x)
        a.f_annots = annots
        a.img_id = p.id
        a.sectionId = p.id

        return a

    return factory


class TestAnnotationModel:
    def test_base_init(self, qtbot, qtmodeltester):
        assert check_super_init(
            "package.page.page_model.QAbstractListModel", AnnotationModel
        )
        b = AnnotationModel()
        assert b.row_count == 0

        a = AnnotationModel()
        # a._datas = [1, 2, 4]
        qtmodeltester.check(a)

    #
    def test_data_role(self, am, qtbot):
        a = am(2)
        # valid index
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[1].id)
        # invalid index
        assert a.data(a.index(99, 99), a.AnnotationRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    def test_flags(self, am, qtbot):
        x = am(1)
        assert int(x.flags(x.index(0, 0))) == 128 + 35
        assert x.flags(x.index(99, 99)) is None

    def test_insertRows_and_row(self, am, qtbot):
        x = am(2)
        assert x.rowCount() == 2

        f_annotationText(section=x.sectionId)
        assert x.insertRows(1, 0)
        assert x.rowCount() == 3

        f_annotationText(section=x.sectionId)
        assert x.insertRow(1)
        assert x.rowCount() == 4

    def test_roles(self):
        am = AnnotationModel()
        assert Qt.DisplayRole in am.roleNames()
        assert AnnotationModel.AnnotationRole in am.roleNames()
        assert am.roleNames()[AnnotationModel.AnnotationRole] == b"annot"

    def test_row_count(self, am):
        a = am(2)
        assert a.rowCount() == a.row_count == a.count == 2

    def test_count(self, am, qtbot):
        a = am(1)
        with qtbot.waitSignal(a.countChanged):
            a.count = 3
        assert a.rowCount() == a.row_count == a.count == 3

    def test_sloot_reset(self, ddbr, qtbot):
        a = AnnotationModel()

        # section does not exists
        with qtbot.waitSignal(a.modelReset):
            assert a.slotReset(99) is None
            assert a.section is None
            assert a.sectionId == 0

        f = f_imageSection()
        f_annotationDessin(section=f.id)
        with qtbot.waitSignal(a.modelReset):
            assert a.slotReset(f.id)

        with db_session:
            assert a.section.id == f.id
            assert isinstance(a.section, EntityProxy)
            assert a.sectionId == f.id
            assert a.count == 1

    def test_removeRows_at_0(self, am, ddbr, qtbot):
        a = am(3)

        assert a.removeRows(0, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == str(a.f_annots[1].id)
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[2].id)

    def test_removeRows_at_1(self, am, ddbr, qtbot):
        a = am(3)

        assert a.removeRows(1, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == str(a.f_annots[0].id)
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[2].id)

    def test_removeRows_at_end(self, am, ddbr, qtbot):
        a = am(3)

        assert a.removeRows(2, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == str(a.f_annots[0].id)
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[1].id)

    def test_removeRow(self, am, ddbr, qtbot):
        a = am(3)
        assert a.removeRow(0)
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == str(a.f_annots[1].id)
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[2].id)

    def test_removeRow_by_id(self, am, ddbr, qtbot):
        a = am(3)
        assert a.removeRow(str(a.f_annots[1].id), True)
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == str(a.f_annots[0].id)
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == str(a.f_annots[2].id)

    def test_setData(self, am, qtbot):
        a = am(3)
        a0 = str(a.f_annots[0].id)
        # ok to set
        with qtbot.waitSignal(a.dataChanged):
            assert a.setData(
                a.index(0, 0),
                QJsonDocument.fromJson(
                    json.dumps({"id": a0, "text": "blabla"}).encode()
                ),
                Qt.EditRole,
            )
        with db_session:
            assert AnnotationText[a0].text == "blabla"

        # wrong index
        with qtbot.assert_not_emitted(a.dataChanged):
            assert not a.setData(
                a.index(0, 99),
                QJsonDocument.fromJson(
                    json.dumps({"id": a0, "text": "bleble"}).encode()
                ),
                Qt.EditRole,
            )
        with db_session:
            assert AnnotationText[a0].text == "blabla"

    def test_set_data_select_right_class_annotation(self, am):
        a = am(1, ("d",))
        a0 = str(a.f_annots[0].id)
        assert a.setData(
            a.index(0, 0),
            QJsonDocument.fromJson(json.dumps({"id": a0, "width": 23}).encode()),
            Qt.EditRole,
        )
        with db_session:
            assert AnnotationDessin[a0].width == 23

    def test_modif_update_recents_and_activites(self, qtbot, am, qapp):
        a = am(3)

        with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
            a.removeRow(0)

        with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
            a.insertRow(0)

    def test_addannotation(self, am, qtbot):
        a = am(1)
        check_args(a.addAnnotation, [float, float, float, float])
        with qtbot.waitSignal(a.rowsInserted):
            a.addAnnotation(0.1, 0.2, 0.3, 0.4)
        with db_session:
            a1 = AnnotationText.select()[1:][0]
            assert a1.to_dict() == {
                "bgColor": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 0.000000),
                "classtype": "AnnotationText",
                "family": "",
                "fgColor": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 1.000000),
                "id": str(a1.id),
                "pointSize": None,
                "section": ImageSection[a.img_id],
                "strikeout": False,
                "styleId": 2,
                "text": None,
                "underline": False,
                "weight": None,
                "x": 0.1 / 0.3,
                "y": 0.5,
            }

    def test_newDessin(self, am, qtbot):
        a = am(1)
        check_args(a.newDessin, dict)
        with qtbot.waitSignal(a.rowsInserted):
            a.newDessin(
                {
                    "fillStyle": QColor("yellow"),
                    "strokeStyle": QColor("purple"),
                    "lineWidth": 3,
                    "x": 0.1,
                    "y": 0.5,
                    "width": 0.3,
                    "height": 0.4,
                    "tool": "trait",
                    "startX": 0.8,
                    "startY": 0.9,
                    "endX": 0.9,
                    "endY": 0.95,
                    "opacity": 1,
                }
            )

        with db_session:
            a1 = AnnotationDessin.select().first()
            assert a1.to_dict() == {
                "bgColor": QColor("yellow"),
                "classtype": "AnnotationDessin",
                "family": "",
                "fgColor": QColor("purple"),
                "id": str(a1.id),
                "section": ImageSection[a.img_id],
                "strikeout": False,
                "styleId": 2,
                "underline": False,
                "weight": 10,
                "pointSize": 3.0,
                "x": 0.1,
                "y": 0.5,
                "width": 0.3,
                "height": 0.4,
                "tool": "trait",
                "startX": 0.8,
                "startY": 0.9,
                "endX": 0.9,
                "endY": 0.95,
            }
