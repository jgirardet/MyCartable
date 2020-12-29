import json

import pytest

from PySide2.QtCore import QByteArray
from PySide2.QtGui import QColor
from mycartable.default_configuration import KEEP_UPDATED_CONFIGURATION
from tests.python.fixtures import disable_log
from mycartable.classeur import (
    Annotation,
    AnnotationText,
    AnnotationDessin,
    ImageSection,
)
from mycartable.classeur.sections.annotation import AnnotationModel

from pony.orm import db_session

sub_classes = (Annotation, AnnotationText, AnnotationDessin)


class TestAnnotation:
    def test_subclassing(self, fk):
        ac = fk.f_section()
        x = Annotation.new(section=ac.id, x=0.2, y=0.3, classtype="Annotation")
        assert x is not None
        y = Annotation.get(x.id)
        assert y is not None
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert Annotation.get(y.id) is None

    def test_sytlable_subtypeable(self, fk):
        # subtypable
        ac = fk.f_annotationText()
        x = Annotation.get(ac.id)
        assert x.classtype == "AnnotationText"
        ac = fk.f_annotationDessin()
        x = Annotation.get(ac.id)
        assert x.classtype == "AnnotationDessin"

        # styalable
        ac = fk.f_annotationDessin()
        x = Annotation.get(ac.id)
        x.bgColor == ""
        hasattr(x, "underline")

    def test_properties(self, fk, qtbot):
        anx = fk.f_annotation(x=0.2, y=0.3, td=True)
        an = Annotation.get(anx["id"])
        assert an.x == 0.2
        assert an.y == 0.3
        with qtbot.waitSignal(an.xChanged):
            an.x = 0.5

        with qtbot.waitSignal(an.yChanged):
            an.y = 0.7

        with db_session:
            item = fk.db.Annotation[an.id]
            assert item.x == 0.5
            assert item.y == 0.7

    def test_available_subclasses(self):
        assert Annotation.available_subclass() == sub_classes

    @pytest.mark.parametrize(
        "_class",
        sub_classes,
    )
    def test_get_class(self, fk, _class):
        f_name = "f_" + _class.entity_name[0].lower() + _class.entity_name[1:]
        a = getattr(fk, f_name)(td=True)
        s = Annotation.get(a["id"])
        assert a == s._data
        assert s.classtype == _class.entity_name
        assert isinstance(s, _class)


class TestAnnotationText:
    def test_subclassing(self, fk):
        ac = fk.f_section()
        x = AnnotationText.new(
            section=ac.id, x=0.2, y=0.3, text="a", classtype="AnnotationText"
        )
        y = AnnotationText.get(x.id)
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert AnnotationText.get(y.id) is None

    def test_properties(self, fk, qtbot):
        anx = fk.f_annotationText(text="aa")
        an = AnnotationText.get(anx.id)
        assert an.text == "aa"
        with qtbot.waitSignal(an.textChanged):
            an.text = "text"
        with db_session:
            item = fk.db.AnnotationText[an.id]
            assert item.text == "text"

    def test_annotationCurrentTextSizeFactor(self, fk, qtbot):
        anx = fk.f_annotationText(text="aa")
        an = AnnotationText.get(anx.id)
        assert (
            an.annotationCurrentTextSizeFactor
            == KEEP_UPDATED_CONFIGURATION["annotationCurrentTextSizeFactor"]
        )


class TestAnnotationDessin:
    def test_subclassing(self, fk):
        ac = fk.f_section()
        x = AnnotationDessin.new(
            **{
                "x": 0.3,
                "y": 0.6,
                "width": 0.8,
                "height": 0.7,
                "tool": "rect",
                "startX": 0.4,
                "startY": 0.8,
                "endX": 0.1,
                "endY": 0.3,
                "section": ac.id,
            }
        )
        y = AnnotationDessin.get(x.id)
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert AnnotationDessin.get(y.id) is None

    def test_properties(self, fk, qtbot):
        ac = fk.f_section()
        prop_before = {
            "x": 0.3,
            "y": 0.6,
            "width": 0.8,
            "height": 0.7,
            "tool": "rect",
            "startX": 0.4,
            "startY": 0.8,
            "endX": 0.1,
            "endY": 0.3,
            "points": json.dumps([{"x": 1, "y": 2}]),
        }
        prop_after = {
            "x": 0.1,
            "y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "tool": "trait",
            "startX": 0.5,
            "startY": 0.6,
            "endX": 0.7,
            "endY": 0.8,
            "points": [{"x": 3, "y": 4}],
        }
        an = AnnotationDessin.new(**{"section": ac.id, **prop_before})

        for k, v in prop_before.items():
            if k == "points":
                v = json.loads(v)
            assert getattr(an, k) == v
        for k, v in prop_after.items():
            with qtbot.waitSignal(getattr(an, k + "Changed")):
                setattr(an, k, v)
        with db_session:
            item = fk.db.AnnotationDessin[an.id]
            for k, v in prop_after.items():
                if k == "points":
                    v = json.dumps(v)
                assert getattr(item, k) == v


@pytest.fixture
def am(fk):
    def factory(nb):
        p = fk.f_imageSection()
        annots = []
        if isinstance(nb, int):
            for i in range(nb):
                x = fk.f_annotationText(section=p.id, td=True)
                annots.append(x)
        else:
            for i in nb:
                if i == "t":
                    x = fk.f_annotationText(section=p.id, td=True)
                    annots.append(x)
                elif i == "d":
                    x = fk.f_annotationDessin(section=p.id, td=True)
                    annots.append(x)

        a = ImageSection.get(p.id)
        a.f_annots = annots
        return a

    return factory


class TestAnnotationModel:
    def test__init__et_reset(self, am):
        s = am(3)
        a = AnnotationModel(s)
        ids = [b["id"] for b in s.f_annots]
        assert sorted([w.id for w in a._data]) == sorted(ids)

    def test__rowCount(self, am):
        s = am(3)
        a = AnnotationModel(s)
        assert a.rowCount() == 3

    def test_roleNames(self, am):
        s = am(0)
        a = AnnotationModel(s)
        assert AnnotationModel.AnnotationRole in a.roleNames()
        assert a.roleNames()[AnnotationModel.AnnotationRole] == QByteArray(
            b"annotation"
        )

    def test_data(self, am):
        s = am(("t", "t", "d"))
        a = AnnotationModel(s)
        # valid indexes
        for i in range(3):
            assert a.data(a.index(i, 0), a.AnnotationRole) == a._data[i]
        # invalid index
        assert a.data(a.index(99, 99), a.AnnotationRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    @pytest.mark.parametrize(
        "removed, zero, un",
        [
            (0, 1, 2),
            (1, 0, 2),
            (2, 0, 1),
        ],
    )
    def test_removeRows(self, am, ddbr, removed, zero, un):
        s = am(3)
        a = AnnotationModel(s)

        ids = [anot.id for anot in a._data]
        assert a.remove(removed)
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.AnnotationRole).id == ids[zero]
        assert a.data(a.index(1, 0), a.AnnotationRole).id == ids[un]

    # def test_insertRows(self, am):
    #     s = am(3)
    #     a = AnnotationModel(s)
    #     ids = [anot.id for anot in a._data]
    #     a._reset = MagicMock()
    #     a.insertRow(0)
    #     assert a._reset.called

    def test_addAnnotation_AnnotationText(self, am, qtbot, fk):
        s = am(2)
        x = AnnotationModel(s)
        assert x.rowCount() == 2
        # assert x.insertRows(1, 0)

        with qtbot.waitSignal(x.rowsInserted):
            x.addAnnotation(
                "AnnotationText", {"x": 3, "y": 5, "width": 100, "height": 300}
            )

        assert x._data[-1].x == 3 / 100
        assert x.rowCount() == 3

    def test_addAnnotation_AnnotationDessin(self, am, qtbot, fk):
        s = am(2)
        x = AnnotationModel(s)
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
        assert x._data[-1].x == 0.24426605504587157

    def test_addAnnotation_Rien(self, am, qtbot, fk):
        s = am(2)
        x = AnnotationModel(s)
        x.addAnnotation(
            "Bla",
            {},
        )

        assert x.rowCount() == 2
        # assert x._data[-1].x == 0.24426605504587157

    #
    # def test_setData(self, am, qtbot, ddbr):
    #     a = am(3)
    #     a0 = str(a.f_annots[0]["id"])
    #     # ok to set
    #     with qtbot.waitSignal(a.dataChanged):
    #         assert a.setData(
    #             a.index(0, 0),
    #             QJsonDocument.fromJson(
    #                 json.dumps({"id": a0, "text": "blabla"}).encode()
    #             ),
    #             Qt.EditRole,
    #         )
    #     with db_session:
    #         assert ddbr.AnnotationText[a0].text == "blabla"
    #
    #     # wrong index
    #     with qtbot.assert_not_emitted(a.dataChanged):
    #         assert not a.setData(
    #             a.index(0, 99),
    #             QJsonDocument.fromJson(
    #                 json.dumps({"id": a0, "text": "bleble"}).encode()
    #             ),
    #             Qt.EditRole,
    #         )
    #     with db_session:
    #         assert ddbr.AnnotationText[a0].text == "blabla"
    #
    # def test_set_data_select_right_class_annotation(self, am, ddbr):
    #     a = am(1, ("d",))
    #     a0 = str(a.f_annots[0]["id"])
    #     assert a.setData(
    #         a.index(0, 0),
    #         QJsonDocument.fromJson(json.dumps({"id": a0, "width": 23}).encode()),
    #         Qt.EditRole,
    #     )
    #     with db_session:
    #         assert ddbr.AnnotationDessin[a0].width == 23
    #
    # def test_modif_update_recents_and_activites(self, qtbot, am):
    #     a = am(3)
    #
    #     with qtbot.waitSignal(a.dao.updateRecentsAndActivites):
    #         a.removeRow(0)
    #
    #     with qtbot.waitSignal(a.dao.updateRecentsAndActivites):
    #         a.insertRow(0)
