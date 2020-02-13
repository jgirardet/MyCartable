import QtQuick 2.12
import QtQuick.Controls 2.12
Rectangle {
  id: control
  property QtObject referent
  property real relativeX
  property real relativeY
  property real relativeWidth: 0
  property real relativeHeight: 0
  property int ddbId: 0

  signal deleteRequested(QtObject anotObj)

  height: relativeHeight * referent.height
  width: relativeWidth * referent.width
  x: relativeX * referent.width
  y: relativeY * referent.height

  color: Qt.rgba(0.5, 0.4, 0.2, 0.4)

  Component.onCompleted: deleteRequested.connect(referent.deleteAnnotation)

  MouseArea {
    objectName: "mouseArea"
    anchors.fill: parent
    acceptedButtons: Qt.Right | Qt.MiddleButton
    onPressed: {
      if (mouse.buttons === Qt.MiddleButton) {
        deleteRequested(control)
      } else if (mouse.buttons === Qt.RightButton) {
      print("dabs mouse")
        menuflotant.popup()
        mouse.accepted=false
      }
    }
    MenuFlottant {
      id: menuflotant
    }
  }
}