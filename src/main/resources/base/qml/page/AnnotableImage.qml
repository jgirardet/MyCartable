import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
FocusScope {
  id: root
  /* beautify preserve:start */
    property alias content: img.content
    property var base
    property Image image: img
    property var annotations: []
   /* beautify preserve:end */
  height: img.height
  width: img.width

  function initZones() {
    for (var z of content.annotations) {
      let newObject
      switch (z.classtype) {
        case "Stabylo": {
          newObject = img.stabyloRectangle.createObject(root, {
            "relativeX": z.x,
            "relativeY": z.y,
            "relativeWidth": z.width,
            "relativeHeight": z.height,
            "referent": img
          })
          break;
        }
        case "Annotation": {
          newObject = img.annotationInput.createObject(root, {
            "relativeX": z.x,
            "relativeY": z.y,
            "text": z.text,
            "referent": img
          })
          break;
        }
      }
      if (newObject != undefined) {
        root.annotations.push(newObject)
      }
    }
  }

  Component.onCompleted: initZones()
  onAnnotationsChanged: {
    print(value)
  }

  Image {
    id: img
    /* beautify preserve:start */
        property var content


        // propiete a ne pas oublier à la declaration
        property QtObject mouseArea: mouseArea
        readonly property var annotationInput: Qt.createComponent(
            "qrc:/qml/page/AnnotationInput.qml")
        readonly property var stabyloRectangle: Qt.createComponent(
            "qrc:/qml/page/StabyloRectangle.qml")
       /* beautify preserve:end */
    asynchronous: true
    fillMode: Image.PreserveAspectFit
    source: 'file://' + content.content
    sourceSize.width: base.width
    //slot
    function addAnnotation(mouseEvent, parent) {
      let newObject = annotationInput.createObject(root, {
        "relativeX": mouseEvent.x / img.implicitWidth,
        "relativeY": mouseEvent.y / img.implicitHeight,
        "referent": img
      })
      root.annotations.push(newObject)
      newObject.forceActiveFocus()
      return newObject
    }

    function initZone(mouseEvent) {
      var new_rec = stabyloRectangle.createObject(img, {
        "relativeX": mouseEvent.x / img.implicitWidth,
        "relativeY": mouseEvent.y / img.implicitHeight,
        "referent": img
      })
      return new_rec
    }

    function updateZone(mouseEvent, rec) {
      const new_rel_height = (mouseEvent.y - rec.y) / img.height
      const new_rel_width = (mouseEvent.x - rec.x) / img.implicitWidth
      rec.relativeHeight = new_rel_height >= 0 ? new_rel_height : 0
      rec.relativeWidth = new_rel_width >= 0 ? new_rel_width : 0
      return rec
    }

    function storeZone(rec) {
      if (rec.relativeWidth > 0 && rec.relativeHeight > 0) {
        annotations.push(rec)
      }
    }

  }
  MouseArea {
    id: mouseArea
    objectName: "mouseArea"
    anchors.fill: root
    property QtObject temp_rec
    preventStealing: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    onPressed: {
      if (pressedButtons === Qt.LeftButton) {
        temp_rec = img.initZone(mouse)
      } else if (pressedButtons === Qt.RightButton) {
        base.focus = true
        img.addAnnotation(mouse, mouseArea)
        mouse.accepted = false
      }
    }

    onReleased: {
      img.storeZone(temp_rec)
      temp_rec = null
    }
  }
}