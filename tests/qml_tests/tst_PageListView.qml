import QtQuick 2.15
import QtQuick.Controls 2.15
import QtTest 1.14

Rectangle {
    id: item

    width: 800
    height: 600
    color: "blue"

    Component {
        id: modelComp

        ListModel {
            id: listmodel

            property int lastPosition: 2
            property var _move
            property var _removeSection

            signal rowsInserted(int index, int row, int col)
            signal modelReset()

            function move(source, target) {
                _move = [source, target];
            }

            function removeSection(source) {
                _removeSection = source;
                remove(index);
            }

            Component.onCompleted: {
                var listData = [{
                    "page": {
                        "id": 1,
                        "classtype": "EquationSection"
                    }
                }, {
                    "page": {
                        "id": 1,
                        "classtype": "EquationSection"
                    }
                }, {
                    "page": {
                        "id": 1,
                        "classtype": "EquationSection"
                    }
                }, {
                    "page": {
                        "id": 1,
                        "classtype": "EquationSection"
                    }
                }, {
                    "page": {
                        "id": 300,
                        "classtype": "EquationSection"
                    }
                }];
                for (var x of listData) {
                    listmodel.append(x);
                }
            }
        }

    }

    CasTest {
        //            print(tested.contentItem.childrenRect.height, newheight);
        //            compare(tested.cacheBuffer, );
        //38298
        //            tryCompare(tested, "cacheBuffer", 45798);

        property ListModel listmodel
        property var un
        property var deux
        property var eq1
        property var eq2

        function initPre() {
            Qt.application.organization = "blablb";
            listmodel = createTemporaryObject(modelComp, item);
            params = {
                "model": listmodel,
                "width": item.width,
                "height": item.height,
                "populate": null
            };
        }

        function initPreCreate() {
            ddb._loadSection = {
                "id": 1,
                "created": "2019-09-22T19:21:57.521813",
                "modified": "2019-09-22T19:21:57.521813",
                "page": 1,
                "position": 1,
                "classtype": "EquationSection",
                "content": "1     \\n__ + 1\\n15    ",
                "curseur": 10
            };
        }

        function initPost() {
            un = tested.itemAtIndex(1);
            deux = tested.itemAtIndex(2);
            eq1 = findChild(un, "loader").item;
            eq2 = findChild(deux, "loader").item;
        }

        function test_init() {
            compare(tested.clip, true);
            compare(tested.count, 5);
            compare(findChild(tested.itemAtIndex(0), "loader").item.text, "1     \\n__ + 1\\n15    ");
            compare(tested.highlightMoveDuration, -1);
            compare(tested.boundsBehavior, Flickable.DragOverBounds);
            compare(tested.currentIndex, 0);
        }

        function test_currentindex_bind_last_position() {
            compare(tested.currentIndex, 0);
            tested.currentIndex = 3;
            tryCompare(listmodel, "lastPosition", 3);
        }

        function test_add_row_selection_nouveau_row() {
            listmodel.rowsInserted("bla", 3, 0);
            tryCompare(tested, "currentIndex", 3);
        }

        function test_model_reset_change_current_index() {
            listmodel.lastPosition = 3;
            listmodel.modelReset();
            compare(tested.currentIndex, 3);
        }

        function test_pagebasedelegate_mousearea_click_simple_traverse() {
            // test click sans modifier traverse
            ddb._updateEquation = {
                "content": "",
                "curseur": 1
            };
            ddb._updateEquationParams = [];
            un.sectionId = 924;
            mouseClick(un); // ici le click focus ave le contenu envoyé
            keyClick(Qt.Key_4); // sans effet sur le résultat
            compare(JSON.parse(ddb._updateEquationParams[3])["key"], 52);
        }

        function test_pagebasedelegate_mousearea_click_modifier_deplace() {
            ddb._updateEquation = {
                "content": "",
                "curseur": 1
            };
            ddb._updateEquationParams = [];
            un.sectionId = 924;
            mousePress(un, 1, 1, Qt.LeftButton, Qt.ShiftModifier);
            keyClick(Qt.Key_3); // sans effet sur le résultat
            compare(ddb._updateEquationParams, []); //non transmis plus bas
            compare(listmodel._move, [1, 1]); // move appelé
        }

        function test_move_delegate() {
            mouseDrag(un, 1, un.height, 0, un.height * 2, Qt.LeftButton, Qt.ShiftModifier);
            compare(listmodel._move, [1, 2]); // move appelé
        }

        function test_move_delegate_state() {
            var dragged = findChild(un, "dragitem");
            compare(dragged.opacity, 1); // move appelé
            verify(Qt.colorEqual(dragged.color, "transparent"), dragged.color);
            mousePress(un, 1, 1, Qt.LeftButton, Qt.ShiftModifier);
            compare(dragged.opacity, 0.6); // move appelé
            verify(Qt.colorEqual(dragged.color, "steelblue"), dragged.color);
        }

        function test__remove_a_row() {
            mouseClick(un, 1, 1, Qt.MiddleButton, Qt.ShiftModifier);
            verify(tested.removeDialog.visible);
            tested.removeDialog.accept();
            compare(listmodel._removeSection, 1); // move appelé
            compare(tested.count, 4);
        }

        function test_insert_row_entre_data() {
            return [{
                "index": 0,
                "classType": "TextSection"
            }, {
                "index": 3,
                "classType": "EquationSection"
            }];
        }

        function test_insert_row_entre(data) {
            ddb.currentPage = 1;
            var inter = findChild(un, "intermousearea");
            mouseClick(inter, undefined, undefined, Qt.RightButton, Qt.ShiftModifier);
            wait(50);
            mouseClick(tested.addDialog.contentItem.children[data.index]); // newtext
            compare(tested.addDialog.visible, false);
            compare(ddb._addSection, [1, {
                "classtype": data.classType,
                "position": 2
            }]);
        }

        function test_adapt_cacheBufffer_superieur_a_2000() {
            compare(tested.cacheBuffer, 20000);
            var ch = tested.contentItem.childrenRect.height; //580
            var h_un = un.height;
            var others = ch - h_un;
            un.height = 20000;
            var newheight = ch - h_un + un.height;
            tryCompare(tested.contentItem.childrenRect, "height", newheight);
            tryCompare(tested, "cacheBuffer", newheight + (newheight / 2)); //38298
        }

        function test_adapt_cacheBufffer_tres_superieur_a_2000() {
            compare(tested.cacheBuffer, 20000);
            var ch = tested.contentItem.childrenRect.height;
            var h_un = un.height;
            var others = ch - h_un;
            un.height = 30000;
            var newheight = ch - h_un + un.height;
            tryCompare(tested.contentItem.childrenRect, "height", newheight);
            tryCompare(tested, "cacheBuffer", newheight + (newheight / 2));
        }

        function test_adapt_cacheBufffer_inferieur_a_2000() {
            compare(tested.cacheBuffer, 20000);
            un.height = 10000;
            var newheight = 10552;
            tryCompare(tested.contentItem.childrenRect, "height", newheight);
            tryCompare(tested, "cacheBuffer", 20000);
        }

        name: "PageListView"
        testedNom: "qrc:/qml/page/PageListView.qml"
    }

}
