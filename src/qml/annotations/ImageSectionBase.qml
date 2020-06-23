import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/menu"
import "qrc:/qml/annotations"

Image {
  id: root
  /* beautify preserve:start */
    property int sectionId
    property var sectionItem
    property var model
    property MouseArea mousearea: mousearea
    property var currentAnnotation
   /* beautify preserve:end */
  asynchronous: true
  fillMode: Image.PreserveAspectCrop
  sourceSize.width: sectionItem ? sectionItem.width : 0
  cache: false

  Component.onCompleted: {
    var content = ddb.loadSection(sectionId)
    var path = content.path.toString()
    root.source = path.startsWith("file:///") || path.startsWith("qrc:") ? content.path : "file:///" + path
  }

  MouseArea {
    id: mousearea
    objectName: "mousearea"
    anchors.fill: root
    preventStealing: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton

    onPressed: {
      if (pressedButtons === Qt.RightButton) {
        if (mouse.modifiers == Qt.ControlModifier) {
          canvas.startDraw(true)
        } else {
          uiManager.menuFlottantImage.ouvre(root)
        }
      } else if (pressedButtons === Qt.LeftButton) {
        if (mouse.modifiers == Qt.ControlModifier) {
          root.model.addAnnotation(mouse.x, mouse.y, root.width, root.height)
        } else {
          if (uiManager.annotationCurrentTool == "text") {
            root.model.addAnnotation(mouse.x, mouse.y, root.width, root.height)
          } else {
            canvas.startDraw()
          }
        }
        mouse.accepted = true
      }
    }
    onReleased: {
      if (canvas.painting) {
        canvas.endDraw(root.sectionId)
      }
    }
    onPositionChanged: {
      if (canvas.painting) {
        canvas.requestPaint()
      }
    }

  }
  Repeater {
    id: repeater
    objectName: "repeater"
    anchors.fill: root
    model: root.status == Image.Ready ? root.model : 0
    delegate: BaseAnnotation {
      id: repdelegate
      referent: root
    }
  }

  CanvasFactory {
    id: canvas
    objectName: "canvasFactory"
    mouse: mousearea
    anchors.fill: root

  }

  function reloadImage() {
    // not tested
    var oldSource = root.source
    root.source = ""
    root.source = oldSource
  }

  function setStyleFromMenu(datas) {
    if ("style" in datas) {
      if ("pointSize" in datas['style']) {
        uiManager.annotationDessinCurrentLineWidth = datas['style']["pointSize"]
      }
      if ("fgColor" in datas['style']) {
        uiManager.annotationDessinCurrentStrokeStyle = datas['style']["fgColor"]
      }
      if ("tool" in datas['style']) {
        var newTool = datas['style']["tool"]
        uiManager.annotationCurrentTool = newTool
        if (newTool == "text") {
          uiManager.annotationDessinCurrentTool = "fillrect"
        } else {
          uiManager.annotationDessinCurrentTool = newTool
        }
      }

    }
  }

}