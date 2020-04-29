import QtQuick 2.12
import QtQuick.Controls 2.12
import "qrc:/qml/menu"

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

  color: Qt.rgba(0.5, 0.4, 0.2)
  opacity: 0.2

  MouseArea {
    objectName: "mouseArea"
    anchors.fill: parent
    acceptedButtons: Qt.RightButton | Qt.MiddleButton
    onPressed: {
      if (mouse.button === Qt.MiddleButton) {
        deleteRequested(control) // tested in tst_annotableimage
      } else if (mouse.button === Qt.RightButton) {
        uiManager.menuFlottantStabylo.ouvre(control)
        mouse.accepted = true
      }
    }

  }
  Component.onCompleted: deleteRequested.connect(referent.deleteAnnotation)

  function setStyleFromMenu(data) {
    ddb.updateAnnotation(control.ddbId, data)
    control[data.type] = data.value
  }
}