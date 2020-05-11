import QtQuick 2.12
import QtQuick.Controls 2.12
//import "menu"

TextField {
  id: root
  /* beautify preserve:start */
  property var model
  property var objStyle
  /* beautify preserve:end */
  property QtObject referent

  property real relativeX: model.relativeX
  property real relativeY: model.relativeY
  property int ddbId: model.id
  property int pointSizeStep: 2

  signal deleteRequested(QtObject anotObj)

  //size and pos
  height: contentHeight
  padding: 0
  width: contentWidth + 5
  x: relativeX * referent.implicitWidth
  y: relativeY * referent.height
  color: objStyle ? objStyle.fgColor : "orange"
  font.underline: objStyle.underline
  text: model.text

  font.pointSize: objStyle.pointSize ? objStyle.pointSize : 12.0
  // other atributes
  background: Rectangle {
    implicitWidth: parent.width
    implicitHeight: parent.height
    color: objStyle.bgColor
    border.color: root.focus ? "#21be2b" : "transparent"
  }
  selectByMouse: true
  hoverEnabled: true
  // slots
  onFocusChanged: {

    focus ? cursorPosition = text.length : null //  toujours curseur à la fin quand focus
    if (!focus && !text) {
      deleteRequested(root)
    }
    focus ? uiManager.menuTarget = root : null
  }
  Keys.onPressed: {
    if ((event.key == Qt.Key_Plus) && (event.modifiers & Qt.ControlModifier)) {
      var res = ddb.setStyle(objStyle.id, {
        "pointSize": root.font.pointSize + pointSizeStep
      })
      if (res) {
        root.objStyle = res
      }
      event.accepted = true
    } else if ((event.key == Qt.Key_Minus) && (event.modifiers & Qt.ControlModifier)) {
      var res = ddb.setStyle(objStyle.id, {
        "pointSize": root.font.pointSize - pointSizeStep
      })
      if (res) {
        root.objStyle = res
      }
      event.accepted = true
    }
  }
  onHoveredChanged: hovered ? focus = true : null
  onPressed: {
    if (event.buttons === Qt.MiddleButton) {
      deleteRequested(root)
    } else if (event.buttons === Qt.RightButton) {
      uiManager.menuFlottantText.ouvre(root)
    }
  }
  onTextChanged: ddb.updateAnnotation(ddbId, {
    "text": text
  })

  Component.onCompleted: {
    deleteRequested.connect(referent.deleteAnnotation)
  }

  function setStyleFromMenu(data) {
    var res = ddb.setStyle(objStyle.id, data["style"])
    if (res) {
      objStyle = res
    }
  }
}