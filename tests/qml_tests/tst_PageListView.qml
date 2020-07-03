import QtQuick 2.14
import QtTest 1.14

Item {
    id: item

    width: 800
    height: 600

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
        //      tested.sectionId = 1
        // PARTIE TEST PAGELISTVIEW
        // positionview non testé
        // PARTIE TEST DELEGATE
        // JE SAIS PAS LE TESTER
        //      ddb.currentPage = 1
        //      mouseClick(un, 1, height - 5, Qt.RightButton, Qt.ShiftModifier)
        //      tested.addDialog.width = item.width
        //      var addText = tested.addDialog.contentItem.children[0]
        //      wait(2000)
        //      mouseClick(addText, 1, 1)
        //      //      addText.toggle()
        //      compare(ddb._addSection, {
        //        "classtype": "TextSection",
        //        "position": 3
        //      })
        //          wait(3000)

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

        function test_insert_row_entre() {
        }

        name: "PageListView"
        testedNom: "qrc:/qml/page/PageListView.qml"
    }

}
