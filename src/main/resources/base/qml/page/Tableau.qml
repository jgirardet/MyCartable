import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/js/lodash.js"
as Lodash

TableView {
  id: root
  property int position
  property int sectionId
  property
  var base
  height: root.contentItem.childrenRect.height //model.x * 30
  contentY: model.n_rows * 30 // fix le problème d'une partie caché au chargement
  width: base.width
  interactive: false
  clip: true
  columnSpacing: 3
  rowSpacing: 1
  property int size: rows * columns
  property
  var selectedCells: []

  MouseArea {
    id: bigMouse
    x: root.x
    y: root.y
    width: contentItem.childrenRect.width
    height: contentItem.childrenRect.height
    preventStealing: true
    z: 2 // par dessus les delegate
    propagateComposedEvents: true

    /* beautify preserve:start */
    property var currentSelectedCell
    /* beautify preserve:end */
    pressAndHoldInterval: 300
//    onPressAndHold: {
//      print("holgind")
//      print(pressAndHoldInterval)
//      if (mouse.button == Qt.LeftButton) {
//        if (root.selectedCells.length > 0) {
//          root.unSelectAll()
//        }
//      }
//    }
    onPositionChanged: {
      var tempItem = root.contentItem.childAt(mouse.x, mouse.y)
      if (!containsMouse) {
        // on ne fait rien en dehors de la zone
        return
      } else if (tempItem === currentSelectedCell) {
        // le même on fait rien
        return
      } else if (!tempItem.isTableDelegate) {
        // doit être une des cell
        return

      } else if (tempItem === selectedCells[selectedCells.length - 2]) {
        // c un recul  on déselect celui en cours et change current
        root.selectCell(currentSelectedCell)
        currentSelectedCell = tempItem
      } else {
        //cas simple : nouveau = on ajoute.
        currentSelectedCell = tempItem
        root.selectCell(currentSelectedCell)
      }
    }

    onReleased: {
      //show un pop ?
    }

//    onClicked: {
//      print("onclicked")
//      if (mouse.button == Qt.LeftButton) {
//        if (root.selectedCells.length > 0) {
//          root.unSelectAll()
//        }
//        mouse.accepted = false
//      } else if (mouse.button == Qt.RightButton) {
//        var cel = root.contentItem.childAt(mouse.x, mouse.y)
//        if (root.selectedCells.includes(cel)) {
//          print("show menu")
//        } else {
//          root.unSelectAll()
//          mouse.accepted = false
//        }
//      }
//    }
  }

  delegate: Rectangle {

    id: rectangle
    property alias tinput: textinput
    implicitWidth: textinput.contentWidth + 10
    implicitHeight: textinput.contentHeight + 10
    focus: true
    property bool isTableDelegate: true //juste pour vérifier le type

    states: [
      State {
        name: "selected"
        PropertyChanges {
          target: rectangle;color: "lightsteelblue"
        }
      }
    ]

    MouseArea {
      acceptedButtons: Qt.LeftButton | Qt.RightButton
      anchors.fill: parent
      preventStealing: true
      //      onClicked: {
      //                console.log("clicked base")
      //                mouse.accepted = true
      //            }

      onClicked: {
        print("pressed", mouse.button)
        if (mouse.button == Qt.LeftButton) {
          textinput.forceActiveFocus()
        } else if (pressedButtons === Qt.RightButton) {
          textinput.forceActiveFocus()
          uiManager.menuFlottantText.ouvre(textinput)
        }
      }

      //      onPressAndHold: {
      //        rectangle.state = "selected"
      ////        mouse.accepted=true
      //      }
      //
      //      onEntered: {
      //        print("entered")
      //        if (pressed) {
      //          print("entered and pressed")
      //          rectangle.state = "selected"
      //        }
      //      }

      //      onPositionChanged: {
      //        print(mouse.x, mouse.y)
      //      }

    }
    TextArea {
      padding: 0

      focus: true
      id: textinput
      onTextChanged: {
        if (text != display) {
          edit = text
          root.forceLayout()
        }
      }
      Component.onCompleted: {
        text = display
      }


      function changeCase(event) {
        var obj
        var iLine = row * root.columns + column
        switch (event.key) {
          case Qt.Key_Right: {
            iLine = iLine + 1;
            break
          }
          case Qt.Key_Left: {
            iLine = iLine - 1;
            break
          }
          case Qt.Key_Up: {
            iLine = iLine - root.columns;
            break
          }
          case Qt.Key_Down: {
            iLine = iLine + root.columns;
            break
          }
        }
        if (iLine >= size) {
          return
        } else if (iLine < 0) {
          return
        }

        obj = root.getItem(iLine)

        if (obj != rectangle) {
          obj.tinput.forceActiveFocus()
        }
      }

      function isFirstLine() {
        var fl = text.split('\n')[0].length
        return cursorPosition <= fl
      }

      function isLastLine() {
        return !text.slice(cursorPosition, length).includes("\n")

      }

      Keys.onPressed: {
        var isMove = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key)

        if ((isMove && (event.modifiers & Qt.ControlModifier)) ||
          (event.key == Qt.Key_Right && cursorPosition == length) ||
          (event.key == Qt.Key_Left && cursorPosition == 0) ||
          (event.key == Qt.Key_Up && isFirstLine()) ||
          (event.key == Qt.Key_Down && isLastLine())) {
          changeCase(event)
          event.accepted = true
        } else {
          moreKeys(event)
        }
      }

      onPressed: {
        if (event.buttons === Qt.MiddleButton) {
          //      deleteRequested(control)
        } else if (event.buttons === Qt.RightButton) {
          uiManager.menuFlottantText.ouvre(textinput)
        }
      }

      function setStyleFromMenu(data) {
        if (data['type'] == "color") {
          color = data['value']
        } else if (data['type'] == "underline") {
          color = data['value']
          font.underline = true
        }
      }

      function moreKeys(event) {
        //        print("morekeys")
      }

    }
  }

  function getRowAndCol(idx) {
    var newRow = (idx / columns) >> 0
    var newCol = idx % columns
    return [newRow, newCol]
  }

  function selectCell(obj) {
    obj.state = obj.state == "selected" ? null : "selected"
    if (obj.state == "selected") {
      if (!selectedCells.includes(obj)) {
        root.selectedCells.push(obj)
      }
    } else {
      selectedCells.pop(obj)
    }

    print("selected cell", root.selectedCells)
  }

  function unSelectAll(obj) {
    for (var i of root.selectedCells) {
      i.state = null
    }
    root.selectedCells.length = 0
    print("unselectAll", root.selectedCells)
  }

  function getItem(idx) {

    var [newRow, newCol] = getRowAndCol(idx)

    var heights = []
    var widths = []
    var first = contentItem.childAt(1, 1)

    var current = first

    for (var i of Array(root.columns)) {
      widths.push(current.width)
      current = contentItem.childAt(current.x + current.width + root.columnSpacing, current.y)
    }
    current = first
    for (var i of Array(root.rows)) {
      heights.push(current.height)
      current = contentItem.childAt(current.x, current.y + current.height + root.rowSpacing)
    }
    var new_x = 0
    for (var i of Array(newCol).keys()) {
      new_x += (widths[i] + columnSpacing)
    }

    var new_y = 0
    for (var i of Array(newRow).keys()) {
      new_y += (heights[i] + rowSpacing)
    }
    var res = contentItem.childAt(new_x, new_y)
    return res

  }
}