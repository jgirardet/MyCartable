import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/menu"

Rectangle {
  id: root
  property QtObject referent
  /* beautify preserve:start */
  property var model
  property var objStyle
  /* beautify preserve:end */

  property real relativeX: model.relativeX
  property real relativeY: model.relativeY
  property real relativeWidth: model.relativeWidth
  property real relativeHeight: model.relativeHeight
  property int ddbId: model.id

  signal deleteRequested(QtObject anotObj)
  property bool pushed: false // qand ajouté dans annotations

  Binding {
    when: pushed
    target: root
    property: 'relativeWidth'
    value: root.model.relativeWidth
  }
  Binding {
    when: pushed
    target: root
    property: 'relativeHeight'
    value: root.model.relativeHeight
  }
  height: relativeHeight * referent.height
  width: relativeWidth * referent.width
  x: relativeX * referent.width
  y: relativeY * referent.height

  color: objStyle.bgColor
  opacity: 0.2

  MouseArea {
    objectName: "mouseArea"
    anchors.fill: parent
    acceptedButtons: Qt.RightButton | Qt.MiddleButton
    onPressed: {
      if (mouse.button === Qt.MiddleButton) {
        deleteRequested(root) // tested in tst_annotableimage
      } else if (mouse.button === Qt.RightButton) {
        uiManager.menuFlottantStabylo.ouvre(root)
        mouse.accepted = true
      }
    }
  }
  Component.onCompleted: {
    deleteRequested.connect(referent.parent.deleteAnnotation)
  }

  function setStyleFromMenu(data) {
    var res = ddb.setStyle(objStyle.id, data["style"])
    if (res) {
      objStyle = res
    }
  }
}