import QtQuick 2.14
import QtQuick.Controls 2.14

Loader {
  id: root
  /* beautify preserve:start */
  property var referent
  property var mouse: mousearea
  property bool held: false
  anchors.top: parent.top
  anchors.topMargin: annot.y * parent.implicitHeight
  anchors.left: parent.left
  anchors.leftMargin: annot.x * parent.implicitWidth
  states: [
    State {
      name: "dragging"
      when: root.held
      AnchorChanges {
          target: root
          anchors.top: undefined
          anchors.left: undefined
      }
    }
  ]
  focus: parent.currentAnnotation == root

  MouseArea {
    id: mousearea
    anchors.fill: parent
//    Rectangle{
//      border.width:0
//      anchors.fill: parent
//      color: "green"
//      opacity: 0.4
//    }
    z:1

    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    hoverEnabled: true
    onEntered: {
    root.parent.currentAnnotation = root
    }
    //    property point startPosition
    preventStealing: true
    onPressed: {
      if (mouse.buttons === Qt.MiddleButton) {
        root.parent.model.removeRow(index)
      } else if (mouse.buttons === Qt.RightButton) {
        uiManager.menuFlottantText.ouvre(root.item)
          mouse.accepted = true
      } else if (mouse.buttons === Qt.LeftButton && (mouse.modifiers & Qt.ControlModifier)) {
        root.held = true
        //        mouse.accepted = true
      }
      else {
              mouse.accepted = false
            }
    }
    onReleased: {
      if (held) {
        saveMove()
        root.held = false
      }

    }
    drag.target: held ? root : null
    drag.smoothed: false
  }
  function move(dx, dy) {
    anchors.leftMargin+=dx
    anchors.topMargin+=dy
    saveMove()
  }

  function saveMove() {
    edit = {"id":annot.id, "x" : root.x / root.parent.implicitWidth,
        "y" : root.y / root.parent.implicitHeight}
  }

  Component.onCompleted: {
    root.setSource(`qrc:/qml/annotations/${annot.classtype}.qml`, {
      "referent": referent,
    })
//    print(x, y, anchors.topMargin, anchors.leftMargin)
  }

}