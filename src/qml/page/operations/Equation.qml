import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  property int sectionId
  width: base.width - 20
  height: contentHeight + 30
  font.pointSize: 12
  /* beautify preserve:start */
  property var base
  property int previousCursorPosition
  /* beautify preserve:end */
  onSectionIdChanged: {
    var data = ddb.loadSection(sectionId)
    text = data.content
    cursorPosition = data.curseur
    print("cursopr pose", data.curseur, cursorPosition)
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
  onPressed: {
    print(event.x, event.y)
  }
  onSelectionStartChanged: {
    if (!ddb.isEquationFocusable(text, selectionStart)) {
      cursorPosition = previousCursorPosition
    }
  }

}