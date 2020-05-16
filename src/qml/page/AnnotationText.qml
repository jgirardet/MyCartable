import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  /* beautify preserve:start */
  property var model
  property var objStyle
  /* beautify preserve:end */
  property QtObject referent

  property real relativeX: model.relativeX
  property real relativeY: model.relativeY
  property int ddbId: model.id
  property int pointSizeStep: 1
  property int fontSizeFactor: objStyle.pointSize ? objStyle.pointSize : 0 //uiManager.annotationCurrentTextSizeFactor
  signal deleteRequested(QtObject anotObj)

  //size and pos
  height: contentHeight
  padding: 0
  width: contentWidth + 5
  x: relativeX * referent.implicitWidth
  y: relativeY * referent.height
  color: objStyle.fgColor ? objStyle.fgColor : "black"
  font.underline: objStyle.underline ? objStyle.underline : false
  text: model.text

  onFontSizeFactorChanged: {
    if (objStyle.pointSize == fontSizeFactor) {
      return
    }
    // attention on stock fontSizeFactor dans du pointSize :le nom dans la ddb est nul :-)
    var res = ddb.setStyle(objStyle.id, {
      "pointSize": root.fontSizeFactor //uiManager.annotationCurrentTextSizeFactor
    })
    if (res) {
      root.objStyle = res
    }
    uiManager.annotationCurrentTextSizeFactor = root.fontSizeFactor
  }

  font.pixelSize: (referent.height / fontSizeFactor) | 0

  // other atributes
  Component.onCompleted: {
    if (!objStyle.pointSize) {
      fontSizeFactor = uiManager.annotationCurrentTextSizeFactor
    }
    deleteRequested.connect(referent.parent.deleteAnnotation)

  }
  background: Rectangle {
    implicitWidth: parent.width
    implicitHeight: parent.height
    color: objStyle.bgColor ? objStyle.bgColor : "transparent"
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
      root.fontSizeFactor -= pointSizeStep
      event.accepted = true
    } else if ((event.key == Qt.Key_Minus) && (event.modifiers & Qt.ControlModifier)) {
      root.fontSizeFactor += pointSizeStep
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

  function setStyleFromMenu(data) {
    var res = ddb.setStyle(objStyle.id, data["style"])
    if (res) {
      objStyle = res
    }
  }
}