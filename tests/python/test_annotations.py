import json

import pytest

from PySide2.QtCore import Qt, QJsonDocument
from PySide2.QtGui import QColor
from fixtures import check_super_init
from mycartable.types.dtb import DTB
from package.page.annotation_model import AnnotationModel
from pony.orm import db_session


@pytest.fixture
def am(fk, ddbr, dao):
    def factory(nb, genre=None):
        p = fk.f_imageSection()
        a = AnnotationModel()
        a.dao = dao
        a.dtb = DTB()
        annots = []
        if isinstance(genre, tuple):
            for i in genre:
                if i == "t":
                    x = fk.f_annotationText(section=p.id, td=True)
                    annots.append(x)
                elif i == "d":
                    x = fk.f_annotationDessin(section=p.id, td=True)
                    annots.append(x)
        else:
            for i in range(nb):
                x = fk.f_annotationText(section=p.id, td=True)
                annots.append(x)
        a.f_annots = annots
        a.img_id = p.id
        a.sectionId = p.id
        return a

    return factory


class TestAnnotationModel:
    # def test_base_init(self, qtbot, qtmodeltester):
    #     assert check_super_init(
    #         "package.page.page_model.QAbstractListModel", AnnotationModel
    #     )
    #     b = AnnotationModel()
    #     assert b.rowCount() == 0
    #
    #     a = AnnotationModel()
    #     # a._datas = [1, 2, 4]
    #     qtmodeltester.check(a)

    #
    def test_data_role(self, am, qtbot):
        a = am(2)
        # valid index
        assert a.data(a.index(1, 0), a.AnnotationRole) == a.annotations[1]
        # invalid index
        assert a.data(a.index(99, 99), a.AnnotationRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    def test_flags(self, am, qtbot):
        x = am(1)
        assert int(x.flags(x.index(0, 0))) == 128 + 35
        assert x.flags(x.index(99, 99)) is None

    def test_roles(self):
        am = AnnotationModel()
        assert Qt.DisplayRole in am.roleNames()
        assert AnnotationModel.AnnotationRole in am.roleNames()
        assert am.roleNames()[AnnotationModel.AnnotationRole] == b"annot"

    def test_addAnnotation_AnnotationText(self, am, qtbot, fk):
        x = am(2)
        assert x.rowCount() == 2
        # assert x.insertRows(1, 0)

        with qtbot.waitSignal(x.rowsInserted):
            x.addAnnotation(
                "AnnotationText", {"x": 3, "y": 5, "width": 100, "height": 300}
            )
        assert x.annotations[-1]["x"] == 3 / 100
        assert x.rowCount() == 3

    def test_addAnnotation_AnnotationDessin(self, am, qtbot, fk):
        x = am(2)
        x.addAnnotation(
            "AnnotationDessin",
            {
                "endX": 0.9571428571428572,
                "endY": 0.9583333333333334,
                "fillStyle": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 0.000000),
                "height": 0.09473684210526316,
                "lineWidth": 3.0,
                "opacity": 1.0,
                "startX": 0.04285714285714286,
                "startY": 0.041666666666666664,
                "strokeStyle": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 1.000000),
                "tool": "trait",
                "width": 0.08027522935779817,
                "x": 0.24426605504587157,
                "y": 0.2644736842105263,
            },
        )

        assert x.rowCount() == 3
        assert x.annotations[-1]["x"] == 0.24426605504587157

    def test_row_count(self, am):
        a = am(2)
        assert a.rowCount() == 2

    def test_reset(self, fk, am, qtbot):
        a = am(2)
        newAnot = fk.f_annotationDessin(section=a.sectionId, td=True)
        a._reset()
        assert a.rowCount() == 3
        assert newAnot["id"] in [x["id"] for x in a.annotations]

    def test_remove(self, am, ddbr, qtbot):
        a = am(3)
        ids = [anot["id"] for anot in a.annotations]
        assert a.remove(0)
        assert a.rowCount() == 2

        assert a.data(a.index(0, 0), a.AnnotationRole)["id"] in ids
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] in ids

    def test_setData(self, am, qtbot, ddbr):
        a = am(3)
        a0 = str(a.f_annots[0]["id"])
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
            assert ddbr.AnnotationText[a0].text == "blabla"

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
            assert ddbr.AnnotationText[a0].text == "blabla"

    def test_set_data_select_right_class_annotation(self, am, ddbr):
        a = am(1, ("d",))
        a0 = str(a.f_annots[0]["id"])
        assert a.setData(
            a.index(0, 0),
            QJsonDocument.fromJson(json.dumps({"id": a0, "width": 23}).encode()),
            Qt.EditRole,
        )
        with db_session:
            assert ddbr.AnnotationDessin[a0].width == 23

    def test_modif_update_recents_and_activites(self, qtbot, am):
        a = am(3)

        with qtbot.waitSignal(a.dao.updateRecentsAndActivites):
            a.removeRow(0)

        with qtbot.waitSignal(a.dao.updateRecentsAndActivites):
            a.insertRow(0)
