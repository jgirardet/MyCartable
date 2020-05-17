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
  property int moveStep: 5
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
    } else if ([Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].includes(event.key) && (event.modifiers & Qt.ControlModifier)) {
      move(event.key)
      event.accepted = true
    }
  }

  function move(key) {
    if (key == Qt.Key_Left) {
      root.x -= moveStep
    } else if (key == Qt.Key_Right) {
      root.x += moveStep
    } else if (key == Qt.Key_Up) {
      root.y -= moveStep
    } else if (key == Qt.Key_Down) {
      root.y += moveStep
    }

    ddb.updateAnnotation(root.ddbId, {
      "relativeX": root.x / root.referent.implicitWidth,
      "relativeY": root.y / root.referent.height
    })
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

  MouseArea {
    id: mousearea
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    hoverEnabled: true
    onHoveredChanged: hovered ? root.focus = true : null
    property bool held
    //    property point startPosition
    preventStealing: true
    onPressed: {
      if (mouse.buttons === Qt.MiddleButton) {
        deleteRequested(root)
        mouse.accepted = true
      } else if (mouse.buttons === Qt.RightButton) {
        uiManager.menuFlottantText.ouvre(root)
        mouse.accepted = true
      } else if (mouse.buttons === Qt.LeftButton && (mouse.modifiers & Qt.ControlModifier)) {
        held = true
        mouse.accepted = true
      } else {
        mouse.accepted = false
      }
    }
    onReleased: {
      if (held) {
        held = false
        ddb.updateAnnotation(root.ddbId, {
          "relativeX": root.x / root.referent.implicitWidth,
          "relativeY": root.y / root.referent.height
        })
      }

    }
    drag.target: root
    //    drag.threshold: 0
    drag.smoothed: false
  }
}
//}