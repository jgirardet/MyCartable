 import QtQuick 2.15
 import QtQuick.Controls 2.15
 import QtQuick.Layouts 1.15

 Item {
   width: 400
   height: 300
   id: item

  property var cellModel: [
  {
     "style": {
       "bgColor": "red",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10791,
       "underline": false
     },
     "tableau": 1270,
     "texte": "zero",
     "x": 0,
     "y": 0
   }, {
     "style": {
       "bgColor": "blue",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10792,
       "underline": false
     },
     "tableau": 1270,
     "texte": "un",
     "x": 1,
     "y": 0
   }, {
     "style": {
       "bgColor": "blue",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10793,
       "underline": false,
       "pointSize": 8
     },
     "tableau": 1270,
     "texte": "deux\ndeux",
     "x": 2,
     "y": 0
   }, {
     "style": {
       "bgColor": "red",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10794,
       "underline": false
     },
     "tableau": 1270,
     "texte": "trois trois",
     "x": 0,
     "y": 1
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "red",
       "strikeout": false,
       "styleId": 10795,
       "underline": false
     },
     "tableau": 1270,
     "texte": "quatre",
     "x": 1,
     "y": 1
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10796,
       "underline": false
     },
     "tableau": 1270,
     "texte": "cinq",
     "x": 2,
     "y": 1
   }, {
     "style": {
       "bgColor": "red",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10797,
       "underline": false
     },
     "tableau": 1270,
     "texte": "six",
     "x": 0,
     "y": 2
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10798,
       "underline": false
     },
     "tableau": 1270,
     "texte": "sept sept sept",
     "x": 1,
     "y": 2
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "red",
       "strikeout": false,
       "styleId": 10799,
       "underline": false
     },
     "tableau": 1270,
     "texte": "huit",
     "x": 2,
     "y": 2
   }, {
     "style": {
       "bgColor": "red",
       "family": "",
       "fgColor": "green",
       "strikeout": false,
       "styleId": 10800,
       "underline": true
     },
     "tableau": 1270,
     "texte": "neuf",
     "x": 0,
     "y": 3
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "green",
       "strikeout": false,
       "styleId": 10801,
       "underline": true
     },
     "tableau": 1270,
     "texte": "dix\ndix\ndix",
     "x": 1,
     "y": 3
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "green",
       "strikeout": false,
       "styleId": 10802,
       "underline": true
     },
     "tableau": 1270,
     "texte": "onze",
     "x": 2,
     "y": 3
   }, {
     "style": {
       "bgColor": "red",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10803,
       "underline": false
     },
     "tableau": 1270,
     "texte": "doux",
     "x": 0,
     "y": 4
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10804,
       "underline": false
     },
     "tableau": 1270,
     "texte": "treize",
     "x": 1,
     "y": 4
   }, {
     "style": {
       "bgColor": "#00000000",
       "family": "",
       "fgColor": "black",
       "strikeout": false,
       "styleId": 10805,
       "underline": false
     },
     "tableau": 1270,
     "texte": "quatorze",
     "x": 2,
     "y": 4
   }]

   CasTest {
     name: "TableauSection"
     testedNom: "qrc:/qml/sections/TableauSection.qml"
     params: {}

    property Repeater rep
    property GridLayout grid
    property TextArea un
    property TextArea deux
    property var model: item.cellModel




     function initPre() {
       params = {
         "sectionId": 1270,
         "sectionItem": item,
       }
     }

     function initPreCreate() {
       ddb._loadSection = {
         "classtype": "TableauSection",
         "colonnes": 3,
         "created": "2020-06-25T20:05:21.065677",
         "id": 1270,
         "lignes": 5,
         "modified": "2020-06-25T20:07:07.635539",
         "page": 101,
         "position": 0
       }
       ddb._initTableauDatas = model
     }

     function initPost() {
       rep = findChild(tested, "repeater")
       grid = findChild(tested, "grid")
       un = rep.itemAt(1)
       deux = rep.itemAt(2)
     }

     function check_all_deselected() {
       for (var i of Array(15).keys()) {
         var cel = rep.itemAt(i)
         compare(cel.state, "")
       }
       compare(grid.selectedCells, [])
       compare(grid.currentSelectedCell, null)
     }

     function select_many(numbers) {
       var cells = []
       for (var i of numbers) {
         var cel = rep.itemAt(i)
         grid.selectCell(cel)
         cells.push(cel)
       }
       return cells
     }

     function test_init() {
       compare(tested.sectionId, 1270)
       compare(rep.count, 15)
       compare(tested.width, grid.width)
       compare(tested.height, grid.height)

     }

     function test_grid() {
       compare(grid.selectedCells, [])
       compare(grid.currentSelectedCell, null)
       compare(grid.columns, 3)
     }

     function test_grid_selectCell() {
       // cas simple
       grid.selectCell(un)
       compare(un.state, "selected")
       compare(grid.selectedCells, [un])
       compare(grid.currentSelectedCell, un)
       // cas simple du deuxieme
       grid.selectCell(deux)
       compare(grid.selectedCells, [un, deux])
       compare(grid.currentSelectedCell, deux)
     }

     function test_grid_unselectCells_not_last() {
       grid.selectCell(un)
       grid.selectCell(deux)
       grid.selectCell(un)
       compare(grid.selectedCells[deux])
       compare(grid.currentSelectedCell, deux)
     }

     function test_grid_unselectCells_is_last_then_empty() {
       grid.selectCell(un)
       compare(grid.currentSelectedCell, un)
       grid.selectCell(un)
       compare(grid.selectedCells, [])
       compare(grid.currentSelectedCell, null)
     }

     function test_grid_unselectCells_is_last_not_empty() {
       grid.selectCell(un)
       grid.selectCell(deux)
       compare(grid.currentSelectedCell, deux)
       grid.selectCell(deux)
       compare(grid.selectedCells, [un])
       compare(grid.currentSelectedCell, un)
     }

     function test_grid_unSelectAll() {
       var cels = select_many([3, 4, 5, 6, 7, 8])
       grid.unSelectAll()
       check_all_deselected()

     }

     function test_grid_setStyleFromMenu() {
       [un, deux] = select_many([1, 2])
       var trois = rep.itemAt(3)
       grid.setStyleFromMenu({
         "style": {
           "underline": true
         }
       })
       verify(un.font.underline)
       verify(deux.font.underline)
       verify(!trois.font.underline)
       check_all_deselected()
     }

     function test_repeater() {
       compare(rep.model, ddb.initTableauDatas(3))
     }

     function test_delegate_init() {
       verify(un.Layout.fillHeight)
       verify(un.Layout.fillWidth)
       verify(un.selectByMouse)
       compare(un.text, model[1].texte)
       compare(un.font.pointSize, 14)
       compare(deux.font.pointSize, 8)
       compare(deux.font.underline, false)
       compare(rep.itemAt(9).font.underline, true)
       verify(Qt.colorEqual(un.color, "black"))
       verify(Qt.colorEqual(rep.itemAt(4).color, "red"))
       verify(Qt.colorEqual(rep.itemAt(11).color, "green"))
       verify(Qt.colorEqual(rep.itemAt(11).color, "green"))
       verify(Qt.colorEqual(rep.itemAt(4).background.color, "white"))
       verify(Qt.colorEqual(un.background.color, "blue"))

     }

     function test_delegate_onTextChanged_and_setText() {
       un.text = "bla"
       compare(ddb._updateCell, [1270, 0, 1, {
         "texte": "bla"
       }])

     }

     function test_delegate_selected_state() {
       verify(Qt.colorEqual(un.background.color, "blue"))
       un.state = "selected"
       verify(Qt.colorEqual(un.background.color, "lightsteelblue"))
       un.state = ""
       verify(Qt.colorEqual(un.background.color, "blue"))

     }

     function test_delegate_deplacement_curseur() {
       function testFocus(prev, next, key, modifier = Qt.ControlModifier) {
         rep.itemAt(prev).forceActiveFocus()
         keyClick(key, modifier)
         compare(rep.itemAt(next).focus, true, `prev: ${prev}, next: ${next}`)
         if (prev != next) {
           compare(rep.itemAt(prev).focus, false, `prev: ${prev}, next: ${next}`)
         }
       }
       testFocus(4, 7, Qt.Key_Down)
       testFocus(4, 1, Qt.Key_Up)
       testFocus(4, 3, Qt.Key_Left)
       testFocus(4, 5, Qt.Key_Right)
       testFocus(13, 13, Qt.Key_Down)
       testFocus(1, 1, Qt.Key_Up)
       testFocus(2, 3, Qt.Key_Right)
       testFocus(14, 14, Qt.Key_Right)
       testFocus(0, 0, Qt.Key_Left)

       var dix = rep.itemAt(10)
       var end = dix.length
       // cas en limite de case gauche
       dix.cursorPosition = 0
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Right, Qt.NoModifier)
       dix.cursorPosition = 0
       dix.forceActiveFocus()
       testFocus(10, 9, Qt.Key_Left, Qt.NoModifier)
       dix.cursorPosition = 0
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Down, Qt.NoModifier)
       dix.cursorPosition = 0
       dix.forceActiveFocus()
       testFocus(10, 7, Qt.Key_Up, Qt.NoModifier)

       // cas en limite de case droit e
       dix.cursorPosition = end
       dix.forceActiveFocus()
       testFocus(10, 11, Qt.Key_Right, Qt.NoModifier)
       dix.cursorPosition = end
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Left, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = end
       testFocus(10, 13, Qt.Key_Down, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = end
       testFocus(10, 10, Qt.Key_Up, Qt.NoModifier)

       // cas en limite de case haut
       dix.cursorPosition = 2
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Right, Qt.NoModifier)
       dix.cursorPosition = 2
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Left, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = 2
       testFocus(10, 10, Qt.Key_Down, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = 2
       testFocus(10, 7, Qt.Key_Up, Qt.NoModifier)

       // cas en limite de case bas
       dix.cursorPosition = end - 2
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Right, Qt.NoModifier)
       dix.cursorPosition = end - 2
       dix.forceActiveFocus()
       testFocus(10, 10, Qt.Key_Left, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = end - 2
       testFocus(10, 13, Qt.Key_Down, Qt.NoModifier)
       dix.forceActiveFocus()
       dix.cursorPosition = end - 2
       testFocus(10, 10, Qt.Key_Up, Qt.NoModifier)
     }

     function test_set_PointSize() {
       un.font.pointSize = 10
       un.forceActiveFocus()
       un.cursorPosition = 2
       keyPress(Qt.Key_Plus)
       compare(un.text, "un+")
       keyClick(Qt.Key_Plus, Qt.ControlModifier)
       compare(un.font.pointSize, 12)
       keyClick(Qt.Key_Minus, Qt.ControlModifier)
       compare(un.font.pointSize, 10)

     }

     function test_set_style_from_menu_color() {
       un.color = "blue"
       var dict = {
         "style": {
           "fgColor": "red"
         }
       }
       un.setStyleFromMenu(dict)
       compare(ddb._updateCell, [1270, 0, 1, dict])
       verify(Qt.colorEqual(un.color, "red"))
     }

     function test_set_style_from_menu_bgcolor() {
       un.background.color = "blue"
       var dict = {
         "style": {
           "bgColor": "red"
         }
       }
       un.setStyleFromMenu(dict)
       compare(ddb._updateCell, [1270, 0, 1, dict])
       verify(Qt.colorEqual(un.background.color, "red"))
     }

     function test_set_style_from_menu_underline() {
       un.font.underline = false
       var dict = {
         "style": {
           "underline": "true"
         }
       }
       un.setStyleFromMenu(dict)
       compare(ddb._updateCell, [1270, 0, 1, dict])
       verify(un.font.underline)
     }

     function test_mouseClick() {
       var cbBgRed = uiManager.menuFlottantTableau.contentItem.contentItem.children[0].children[0].children[1].children[0]
       var cbBlueNoUnderline = uiManager.menuFlottantTableau.contentItem.contentItem.children[3].children[0].children[1]
       var cbGreenUnderline = uiManager.menuFlottantTableau.contentItem.contentItem.children[5].children[0].children[2]
       //       wait(5000)
       // background
       compare(Qt.colorEqual(un.background.color, "blue"), true)
       compare(uiManager.menuTarget, undefined)
       mouseClick(un, 1, 1, Qt.RightButton)
       compare(uiManager.menuTarget, un) //target is tx
       mouseClick(cbBgRed, 1, 1)
       compare(Qt.colorEqual(un.background.color, cbBgRed.color), true)

       // text color
       compare(Qt.colorEqual(un.color, "black"), true)
       un.font.underline = true
       mouseClick(un, 1, 1, Qt.RightButton)
       compare(uiManager.menuTarget, un) //target is tx
       mouseClick(cbBlueNoUnderline, 1, 1)
       compare(Qt.colorEqual(un.color, cbBlueNoUnderline.color), true)
       verify(!un.font.underline)

       // color underline
       un.color = "red"
       mouseClick(un, 1, 1, Qt.RightButton)
       compare(uiManager.menuTarget, un) //target is tx
       mouseClick(cbGreenUnderline, 1, 1)
       compare(Qt.colorEqual(un.color, cbGreenUnderline.color), true)
       verify(un.font.underline)

     }

     function test_targetmenu_egale_grid_if_selected() {
       grid.selectCell(un)
       mouseClick(un, 1, 1, Qt.RightButton)
       compare(uiManager.menuTarget, grid)
     }

     function selected(liste) {
       // renvoie une liste d'Item depres le index
       var res = []
       for (var i of liste) {
         res.push(rep.itemAt(i))
       }
       return res
     }

     function test_mouseSelect_bypress(liste) {
       mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier)
       compare(grid.selectedCells, [un])
     }

     function test_mouseSelect_bymove(liste) {
       mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier)
       compare(grid.selectedCells, [un])
       mouseMove(deux, 1, 1)
       compare(grid.selectedCells, [un, deux])
     }

     function test_mousepress_unselect_if_no_ctrl(liste) {
       mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier)
       mouseRelease(un)
       compare(grid.selectedCells, [un])
       mousePress(un, 0, 0, Qt.LeftButton, Qt.NoModifier)
       compare(grid.selectedCells, [])
       verify(un.activeFocus)
     }

     function test_on_ne_rajoute_pas_item_dans_selected_quand_moove_si_deja_selected() {

       // on se déplace dans un élément déjà currentSelectedCell
       grid.selectCell(un)
       compare(grid.selectedCells, [un])
       mouseMove(un, 1, 2)
       compare(grid.selectedCells, [un])
     }

     function test_deselect_marche_arriere() {
       // marche arrière
       mousePress(un, 0, 0, Qt.LeftButton, Qt.ControlModifier)
       mouseMove(deux, deux.width / 2, deux.height / 2)
       compare(grid.selectedCells, [un, deux])
       mouseMove(un, un.width / 2, un.height / 2)
       compare(grid.selectedCells, [un])
     }

   }
 }