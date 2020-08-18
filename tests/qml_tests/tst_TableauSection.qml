import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "assets/tableautestvalues.mjs" as DATA

Item {
    id: item

    property var cellModel: DATA.modelDeBase

    width: 400
    height: 300

    CasTest {
        property Repeater rep
        property GridLayout grid
        property TextArea un
        property TextArea deux
        property var model: item.cellModel

        function initPre() {
            params = {
                "sectionId": 1270,
                "sectionItem": item
            };
        }

        function initPreCreate() {
            ddb._nbColonnes = 3;
            ddb._initTableauDatas = model;
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
            compare(tested.sectionId, 1270);
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
            compare(rep.model, ddb.initTableauDatas(3));
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
            compare(ddb._updateCell, [1270, 0, 1, {
                "texte": "bla"
            }]);
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
            un.font.pointSize = 10;
            un.forceActiveFocus();
            un.cursorPosition = 2;
            keyPress(Qt.Key_Plus);
            compare(un.text, "un+");
            keyClick(Qt.Key_Plus, Qt.ControlModifier);
            compare(un.font.pointSize, 12);
            keyClick(Qt.Key_Minus, Qt.ControlModifier);
            compare(un.font.pointSize, 10);
        }

        function test_set_style_from_menu_color() {
            un.color = "blue";
            var dict = {
                "style": {
                    "fgColor": "red"
                }
            };
            un.setStyleFromMenu(dict);
            compare(ddb._updateCell, [1270, 0, 1, dict]);
            verify(Qt.colorEqual(un.color, "red"));
        }

        function test_set_style_from_menu_bgcolor() {
            un.background.color = "blue";
            var dict = {
                "style": {
                    "bgColor": "red"
                }
            };
            un.setStyleFromMenu(dict);
            compare(ddb._updateCell, [1270, 0, 1, dict]);
            verify(Qt.colorEqual(un.background.color, "red"));
        }

        function test_set_style_from_menu_underline() {
            un.font.underline = false;
            var dict = {
                "style": {
                    "underline": "true"
                }
            };
            un.setStyleFromMenu(dict);
            compare(ddb._updateCell, [1270, 0, 1, dict]);
            verify(un.font.underline);
        }

        function test_mouseClick_style() {
            var cbBgRed = uiManager.menuFlottantTableau.contentItem.contentItem.children[0].children[0].children[1].children[0];
            var cbBlueNoUnderline = uiManager.menuFlottantTableau.contentItem.contentItem.children[3].children[0].children[1];
            var cbGreenUnderline = uiManager.menuFlottantTableau.contentItem.contentItem.children[5].children[0].children[2];
            //       wait(5000)
            // background
            compare(Qt.colorEqual(un.background.color, "blue"), true);
            compare(uiManager.menuTarget, undefined);
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(uiManager.menuTarget, un); //target is tx
            mouseClick(cbBgRed, 1, 1);
            compare(Qt.colorEqual(un.background.color, cbBgRed.color), true);
            // text color
            compare(Qt.colorEqual(un.color, "black"), true);
            un.font.underline = true;
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(uiManager.menuTarget, un); //target is tx
            mouseClick(cbBlueNoUnderline, 1, 1);
            compare(Qt.colorEqual(un.color, cbBlueNoUnderline.color), true);
            verify(!un.font.underline);
            // color underline
            un.color = "red";
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(uiManager.menuTarget, un); //target is tx
            mouseClick(cbGreenUnderline, 1, 1);
            compare(Qt.colorEqual(un.color, cbGreenUnderline.color), true);
            verify(un.font.underline);
        }

        function test_mouseClick_add_column() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[0];
            compare(rep.count, 15);
            ddb._nbColonnes = 4;
            ddb._initTableauDatas = DATA.modelColonneEnPlus;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._insertColumn, [1270, 1]);
            compare(grid.columns, 4);
            compare(rep.count, 20);
        }

        function test_mouseClick_remove_column() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[1];
            compare(rep.count, 15);
            ddb._nbColonnes = 2;
            ddb._initTableauDatas = DATA.modelColonneEnMoins;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._removeColumn, [1270, 1]);
            compare(grid.columns, 2);
            compare(rep.count, 10);
        }

        function test_mouseClick_append_column() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[2];
            ddb._nbColonnes = 4;
            ddb._initTableauDatas = DATA.modelColonneEnPlus;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._appendColumn, [1270]);
            compare(grid.columns, 4);
            compare(rep.count, 20);
        }

        function test_mouseClick_add_row() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[3];
            compare(rep.count, 15);
            ddb._nbColonnes = 3;
            ddb._initTableauDatas = DATA.modelLigneEnPlus;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._insertRow, [1270, 0]);
            compare(rep.count, 18);
        }

        function test_mouseClick_remove_row() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[4];
            ddb._nbColonnes = 3;
            ddb._initTableauDatas = DATA.modelLigneEnMoins;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._removeRow, [1270, 0]);
            compare(rep.count, 12);
        }

        function test_mouseClick_append_row() {
            var but = uiManager.menuFlottantTableau.contentItem.contentItem.children[7].children[0].children[5];
            ddb._nbColonnes = 3;
            ddb._initTableauDatas = DATA.modelLigneEnPlus;
            mouseClick(un, 1, 1, Qt.RightButton);
            mouseClick(but, 1, 1, Qt.LeftButton);
            compare(ddb._appendRow, [1270]);
            compare(rep.count, 18);
        }

        function test_targetmenu_egale_grid_if_selected() {
            grid.selectCell(un);
            mouseClick(un, 1, 1, Qt.RightButton);
            compare(uiManager.menuTarget, grid);
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
