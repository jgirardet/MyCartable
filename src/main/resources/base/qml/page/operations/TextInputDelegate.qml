import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"


TextField {
    id: input
    property QtObject model: parent.model
    focus: parent.GridView.isCurrentItem
    anchors.fill: parent
    text: display
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
        print(index)
        parent.GridView.view.currentIndex = index
      }
    }
    Keys.onPressed: {
      model.moveCursor(index, event.key)
      event.accepted = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key)
      var numPressed = [Qt.Key_0,Qt.Key_1,Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5,Qt.Key_6,Qt.Key_7,Qt.Key_8,Qt.Key_9].includes(event.key)
      if (numPressed)
        {
        selectAll()
        }
//      event.accepted = numPressed
    }

    background: BorderRectangle {
      color: input.parent.color
      borderColor: model.isResultLine(index) ? "black" : input.parent.color
      borderTop: -2
    }

  }

