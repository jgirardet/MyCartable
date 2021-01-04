import QtQuick 2.15
import QtQuick.Controls 2.15
import QtTest 1.14

Rectangle {
    id: item

    width: 400
    height: 200
    color: "blue"

    CasTest {
        //compare(tested.contentY, 21); //position at load

        property ListModel listmodel
        property var txt1
        property var txt2
        property var img3
        property var page
        property var pageObj
        property var sec0
        property var sec1
        property var sec2
        property var sec3
        property var sec4

        function initPre() {
            Qt.application.organization = "blablb";
            page = fk.f("page", {
                "lastPosition": 3
            });
            sec0 = fk.f("textSection", {
                "text": "blabla 0",
                "page": page.id
            });
            sec1 = fk.f("textSection", {
                "text": "blabla 1",
                "page": page.id
            });
            sec2 = fk.f("textSection", {
                "text": "blabla 2",
                "page": page.id
            });
            sec3 = fk.f("imageSection", {
                "path": "sc1.png",
                "page": page.id
            });
            sec4 = fk.f("textSection", {
                "text": "blabla 4",
                "page": page.id
            });
            pageObj = th.getBridgeInstance(item, "Page", page.id);
            params = {
                "page": pageObj,
                "width": item.width,
                "height": item.height
            };
        }

        function initPost() {
            tryCompare(tested, "populated", true);
            txt1 = tested.itemAt(1);
            txt2 = tested.itemAt(2);
            img3 = tested.itemAt(3);
        }

        function test_init() {
            compare(tested.clip, true);
            compare(tested.count, 5);
            //compare(txt1.height, 17);
            compare(img3.height, 225);
            compare(tested.lastPosition, 3); //binding
            compare(tested._itemAlreadyLoaded, 5);
            compare(tested.populated, true);
            compare(tested.boundsBehavior, Flickable.StopAtBounds);
        }

        function test_empty_page_send_populated() {
            let p = fk.f("page");
            let po = th.getBridgeInstance(item, "Page", p.id);
            let ps = createObj(testedNom, {
                "page": po
            });
            verify(tested.populated);
        }

        function test_append_row__set_last_position() {
            pageObj.addSection("TextSection");
            tryCompare(tested, "count", 6);
            compare(tested.lastPosition, 5);
        }

        function test_insert_row() {
            pageObj.addSection("TextSection", 2, {
            });
            tryCompare(tested, "count", 6);
            compare(tested.lastPosition, 2);
        }

        function test_insert_row_entre_data() {
            return [{
                "index": 0,
                "classType": "TextSection"
            }, {
                "index": 1,
                "classType": "ImageSection"
            }, {
                "index": 3,
                "classType": "EquationSection"
            }];
        }

        function test_insert_row_entre(data) {
            if (Qt.platform.os == "windows")
                skip("ne marche pas sous windows", 1);

            var inter = findChild(txt1, "intermousearea");
            mouseClick(inter, undefined, undefined, Qt.RightButton, Qt.ShiftModifier);
            tryCompare(tested.addDialog, "scale", 1);
            mouseClick(tested.addDialog.contentItem.children[data.index]);
            if (data.classType == "ImageSection") {
                let filedialog = tested.addDialog.contentItem.children[data.index].action.dialog;
                filedialog.folder = "assets";
                wait(50);
                // ATTENTION, en fonction de ce qui a dans asset ça peut changer
                //                mouseClick(filedialog.contentItem, 150, 80, Qt.LeftButton, Qt.NoModifier, 50);
                //                wait(1000);
                mouseDoubleClickSequence(filedialog.contentItem, 150, 80, Qt.LeftButton, Qt.NoModifier, 50);
            }
            tryCompare(tested.addDialog, "scale", 0);
            compare(tested.addDialog.visible, false);
            tryCompare(tested.itemAt(2).section, "classtype", data.classType);
        }

        function test_remove_a_row() {
            mouseClick(txt2, 1, 1, Qt.MiddleButton, Qt.ShiftModifier);
            tryCompare(tested.removeDialog, "scale", 1);
            tested.removeDialog.accept();
            tryCompare(tested.itemAt(2).section, "classtype", "ImageSection");
            compare(tested.count, 4);
        }

        function test_pagebasedelegate_mousearea_click_simple_traverse() {
            clickAndWrite(txt1);
            tryCompare(txt1.contentItem, "length", 3);
        }

        function test_move_delegate_down() {
            mouseDrag(txt1, 1, 1, 0, txt1.height * 6, Qt.LeftButton, Qt.ShiftModifier);
            compare(tested.itemAt(1).section.id, sec2.id);
            compare(tested.itemAt(2).section.id, sec1.id);
        }

        function test_move_delegate_up() {
            mouseDrag(txt2, 1, 1, 0, -txt2.height * 6, Qt.LeftButton, Qt.ShiftModifier);
            compare(tested.itemAt(1).section.id, sec2.id);
            compare(tested.itemAt(2).section.id, sec1.id);
        }

        function test_move_delegate_no_move() {
            mouseDrag(txt2, 1, 1, 0, 0, Qt.LeftButton, Qt.ShiftModifier);
            compare(tested.itemAt(1).section.id, sec1.id);
            compare(tested.itemAt(2).section.id, sec2.id);
        }

        function test_move_delegate_state() {
            var dragged = findChild(txt1, "dragitem");
            compare(dragged.opacity, 1);
            fuzzyCompare(dragged.color, "transparent", 0);
            mousePress(txt1, 1, 1, Qt.LeftButton, Qt.ShiftModifier);
            compare(dragged.opacity, 0.6);
            fuzzyCompare(dragged.color, "steelblue", 0);
        }

        name: "PageSections"
        testedNom: "qrc:/qml/page/PageSections.qml"
    }

}
