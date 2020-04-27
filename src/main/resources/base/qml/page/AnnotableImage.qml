import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/menu"

FocusScope {
  id: root
  /* beautify preserve:start */
    property int sectionId
    property int position
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
    var path = content.path.toString()
    img.source = path.startsWith("file:///") ? content.path : "file:///" + path
    initZones()
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
    for (var z of ddb.loadAnnotations(sectionId)) {
      var initDict = {
        "relativeX": z.relativeX,
        "relativeY": z.relativeY,
        "referent": root,
        "ddbId": z.id,
        "color": z.color,
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
          newObject.font.underline = z.underline
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
        "classtype": "Stabylo",
        "color": rec.color
      })
      if (newId) {
        rec.ddbId = newId
        annotations.push(rec)
        return true
      }
    }
    return false
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
    //    asynchronous: true // asynchronous fail le scrolling on add
    fillMode: Image.PreserveAspectCrop
    source: root.imagePath
    sourceSize.width: base ? base.width : 0

  }
  MouseArea {
    id: mouseArea
    objectName: "mouseArea"
    anchors.fill: root
    /* beautify preserve:start */
    property var temp_rec: null
    /* beautify preserve:end */
    preventStealing: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton

    onPressed: {
      //      root.base.currentIndex = position
      if (pressedButtons === Qt.RightButton) {
        temp_rec = root.createZone(mouse)
      } else if (pressedButtons === Qt.LeftButton) {
        root.focus = true
        root.addAnnotation(mouse)
        mouse.accepted = true
      }
    }

    onPositionChanged: {
      if (containsMouse && temp_rec) {
        temp_rec = root.updateZone(mouse, temp_rec)
      }
    }

    onReleased: {
      if (mouse.button == Qt.RightButton) {
        temp_rec = root.storeZone(temp_rec)
        if (!temp_rec) {
          //          menuflotant.popup()
        }
        temp_rec = null
      }
    }
  }
}

//  Dialog {
//    id: dialogSupprimer
//    title: "Supprimer l'image ?"
//    standardButtons: Dialog.Ok | Dialog.Cancel
//    parent: root.editor
//    anchors.centerIn: parent
//
//    onAccepted: ddb.removeSection(root.editor.sectionId, root.editor.position)
//    //      onRejected: null
//  }