import QtQuick 2.12
import QtQuick.Controls 2.12
import "menu"

TextField {
  id: control
  property QtObject referent
  property real relativeX
  property real relativeY
  property int ddbId

  signal deleteRequested(QtObject anotObj)
  //size and pos
  height: contentHeight
  padding: 0
  width: contentWidth + 5
  x: relativeX * referent.width
  y: relativeY * referent.height

  // other atributes
  background: Rectangle {
    implicitWidth: parent.width
    implicitHeight: parent.height
    color: "transparent"
    border.color: control.focus ? "#21be2b" : "transparent"
  }
  selectByMouse: true
  hoverEnabled: true

  // slots
  onFocusChanged: focus ? cursorPosition = text.length : null
  onHoveredChanged: hovered ? focus = true : null
  onPressed: {
      if (event.buttons === Qt.MiddleButton) {
          deleteRequested(control)
      } else if (event.buttons === Qt.RightButton) {
        menuflotant.popup()
      }
  }
  onTextChanged: ddb.updateAnnotation(ddbId, {"type":"text","value":text})

  Component.onCompleted: deleteRequested.connect(referent.deleteAnnotation)

  function setStyle(data) {
    control.font.underline = (data.type == "underline")
    control.color = data.value
    ddb.updateAnnotation(control.ddbId, data)
  }

  MenuFlottant {
    id: menuflotant
    objectName: "menuflottant"
    editor: control
    }
}