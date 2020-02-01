import QtQuick 2.12
import QtQuick.Controls 2.12

TextField {
  id: control
  property QtObject referent
  property real relativeX
  property real relativeY

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
  onHoveredChanged: hovered ? focus = true : null
  onPressed: event.buttons === Qt.MiddleButton ? control.destroy() : null
  Component.onDestruction: {
    if (referent.annotations) {
      let obj = referent.annotations.indexOf(control)
      referent.annotations.splice(obj, 1)
    }
  }
}