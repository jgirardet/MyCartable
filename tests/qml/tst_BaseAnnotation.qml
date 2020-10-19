import QtQuick 2.15

Item {
    id: item

    property var currentAnnotation: null
    property Item model

    width: 320
    height: 200
    implicitWidth: width
    implicitHeight: height

    CasTest {
        //        "height": 0.8

        property var annot
        property int index: 1
        property var edit

        function initPre() {
            //      params = {
            item.currentAnnotation = null;
            item.model._removeRow = 0;
            edit = null;
            annot = fk.f("annotationText", {
                "x": 0.4,
                "y": 0.2
            });
            params = {
                "annot": annot,
                "referent": item,
                "index": index,
                "edit": edit
            };
        }

        function initPreCreate() {
        }

        function initPost() {
        }

        function test_init() {
            compare(tested.anchors.topMargin, 200 * 0.2);
            compare(tested.anchors.leftMargin, 320 * 0.4);
        }

        function test_focus_hover() {
            item.currentAnnotation = false;
            verify(!tested.focus, "focus should be false");
            verify(!item.currentAnnotation);
            //      item.currentAnnotation = tested
            mouseMove(tested, 1, 1);
            compare(item.currentAnnotation, tested);
        }

        function test_right_button_show_menu() {
            uiManager.menuFlottantAnnotationText = createObj("qrc:/qml/menu/MenuFlottantAnnotationText.qml");
            verify(!tested.item.menu.visible);
            mouseClick(tested, 0, 0, Qt.RightButton);
            verify(tested.item.menu.visible);
        }

        function test_ctrl_left_drag_annot_and_save_move() {
            verify(!tested.held);
            mouseDrag(tested, 0, 0, 16, 20, Qt.LeftButton, Qt.ControlModifier);
            verify(!tested.held);
            compare(edit, {
                "id": annot.id,
                "x": 0.45,
                "y": 0.3
            });
        }

        function test_move() {
            tested.move(32, 40);
            tested.anchors.leftMargin = 0.5;
            tested.anchors.topMargin = 0.4;
            compare(edit, {
                "id": annot.id,
                "x": 0.5,
                "y": 0.4
            });
        }

        function test_setStyleFromMenu() {
            tested.setStyleFromMenu({
                "color": "red"
            });
            compare(edit, {
                "id": annot.id,
                "color": "red"
            });
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
