import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  property int previousCursorPosition
  /* beautify preserve:end */

  width: sectionItem.width - 20
  height: contentHeight + 30
  font.pointSize: 12
  onSectionIdChanged: {
    var data = ddb.loadSection(sectionId)
    text = data.content
    cursorPosition = data.curseur
  }

  background: Rectangle {
    anchors.fill: parent
    color: "white"
  }
  onCursorPositionChanged: {
    previousCursorPosition = cursorPosition
  }
  font.family: "Courier"
  Keys.onPressed: {
    var new_data = ddb.updateEquation(sectionId, text, cursorPosition, JSON.stringify(event))
    root.text = new_data.content
    root.cursorPosition = new_data.curseur
    event.accepted = true

  }
  onSelectionStartChanged: {
    if (!ddb.isEquationFocusable(text, selectionStart)) {
      cursorPosition = previousCursorPosition
    }
  }

}