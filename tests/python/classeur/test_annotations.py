import json

import pytest

from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QColor
from mycartable.defaults.configuration import KEEP_UPDATED_CONFIGURATION
from mycartable.defaults.roles import AnnotationRole
from tests.python.fixtures import disable_log
from mycartable.classeur import (
    Annotation,
    AnnotationText,
    AnnotationDessin,
    Page,
)
from mycartable.classeur.sections.annotation import (
    AnnotationModel,
    RemoveAnnotationCommand,
    SetAnnotationCommand,
)

from pony.orm import db_session

sub_classes = (Annotation, AnnotationText, AnnotationDessin)


class TestAnnotation:
    def test_subclassing(self, fk, bridge):
        ac = fk.f_section()
        x = Annotation.new(
            section=ac.id, x=0.2, y=0.3, classtype="Annotation", parent=bridge
        )
        assert x is not None
        y = Annotation.get(x.id, parent=bridge)
        assert y is not None
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert Annotation.get(y.id, parent=bridge) is None

    def test_sytlable_subtypeable(self, fk, bridge):
        # subtypable
        ac = fk.f_annotationText()
        x = Annotation.get(ac.id, parent=bridge)
        assert x.classtype == "AnnotationText"
        ac = fk.f_annotationDessin()
        x = Annotation.get(ac.id, parent=bridge)
        assert x.classtype == "AnnotationDessin"

        # styalable
        ac = fk.f_annotationDessin()
        x = Annotation.get(ac.id, parent=bridge)
        x.bgColor == ""
        hasattr(x, "underline")

    def test_properties(self, fk, bridge, qtbot):
        anx = fk.f_annotation(x=0.2, y=0.3, td=True)
        an = Annotation.get(anx["id"], parent=bridge)
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
    def test_get_class(self, fk, bridge, _class):
        f_name = "f_" + _class.entity_name[0].lower() + _class.entity_name[1:]
        a = getattr(fk, f_name)(td=True)
        s = Annotation.get(a["id"], parent=bridge)
        assert a == s._data
        assert s.classtype == _class.entity_name
        assert isinstance(s, _class)


class TestAnnotationText:
    def test_subclassing(self, fk, bridge):
        ac = fk.f_section()
        x = AnnotationText.new(
            section=ac.id,
            x=0.2,
            y=0.3,
            text="a",
            classtype="AnnotationText",
            parent=bridge,
        )
        y = AnnotationText.get(x.id, parent=bridge)
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert AnnotationText.get(y.id, parent=bridge) is None

    def test_properties(self, fk, bridge, qtbot):
        anx = fk.f_annotationText(text="aa")
        an = AnnotationText.get(anx.id, parent=bridge)
        assert an.text == "aa"
        with qtbot.waitSignal(an.textChanged):
            an.text = "text"
        with db_session:
            item = fk.db.AnnotationText[an.id]
            assert item.text == "text"

    def test_annotationCurrentTextSizeFactor(self, fk, bridge, qtbot):
        anx = fk.f_annotationText(text="aa")
        an = AnnotationText.get(anx.id, parent=bridge)
        assert (
            an.annotationCurrentTextSizeFactor
            == KEEP_UPDATED_CONFIGURATION["annotationCurrentTextSizeFactor"]
        )


class TestAnnotationDessin:
    def test_subclassing(self, fk, bridge):
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
            },
            parent=bridge
        )
        y = AnnotationDessin.get(x.id, parent=bridge)
        assert x == y
        assert x.delete()
        with disable_log("mycartable.types.dtb"):
            assert AnnotationDessin.get(y.id, parent=bridge) is None

    def test_properties(self, fk, bridge, qtbot):
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
        an = AnnotationDessin.new(**{"section": ac.id, **prop_before}, parent=bridge)

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
def am(fk, bridge):
    def factory(nb):
        page = fk.f_page()
        p = fk.f_imageSection(page=page.id)
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
        pageobj = Page.get(page.id, parent=bridge)
        a = pageobj.get_section(0)
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
        assert AnnotationRole in a.roleNames()
        assert a.roleNames()[AnnotationRole] == QByteArray(b"annotation")

    def test_data(self, am):
        s = am(("t", "t", "d"))
        a = AnnotationModel(s)
        # valid indexes
        for i in range(3):
            assert a.data(a.index(i, 0), AnnotationRole) == a._data[i]
        # invalid index
        assert a.data(a.index(99, 99), AnnotationRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    @pytest.mark.parametrize("genre", ["t", "d"])
    @pytest.mark.parametrize(
        "removed, zero, un",
        [
            (0, 1, 2),
            (1, 0, 2),
            (2, 0, 1),
        ],
    )
    def test_removeRows(self, am, ddbr, removed, zero, un, genre):
        s = am([genre, genre, genre])
        a = s.model
        ids = [anot.id for anot in a._data]
        a.remove(removed)
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), AnnotationRole).id == ids[zero]
        assert a.data(a.index(1, 0), AnnotationRole).id == ids[un]

        s.undoStack.undo()
        assert a.rowCount() == 3
        assert a.data(a.index(0, 0), AnnotationRole).id == ids[0]
        assert a.data(a.index(1, 0), AnnotationRole).id == ids[1]
        assert a.data(a.index(2, 0), AnnotationRole).id == ids[2]

        s.undoStack.redo()
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), AnnotationRole).id == ids[zero]
        assert a.data(a.index(1, 0), AnnotationRole).id == ids[un]

    def test_addAnnotation_AnnotationText(self, am, qtbot, fk):
        s = am(2)
        x = s.model
        assert x.rowCount() == 2

        with qtbot.waitSignal(x.rowsInserted):
            x.addAnnotation(
                "AnnotationText", {"x": 3, "y": 5, "width": 100, "height": 300}
            )

        assert x._data[-1].x == 3 / 100
        assert x.rowCount() == 3
        new_annot = x.data(x.index(2, 0), AnnotationRole)
        old_annot = x.data(x.index(0, 0), AnnotationRole)
        assert new_annot.parent() == old_annot.parent()
        assert new_annot.undoStack == old_annot.undoStack
        s.undoStack.undo()
        assert x.rowCount() == 2
        s.undoStack.redo()
        assert x.rowCount() == 3

    def test_addAnnotation_AnnotationDessin(self, am, qtbot, fk):
        s = am(2)
        x = s.model
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
        new_annot = x.data(x.index(2, 0), AnnotationRole)
        old_annot = x.data(x.index(0, 0), AnnotationRole)
        assert new_annot.parent() == old_annot.parent()
        assert new_annot.undoStack == old_annot.undoStack
        assert x.rowCount() == 3
        assert x._data[-1].x == 0.24426605504587157
        s.undoStack.undo()
        assert x.rowCount() == 2
        s.undoStack.redo()
        assert x.rowCount() == 3

    def test_addAnnotation_Rien(self, am, qtbot, fk):
        s = am(2)
        x = AnnotationModel(s)
        x.addAnnotation(
            "Bla",
            {},
        )

        assert x.rowCount() == 2


class TestAnnotationSetCommand:
    def test_undo_redo(self, am, qtbot, fk):
        s = am(["t", "t", "t"])
        x = s.model
        annot = x.data(x.index(1, 0), AnnotationRole)
        init = annot.text
        c = SetAnnotationCommand(annotation=annot, position=1, toset={"text": "azerty"})
        c.redo()
        assert annot.text == "azerty"
        c.undo()
        assert annot.text == init

    def test_undo_redo_after_a_remove(self, am, qtbot, fk):
        s = am(["t", "t", "t"])
        x = s.model
        anot1 = x.data(x.index(1, 0), AnnotationRole)
        init0 = x.data(x.index(0, 0), AnnotationRole).text
        init1 = anot1.text
        init2 = x.data(x.index(2, 0), AnnotationRole).text
        c = SetAnnotationCommand(annotation=anot1, position=1, toset={"text": "azerty"})

        c.redo()
        assert anot1.text == "azerty"
        d = RemoveAnnotationCommand(annotation=anot1, position=1)
        d.redo()
        d.undo()
        assert x.data(x.index(1, 0), AnnotationRole).id == anot1.id
        c.undo()
        assert x.data(x.index(0, 0), AnnotationRole).text == init0
        assert x.data(x.index(1, 0), AnnotationRole).text == init1
        assert x.data(x.index(2, 0), AnnotationRole).text == init2
