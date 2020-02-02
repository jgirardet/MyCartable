import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
FocusScope {
  id: root
  /* beautify preserve:start */
    property int sectionId
    property var base
    property var annotations: []
    property alias image: img
    readonly property var annotationText: Qt.createComponent("qrc:/qml/page/AnnotationText.qml")
    readonly property var stabyloRectangle: Qt.createComponent("qrc:/qml/page/StabyloRectangle.qml")
   /* beautify preserve:end */

  //doit rester comme ça pour les annotations +++
  height: img.height
  width: img.width

  Component.onCompleted: {
    var content = ddb.loadSection(sectionId)
    img.source = 'file://' + content.content
    initZones(content.annotations)
  }

  function addAnnotation(mouseEvent) {

    let newObject = annotationText.createObject(root, {
      "relativeX": mouseEvent.x / img.implicitWidth,
      "relativeY": mouseEvent.y / img.implicitHeight,
      "referent": root
    })
    var newId = ddb.addAnnotation({
      "relativeX": newObject.relativeX,
      "relativeY": newObject.relativeY,
      "section": parseInt(root.sectionId),
      "classtype": "AnnotationText",
      "text": ""
    })
    if (newId) {
      newObject.ddbId = newId
      annotations.push(newObject)
      newObject.forceActiveFocus()
      return newObject
    }

  }

  function createZone(mouseEvent) {
    var new_rec = stabyloRectangle.createObject(root, {
      "relativeX": mouseEvent.x / img.implicitWidth,
      "relativeY": mouseEvent.y / img.implicitHeight,
      "referent": root
    })
    return new_rec
  }

  function deleteAnnotation(anotObj) {
    ddb.deleteAnnotation(anotObj.ddbId)
    let objIndex = annotations.indexOf(anotObj)
    annotations.splice(objIndex, 1)
    anotObj.destroy()
  }

  function initZones(annots) {
    for (var z of annots) {

      var initDict = {
        "relativeX": z.relativeX,
        "relativeY": z.relativeY,
        "referent": root,
        "ddbId": z.id,
      }
      let newObject
      switch (z.classtype) {

        case "Stabylo": {
          newObject = stabyloRectangle.createObject(root,
            initDict,
          )
          newObject.relativeWidth = z.relativeWidth
          newObject.relativeHeight = z.relativeHeight
          break;
        }
        case "AnnotationText": {
          newObject = annotationText.createObject(root, initDict)
          newObject.text = z.text
          break;
        }
      }
      if (newObject != undefined) {
        root.annotations.push(newObject)
      }
    }
  }

  function storeZone(rec) {
    if (rec.relativeWidth > 0 && rec.relativeHeight > 0) {
      var newId = ddb.addAnnotation({
        "relativeX": rec.relativeX,
        "relativeY": rec.relativeY,
        "relativeWidth": rec.relativeWidth,
        "relativeHeight": rec.relativeHeight,
        "section": parseInt(root.sectionId),
        "classtype": "Stabylo"
      })
      if (newId) {
        rec.ddbId = newId
        annotations.push(rec)
      }
    }
  }

  function updateZone(mouseEvent, rec) {
    const new_rel_height = (mouseEvent.y - rec.y) / img.height
    const new_rel_width = (mouseEvent.x - rec.x) / img.implicitWidth
    rec.relativeHeight = new_rel_height >= 0 ? new_rel_height : 0
    rec.relativeWidth = new_rel_width >= 0 ? new_rel_width : 0
    return rec
  }

  Image {
    id: img

    property QtObject mouseArea: mouseArea
    asynchronous: true
    fillMode: Image.PreserveAspectFit
    source: root.imagePath
    sourceSize.width: base.width

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
        temp_rec = root.createZone(mouse)
      } else if (pressedButtons === Qt.RightButton) {
        root.focus = true
        root.addAnnotation(mouse)
        mouse.accepted = false
      }
    }

    onPositionChanged: {
      if (containsMouse) {
        temp_rec = root.updateZone(mouse, temp_rec)
      }
    }

    onReleased: {
      root.storeZone(temp_rec)
      temp_rec = null
    }
  }
}