import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "assets/tableautestvalues.mjs" as DATA

Item {
    id: item

    property var cellModel: DATA.modelDeBase

    width: 400
    height: 300

    Database {
        id: database
    }

    CasTest {
        //                "datas": DATA.modelDeBase

        property Repeater rep
        property GridLayout grid
        property TextArea un
        property TextArea deux
        property var model: item.cellModel
        property var secDB
        property var sec
        property var page

        function initPre() {
            secDB = fk.f("tableauSection", {
                "id": '11111111-1111-1111-1111-111111111111',
                "lignes": 5,
                "colonnes": 3
            });
            for (let dat of DATA.modelDeBase) {
                database.setDB("TableauCell", [secDB.id, dat.y, dat.x], {
                    "style": dat.style,
                    "texte": dat.texte
                });
            }
            page = th.getBridgeInstance(item, "Page", secDB.page);
            sec = page.getSection(0);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function initPost() {
            rep = findChild(tested, "repeater");
            grid = findChild(tested, "grid");
            un = rep.itemAt(1);
            deux = rep.itemAt(2);
        }

        function check_all_deselected() {
            for (var i of Array(15).keys()) {
                var cel = rep.itemAt(i);
                compare(cel.state, "");
            }
            compare(grid.selectedCells, []);
            compare(grid.currentSelectedCell, null);
        }

        function select_many(numbers) {
            var cells = [];
            for (var i of numbers) {
                var cel = rep.itemAt(i);
                grid.selectCell(cel);
                cells.push(cel);
            }
            return cells;
        }

        function test_init() {
            compare(tested.section.id, sec.id);
            compare(rep.count, 15);
            compare(tested.width, grid.width);
            compare(tested.height, grid.height);
        }

        function test_grid() {
            compare(grid.selectedCells, []);
            compare(grid.currentSelectedCell, null);
            compare(grid.columns, 3);
        }

        function test_grid_selectCell() {
            // cas simple
            grid.selectCell(un);
            compare(un.state, "selected");
            compare(grid.selectedCells, [un]);
            compare(grid.currentSelectedCell, un);
            // cas simple du deuxieme
            grid.selectCell(deux);
            compare(grid.selectedCells, [un, deux]);
            compare(grid.currentSelectedCell, deux);
        }

        function test_grid_unselectCells_not_last() {
            grid.selectCell(un);
            grid.selectCell(deux);
            grid.selectCell(un);
            compare(grid.selectedCells[deux]);
            compare(grid.currentSelectedCell, deux);
        }

        function test_grid_unselectCells_is_last_then_empty() {
            grid.selectCell(un);
            compare(grid.currentSelectedCell, un);
            grid.selectCell(un);
            compare(grid.selectedCells, []);
            compare(grid.currentSelectedCell, null);
        }

        function test_grid_unselectCells_is_last_not_empty() {
            grid.selectCell(un);
            grid.selectCell(deux);
            compare(grid.currentSelectedCell, deux);
            grid.selectCell(deux);
            compare(grid.selectedCells, [un]);
            compare(grid.currentSelectedCell, un);
        }

        function test_grid_unSelectAll() {
            var cels = select_many([3, 4, 5, 6, 7, 8]);
            grid.unSelectAll();
            check_all_deselected();
        }

        function test_grid_setStyleFromMenu() {
            [un, deux] = select_many([1, 2]);
            var trois = rep.itemAt(3);
            grid.setStyleFromMenu({
                "style": {
                    "underline": true
                }
            });
            verify(un.font.underline);
            verify(deux.font.underline);
            verify(!trois.font.underline);
            check_all_deselected();
        }

        function test_repeater() {
            compare(rep.model, sec.initTableauDatas());
        }

        function test_delegate_init() {
            verify(un.Layout.fillHeight);
            verify(un.Layout.fillWidth);
            verify(un.selectByMouse);
            compare(un.text, model[1].texte);
            compare(un.font.pointSize, 14);
            compare(deux.font.pointSize, 8);
            compare(deux.font.underline, false);
            compare(rep.itemAt(9).font.underline, true);
            verify(Qt.colorEqual(un.color, "black"));
            verify(Qt.colorEqual(rep.itemAt(4).color, "red"));
            verify(Qt.colorEqual(rep.itemAt(11).color, "green"));
            verify(Qt.colorEqual(rep.itemAt(11).color, "green"));
            verify(Qt.colorEqual(rep.itemAt(4).background.color, "white"));
            verify(Qt.colorEqual(un.background.color, "blue"));
        }

        function test_delegate_onTextChanged_and_setText() {
            un.text = "bla";
            compare(fk.getItem("TableauCell", sec.id, 0, 1).texte, "bla");
            clickAndUndo(un);
            compare(fk.getItem("TableauCell", sec.id, 0, 1).texte, "un");
            compare(un.text, "un");
            clickAndRedo(un);
            compare(fk.getItem("TableauCell", sec.id, 0, 1).texte, "bla");
            compare(un.text, "bla");
        }

        function test_delegate_selected_state() {
            verify(Qt.colorEqual(un.background.color, "blue"));
            un.state = "selected";
            verify(Qt.colorEqual(un.background.color, "lightsteelblue"));
            un.state = "";
            verify(Qt.colorEqual(un.background.color, "blue"));
        }

        function checkFocus(prev, next, key, modifier = Qt.ControlModifier) {
            rep.itemAt(prev).forceActiveFocus();
            keyClick(key, modifier);
            compare(rep.itemAt(next).focus, true, "prev: " + prev + ", next: " + next);
            if (prev != next)
                compare(rep.itemAt(prev).focus, false, "prev: " + prev + ", next: " + next);

        }

        function test_delegate_deplacement_curseur_standard() {
            checkFocus(4, 7, Qt.Key_Down);
            checkFocus(4, 1, Qt.Key_Up);
            checkFocus(4, 3, Qt.Key_Left);
            checkFocus(4, 5, Qt.Key_Right);
            checkFocus(13, 13, Qt.Key_Down);
            checkFocus(1, 1, Qt.Key_Up);
            checkFocus(2, 3, Qt.Key_Right);
            checkFocus(14, 14, Qt.Key_Right);
            checkFocus(0, 0, Qt.Key_Left);
        }

        function test_delegate_deplacement_curseur_limite_gauche() {
            var dix = rep.itemAt(10);
            var end = dix.length;
            // cas en limite de case gauche
            dix.cursorPosition = 0;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Right, Qt.NoModifier);
            dix.cursorPosition = 0;
            dix.forceActiveFocus();
            checkFocus(10, 9, Qt.Key_Left, Qt.NoModifier);
            dix.cursorPosition = 0;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Down, Qt.NoModifier);
            dix.cursorPosition = 0;
            dix.forceActiveFocus();
            checkFocus(10, 7, Qt.Key_Up, Qt.NoModifier);
        }

        function test_delegate_deplacement_curseur_limite_droite() {
            // cas en limite de case droit e
            var dix = rep.itemAt(10);
            var end = dix.length;
            dix.cursorPosition = end;
            dix.forceActiveFocus();
            checkFocus(10, 11, Qt.Key_Right, Qt.NoModifier);
            dix.cursorPosition = end;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Left, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = end;
            checkFocus(10, 13, Qt.Key_Down, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = end;
            checkFocus(10, 10, Qt.Key_Up, Qt.NoModifier);
        }

        function test_delegate_deplacement_curseur_limite_haut() {
            // cas en limite de case haut
            var dix = rep.itemAt(10);
            var end = dix.length;
            dix.cursorPosition = 2;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Right, Qt.NoModifier);
            dix.cursorPosition = 2;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Left, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = 2;
            checkFocus(10, 10, Qt.Key_Down, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = 2;
            checkFocus(10, 7, Qt.Key_Up, Qt.NoModifier);
        }

        function test_delegate_deplacement_curseur_limite_bas() {
            // cas en limite de case bas
            var dix = rep.itemAt(10);
            var end = dix.length;
            dix.cursorPosition = end - 2;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Right, Qt.NoModifier);
            dix.cursorPosition = end - 2;
            dix.forceActiveFocus();
            checkFocus(10, 10, Qt.Key_Left, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = end - 2;
            checkFocus(10, 13, Qt.Key_Down, Qt.NoModifier);
            dix.forceActiveFocus();
            dix.cursorPosition = end - 2;
            checkFocus(10, 10, Qt.Key_Up, Qt.NoModifier);
        }

        function test_set_PointSize() {
            un.forceActiveFocus();
            un.cursorPosition = 2;
            keyClick(Qt.Key_Plus, Qt.ControlModifier);
            compare(un.font.pointSize, 16);
            clickAndUndo(un);
            compare(un.font.pointSize, 14);
            clickAndRedo(un);
            compare(un.font.pointSize, 16);
            keyClick(Qt.Key_Minus, Qt.ControlModifier);
            compare(un.font.pointSize, 14);
            clickAndUndo(un);
            compare(un.font.pointSize, 16);
            clickAndRedo(un);
            compare(un.font.pointSize, 14);
        }

        function test_set_style_from_menu_color() {
            fuzzyCompare(un.color, "black", 0);
            var dict = {
                "style": {
                    "fgColor": "red"
                }
            };
            un.setStyleFromMenu(dict);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 0, 1).style.fgColor, "red", 0);
            verify(Qt.colorEqual(un.color, "red"));
            clickAndUndo(un);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 0, 1).style.fgColor, "black", 0);
            fuzzyCompare(un.color, "black", 0);
        }

        function test_set_bgcolor_cell_white_undo_redo() {
            let quatre = rep.itemAt(4);
            let backupcolor = quatre.background.color;
            fuzzyCompare(quatre.background.color, "white", 0);
            var dict = {
                "style": {
                    "bgColor": "red"
                }
            };
            quatre.setStyleFromMenu(dict);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 1, 1).style.bgColor, "red", 0);
            verify(Qt.colorEqual(quatre.background.color, "red"));
            clickAndUndo(quatre);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 1, 1).style.bgColor, "#00000000", 0);
            fuzzyCompare(quatre.background.color, "white", 0);
            clickAndRedo(quatre);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 1, 1).style.bgColor, "red", 0);
            fuzzyCompare(quatre.background.color, "red", 0);
        }

        function test_set_style_from_menu_bgcolor() {
            let backupcolor = un.background.color;
            var dict = {
                "style": {
                    "bgColor": "red"
                }
            };
            un.setStyleFromMenu(dict);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 0, 1).style.bgColor, "red", 0);
            verify(Qt.colorEqual(un.background.color, "red"));
            clickAndUndo(un);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 0, 1).style.bgColor, backupcolor, 0);
            fuzzyCompare(un.background.color, backupcolor, 0);
            clickAndRedo(un);
            fuzzyCompare(fk.getItem("TableauCell", sec.id, 0, 1).style.bgColor, "red", 0);
            fuzzyCompare(un.background.color, "red", 0);
        }

        function test_set_style_from_menu_underline() {
            un.font.underline = false;
            var dict = {
                "style": {
                    "underline": "true"
                }
            };
            un.setStyleFromMenu(dict);
            compare(fk.getItem("TableauCell", sec.id, 0, 1).style.underline, true);
            verify(un.font.underline);
            clickAndUndo(un);
            compare(fk.getItem("TableauCell", sec.id, 0, 1).style.underline, false);
            verify(!un.font.underline);
            clickAndRedo(un);
            compare(fk.getItem("TableauCell", sec.id, 0, 1).style.underline, true);
            verify(un.font.underline);
        }

        function test_mouseClick_style() {
            var cbBgRed = tested.menu.fonds.children[0];
            var cbBlueNoUnderline = tested.menu.styleNoUnderline.children[1];
            var cbGreenUnderline = tested.menu.styleUnderline.children[2];
            print(cbBgRed, cbBlueNoUnderline, cbGreenUnderline);
            // background
            compare(Qt.colorEqual(un.background.color, "blue"), true);
            compare(tested.menu.target, undefined);
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(tested.menu.target, un); //target is tx
            mouseClick(cbBgRed, 1, 1);
            compare(Qt.colorEqual(un.background.color, cbBgRed.color), true);
            sec.undoStack.undo();
            fuzzyCompare(un.background.color, "blue", 0);
            sec.undoStack.redo();
            fuzzyCompare(un.background.color, cbBgRed.color, 0);
            // text color
            compare(Qt.colorEqual(un.color, "black"), true);
            un.font.underline = true;
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(tested.menu.target, un); //target is tx
            mouseClick(cbBlueNoUnderline, 1, 1);
            compare(Qt.colorEqual(un.color, cbBlueNoUnderline.color), true);
            verify(!un.font.underline);
            sec.undoStack.undo();
            sec.undoStack.undo();
            fuzzyCompare(un.color, "black", 0);
            verify(!un.font.underline);
            sec.undoStack.redo();
            sec.undoStack.redo();
            fuzzyCompare(un.color, cbBlueNoUnderline.color, 0);
            verify(!un.font.underline);
            // color underline
            let backupcolor = un.color;
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(tested.menu.target, un); //target is tx
            mouseClick(cbGreenUnderline, 1, 1);
            compare(Qt.colorEqual(un.color, cbGreenUnderline.color), true);
            verify(un.font.underline);
            sec.undoStack.undo();
            sec.undoStack.undo();
            fuzzyCompare(un.color, backupcolor, 0);
            verify(!un.font.underline);
            sec.undoStack.redo();
            sec.undoStack.redo();
            fuzzyCompare(un.color, cbGreenUnderline.color, 0);
            verify(un.font.underline);
        }

        function test_modify_tableau_data() {
            return [{
                "tag": "insertColumn",
                "button": 0,
                "colredo": 4,
                "rowredo": 5
            }, {
                "tag": "removeColumn",
                "button": 1,
                "colredo": 2,
                "rowredo": 5
            }, {
                "tag": "appendColumn",
                "button": 2,
                "colredo": 4,
                "rowredo": 5
            }, {
                "tag": "insertRow",
                "button": 3,
                "colredo": 3,
                "rowredo": 6
            }, {
                "tag": "removeRow",
                "button": 4,
                "colredo": 3,
                "rowredo": 4
            }, {
                "tag": "appendRow",
                "button": 5,
                "colredo": 3,
                "rowredo": 6
            }];
        }

        function test_modify_tableau(data) {
            let but = tested.menu[data.tag];
            compare(rep.count, 15);
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(sec.colonnes, data.colredo);
            compare(grid.columns, data.colredo);
            compare(sec.lignes, data.rowredo);
            compare(rep.count, data.rowredo * data.colredo);
            verify(!tested.menu.visible);
            sec.undoStack.undo();
            compare(sec.colonnes, 3);
            compare(grid.columns, 3);
            compare(rep.count, 15);
            compare(sec.lignes, 5);
            sec.undoStack.redo();
            compare(sec.colonnes, data.colredo);
            compare(grid.columns, data.colredo);
            compare(sec.lignes, data.rowredo);
            compare(rep.count, data.rowredo * data.colredo);
        }

        function test_targetmenu_egale_grid_if_selected() {
            grid.selectCell(un);
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(tested.menu.target, grid);
        }

        function selected(liste) {
            // renvoie une liste d'Item depres le index
            var res = [];
            for (var i of liste) {
                res.push(rep.itemAt(i));
            }
            return res;
        }

        function test_mouseSelect_bypress(liste) {
            mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier);
            compare(grid.selectedCells, [un]);
        }

        function test_mouseSelect_bymove(liste) {
            mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier);
            compare(grid.selectedCells, [un]);
            mouseMove(deux, 1, 1);
            compare(grid.selectedCells, [un, deux]);
        }

        function test_mousepress_unselect_if_no_ctrl(liste) {
            mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier);
            mouseRelease(un);
            compare(grid.selectedCells, [un]);
            mousePress(un, 0, 0, Qt.LeftButton, Qt.NoModifier);
            compare(grid.selectedCells, []);
            verify(un.activeFocus);
        }

        function test_on_ne_rajoute_pas_item_dans_selected_quand_moove_si_deja_selected() {
            // on se déplace dans un élément déjà currentSelectedCell
            grid.selectCell(un);
            compare(grid.selectedCells, [un]);
            mouseMove(un, 1, 2);
            compare(grid.selectedCells, [un]);
        }

        function test_deselect_marche_arriere() {
            // marche arrière
            mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier);
            mouseMove(deux, deux.width / 2, deux.height / 2);
            compare(grid.selectedCells, [un, deux]);
            mouseMove(un, un.width / 2, un.height / 2);
            compare(grid.selectedCells, [un]);
        }

        name: "TableauSection"
        testedNom: "qrc:/qml/sections/TableauSection.qml"
        params: {
        }
    }

}
