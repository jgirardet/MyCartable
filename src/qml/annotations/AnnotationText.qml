import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  /* beautify preserve:start */
//  property var annotation
  property var referent
  property var index
  property var menu: uiManager.menuFlottantAnnotationText

  property int pointSizeStep: 1
  property int moveStep: 5
  property int fontSizeFactor: annot.pointSize ? annot.pointSize : 0 //uiManager.annotationCurrentTextSizeFactor

  //size and pos
  height: contentHeight
  padding: 0
  width: contentWidth + 5

  color: annot.fgColor ? annot.fgColor : "black"
  font.underline: annot.underline ? annot.underline : false
  text: annot.text ? annot.text : ""
  focus: parent.focus
  //  Compo

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

  font.pixelSize: (referent.height / fontSizeFactor) | 0

  // other atributes

  Timer {
    id: timerRemove
    interval: 3000;running: false;repeat: false
    onTriggered: {
      if (text == "") {
        root.referent.model.removeRow(annot.id, true)
      }
    }
  }
  Component.onCompleted: {
    if (!annot.pointSize) {
      fontSizeFactor = uiManager.annotationCurrentTextSizeFactor
    }
    forceActiveFocus()
    timerRemove.running = true
  }
  background: Rectangle {
    anchors.fill: parent
    color: annot.bgColor ? annot.bgColor : "blue"
    border.color: parent.focus ? "#21be2b" : "transparent"
    opacity: ddb.annotationTextBGOpacity
  }
  selectByMouse: true

    onFocusChanged: {
      if (focus) {
        cursorPosition = text.length //  toujours curseur à la fin quand focus
//      uiManager.menuTarget = root

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

         edit= {"id": annot.id, "text":text}
  }

  function checkPointIsDraw(mx, my) {
    return false
  }



}