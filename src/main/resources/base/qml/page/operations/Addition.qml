import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"

GridView {
  id: root
  property int position
  property int sectionId
  /* beautify preserve:start */
        property var base
        /* beautify preserve:end */
  //        anchors.fill: parent
  width: cellWidth * model.columns
  height: cellHeight * model.rows
  cellWidth: 50
  cellHeight: 50
  keyNavigationEnabled: false
  onCurrentItemChanged: {
    currentItem.textinput.forceActiveFocus()
    print("currentindex", currentIndex)
  }
  delegate: Rectangle {
    height: root.cellHeight
    width: root.cellWidth
    property TextInput textinput: input



      id: delegateRectangle
      color: "white"
      TextField {
        bottomPadding: index >= root.model.columns ? 5: 0
        topPadding: index >= root.model.columns && index < root.model.columns*2 ? 0: 5
        id: input
        focus: delegateRectangle.GridView.isCurrentItem
        anchors.fill: parent
        text: display
        color: index > root.model.columns ? "black" : "red"
        horizontalAlignment: TextInput.AlignHCenter
        verticalAlignment: index >= root.model.columns*(root.model.rows-1) ? TextInput.AlignVCenter :
                           index < root.model.columns ? TextInput.AlignBottom: TextInput.AlignTop
        readOnly: root.model.readOnly(index)
        validator: IntValidator {
          bottom: 0;top: 9;
        }
        onTextEdited: {
          root.model.autoMoveNext(index)
          currentItem.textinput.focus = true
        }
        onFocusChanged: {
          if (focus && !readOnly) {
            selectAll()
            root.currentIndex = index
          }
        }
        Keys.onPressed: {
          //                  root.model.moveCursor(index, event.key)
          root.model.moveCursor(index, event.key)
          event.accepted = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key)
        }

        background: BorderRectangle {
        color: delegateRectangle.color
          borderColor: index > root.count - root.model.columns - 1 ? "black" : "white"
          borderTop: -2
        }

      }

  }

  Binding on currentIndex {
    when: model.cursorChanged
    value: model.cursor
  }
}