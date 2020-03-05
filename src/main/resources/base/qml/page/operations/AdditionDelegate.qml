import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"

Rectangle {
  id: root
  property alias model: input.model
  property alias textinput: input

  property GridView grid: GridView.view
  height: grid.cellHeight
  width: grid.cellWidth

  color: "white"
  TextField {
    id: input
    property QtObject model
    bottomPadding: model.isRetenueLine(index) ? 0 : 5
    topPadding: model.isMiddleLine(index) ? 0 : 5
    focus: root.GridView.isCurrentItem
    anchors.fill: parent
    text: display
    color: model.isRetenueLine(index) ? "red" : "black"
    horizontalAlignment: TextInput.AlignHCenter
    verticalAlignment: model.isResultLine(index) ? TextInput.AlignVCenter : model.isRetenueLine(index) ? TextInput.AlignBottom : TextInput.AlignTop
    readOnly: model.readOnly(index)
    validator: IntValidator {
      bottom: 0;top: 9;
    }
    onTextEdited: {
      edit = text
      model.autoMoveNext(index)
    }
    onFocusChanged: {
      if (focus && !readOnly) {
        selectAll()
        grid.currentIndex = index
      }
    }
    Keys.onPressed: {
      model.moveCursor(index, event.key)
      event.accepted = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key)
    }

    background: BorderRectangle {
      color: root.color
      borderColor: model.isResultLine(index) ? "black" : root.color
      borderTop: -2
    }


  }

}