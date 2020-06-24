import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
  id: root
  /* beautify preserve:start */
  property var referent
  property var menu: uiManager.menuFlottantAnnotationText

  property int pointSizeStep: 1
  property int moveStep: 5
  property int fontSizeFactor: annot.pointSize ? annot.pointSize : 0 //uiManager.annotationCurrentTextSizeFactor
  /* beautify preserve:end */

  //size and pos
  height: contentHeight
  padding: 0
  width: contentWidth + 5
  focus: parent.focus

  color: annot.fgColor ? annot.fgColor : "black"
  font.underline: annot.underline ? annot.underline : false
  text: annot.text ? annot.text : ""
  font.pixelSize: (referent.height / fontSizeFactor) | 0
  selectByMouse: true

  Component.onCompleted: {
    if (!annot.pointSize) {
      fontSizeFactor = uiManager.annotationCurrentTextSizeFactor
    } // casse le binding mais evite le loop, donc on laisse pour le moment
    forceActiveFocus() // donc création
    timerRemove.running = true
  }

  onFontSizeFactorChanged: {
    if (annot.pointSize == fontSizeFactor) {
      return
    }
    // attention on stock fontSizeFactor dans du pointSize :le nom dans la ddb est nul :-)
    var res = ddb.setStyle(annot.styleId, {
      "pointSize": root.fontSizeFactor //uiManager.annotationCurrentTextSizeFactor
    })
    uiManager.annotationCurrentTextSizeFactor = root.fontSizeFactor
  }

  // other atributes

  Timer {
    id: timerRemove
    objectName: "timerRemove"
    interval: 3000
    running: false
    repeat: false
    onTriggered: {
      if (text == "") {
        root.referent.model.removeRow(annot.id, true)
      }
    }
  }

  background: Rectangle {
    anchors.fill: parent
    color: annot.bgColor ? annot.bgColor : "blue"
    border.color: parent.focus ? "#21be2b" : "transparent"
    opacity: ddb.annotationTextBGOpacity
  }

  onFocusChanged: {
    if (focus) {
      cursorPosition = text.length //  toujours curseur à la fin quand focus

    } else {
      if (!text) {
        timerRemove.running = true
      }
    }
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
      parent.move(-moveStep, 0)
    } else if (key == Qt.Key_Right) {
      parent.move(moveStep, 0)
    } else if (key == Qt.Key_Up) {
      parent.move(0, -moveStep)
    } else if (key == Qt.Key_Down) {
      parent.move(0, moveStep)
    }
  }

  onTextChanged: {
    edit = {
      "id": annot.id,
      "text": text
    }
  }

  function checkPointIsDraw(mx, my) {
    return false
  }

}