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
  /* beautify preserve:start */
  property var selectedCells: []
  property var mouseArea: bigMouse
  property var currentSelectedCell
  /* beautify preserve:end */
  MouseArea {
    id: bigMouse
    x: root.x
    y: root.y
    width: contentItem.childrenRect.width
    height: contentItem.childrenRect.height
    preventStealing: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    z: 2 // par dessus les delegate
    propagateComposedEvents: true

    //    pressAndHoldInterval: 300

    onPositionChanged: {
      var tempItem = root.contentItem.childAt(mouse.x, mouse.y)
      if (!root.currentSelectedCell && (mouse.modifiers != Qt.ControlModifier)) {
        // nouvelle sélection après que clique ait été relaché
        // gardé si ctrl enfoncé
        root.unSelectAll()
      }
      if (!containsMouse // on ne fait rien en dehors de la zone
        ||
        mouse.buttons != Qt.LeftButton // le même on fait rien
        ||
        (tempItem === root.currentSelectedCell) // doit être une des cell
        ||
        !tempItem.isTableDelegate) // pas deleguate on prend pas
      {
        return
      } else if (tempItem === selectedCells[selectedCells.length - 2]) {
        // si c un recul  on déselect celui en cours et change current
        root.selectCell(root.currentSelectedCell)
        root.currentSelectedCell = tempItem
      } else {
        //cas simple : nouveau = on ajoute.
        root.currentSelectedCell = tempItem
        root.selectCell(root.currentSelectedCell)
      }
    }

    onClicked: {

      if (root.currentSelectedCell) {
        root.currentSelectedCell = null
        mouse.accepted = true
      } else if (mouse.button == Qt.LeftButton) {
        if (root.selectedCells.length > 0) {
          root.unSelectAll()
        }
        mouse.accepted = false
      } else if (mouse.button == Qt.RightButton) {
        var cel = root.contentItem.childAt(mouse.x, mouse.y)
        if (root.selectedCells.includes(cel)) {
          uiManager.menuFlottantTableau.ouvre(root)
        } else {
          root.unSelectAll()
          mouse.accepted = false
        }
      }
    }
  }

  delegate: Rectangle {

    id: rectangle
    property alias tinput: textinput
    implicitWidth: textinput.contentWidth + 10
    implicitHeight: textinput.contentHeight + 10
    focus: true
    property bool isTableDelegate: true //juste pour vérifier le type
    color: background ? background : "white"
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
      //      preventStealing: true

      onClicked: {
        if (mouse.button == Qt.LeftButton) {
          textinput.forceActiveFocus()
        } else if (mouse.button === Qt.RightButton) {
          textinput.forceActiveFocus()
          uiManager.menuFlottantText.ouvre(textinput)
        }
      }

    }

    function setBackgroundColor(value) {
      background = value
    }

    function setForegroundColor(value) {
      foreground = value
    }

    function setUnderline(value) {
      underline = value
    }
    TextArea {
      padding: 0
      color: foreground
      font.underline: underline ? underline : false
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
        // pour tinput
        if (data['type'] == "color") {
          foreground = data['value']
          underline = false
        } else if (data['type'] == "underline") {
          foreground = data['value']
          underline = true
        }
      }

      function moreKeys(event) {}

    }
  }

  function setStyleFromMenu(data) {
    // pour rectangle
    if (data["type"] == "cell_color") {
      for (var i of selectedCells) {
        i.setBackgroundColor(data["value"])
      }
    } else if (data['type'] == "color") {
      for (var i of selectedCells) {
        i.setForegroundColor(data["value"])
        i.setUnderline(false)
      }
    } else if (data['type'] == "underline") {
      for (var i of selectedCells) {
        i.setForegroundColor(data["value"])
        i.setUnderline(true)
      }
    }
    unSelectAll()
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

    //    print("selected cell", root.selectedCells)
  }

  function unSelectAll(obj) {
    // désectionne toutes les cases
    for (var i of Array(root.contentItem.children.length).keys()) {
      var ite = root.contentItem.children[i]
      if (ite.isTableDelegate) {
        ite.state = ""
      }
    }

    root.selectedCells.length = 0
    root.currentSelectedCell = null
    //    print("unselectAll", root.selectedCells)
  }

  function getCells() {
    // liste les cellss
    var res = []
    for (var i of Array(root.contentItem.children.length).keys()) {
      var ite = root.contentItem.children[i]
      if (ite.isTableDelegate) {
        res.push(ite)
      }
    }
    return res
  }

  function getItem(idx) {
    // retourn une cell par son index
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
    var res = root.contentItem.childAt(new_x, new_y)
    return res

  }

}