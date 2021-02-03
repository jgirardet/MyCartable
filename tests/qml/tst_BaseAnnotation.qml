import QtQuick 2.15

Item {
    id: item

    property var currentAnnotation: null
    property Item model
    property var section: testcase.ref

    width: 320
    height: 200
    implicitWidth: width
    implicitHeight: height

    CasTest {
        id: testcase

        property int index: 0 // index de annot dans model
        property var annot
        property var annotobj
        property var ref
        property var page

        function initPre() {
            item.currentAnnotation = null;
            let img = fk.f("imageSection");
            annot = fk.f("annotationText", {
                "x": 0.4,
                "y": 0.2,
                "section": img.id
            });
            page = th.getBridgeInstance(item, "Page", img.page);
            ref = page.model.data(page.model.index(0, 0), th.getRole("SectionRole"));
            annotobj = ref.model.data(ref.model.index(0, 0), th.getRole("AnnotationRole"));
            params = {
                "annot": annotobj,
                "referent": item,
                "section": section
            };
        }

        function test_init() {
            compare(tested.anchors.topMargin, 200 * 0.2);
            compare(tested.anchors.leftMargin, 320 * 0.4);
        }

        function test_focus_hover() {
            item.currentAnnotation = false;
            verify(!tested.focus, "focus should be false");
            verify(!item.currentAnnotation);
            mouseMove(tested, 1, 1);
            compare(item.currentAnnotation, tested);
        }

        function test_right_button_show_menu() {
            verify(!tested.item.menu.visible);
            mouseClick(tested, 0, 0, Qt.RightButton);
            verify(tested.item.menu.visible);
        }

        function test_ctrl_left_drag_annot_and_save_move() {
            verify(!tested.held);
            mouseDrag(tested, 0, 0, 16, 20, Qt.LeftButton, Qt.ControlModifier);
            verify(!tested.held);
            let newl = fk.getItem("AnnotationText", annot.id);
            compare(newl.x, 0.45);
            compare(newl.y, 0.3);
        }

        function test_move() {
            tested.move(32, 40);
            tested.anchors.leftMargin = 0.5;
            tested.anchors.topMargin = 0.4;
            let newl = fk.getItem("AnnotationText", annot.id);
            compare(newl.x, 0.5);
            compare(newl.y, 0.4);
        }

        function test_setStyleFromMenu() {
            tested.setStyleFromMenu({
                "style": {
                    "bgColor": th.color("red")
                }
            });
            let newl = fk.getItem("AnnotationText", annot.id);
            fuzzyCompare(newl.style.bgColor, "red", 0);
        }

        function test_setStyle_indo_redo() {
            tested.setStyleFromMenu({
                "style": {
                    "bgColor": th.color("red")
                }
            });
            fuzzyCompare(tested.annot.bgColor, "red", 0);
            tested.setStyleFromMenu({
                "style": {
                    "bgColor": th.color("blue")
                }
            });
            fuzzyCompare(tested.annot.bgColor, "blue", 0);
            tested.annot.undoStack.undo();
            fuzzyCompare(tested.annot.bgColor, "red", 0);
            tested.annot.undoStack.redo();
            fuzzyCompare(tested.annot.bgColor, "blue", 0);
        }

        name: "BaseAnnotation"
        testedNom: "qrc:/qml/annotations/BaseAnnotation.qml"
    }

    model: Item {
        property int _removeRow

        function removeRow(idx) {
            return item._removeRow;
        }

    }

}
