import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/menu"

FocusScope {
  id: root
  /* beautify preserve:start */
    property int sectionId
    property var sectionItem
    property alias image: img
    property var annotations: []
    readonly property var annotationText: Qt.createComponent("qrc:/qml/page/AnnotationText.qml")
    readonly property var stabyloRectangle: Qt.createComponent("qrc:/qml/page/StabyloRectangle.qml")
   /* beautify preserve:end */

  //doit rester comme ça car taille de root calculé sur image et width image calculé sur root. et  pour les annotations +++
  height: img.height

  Component.onCompleted: {
    var content = ddb.loadSection(sectionId)
    var path = content.path.toString()
    img.source = path.startsWith("file:///") || path.startsWith("qrc:") ? content.path : "file:///" + path
    initZones()
  }

  function addAnnotation(mouseEvent) {
    var [newDdbObj, stylObj] = ddb.addAnnotation({
      "relativeX": mouseEvent.x / img.implicitWidth, //newObject.relativeX,
      "relativeY": mouseEvent.y / img.implicitHeight, //newObject.relativeY,
      "section": parseInt(root.sectionId),
      "classtype": "AnnotationText",
      "text": ""
    })
    if (newDdbObj) {
      var newObject = annotationText.createObject(root, {
        "model": newDdbObj,
        "objStyle": stylObj,
        "referent": img
      })
      newObject.ddbId = newDdbObj.id
      newObject.objStyle = stylObj
      annotations.push(newObject)
      newObject.forceActiveFocus()
      return newObject
    }

  }

  function createZone(mouseEvent) {
    var relativeX = mouseEvent.x / img.implicitWidth
    var relativeY = mouseEvent.y / img.implicitHeight
    var [newDdbObj, stylObj] = ddb.addAnnotation({
      "relativeX": relativeX,
      "relativeY": relativeY,
      "relativeWidth": 0,
      "relativeHeight": 0,
      "section": parseInt(root.sectionId),
      "classtype": "Stabylo",
      "style": {
        "bgColor": "red"
      }
    })
    var new_rec = stabyloRectangle.createObject(root, {
      "model": newDdbObj,
      "objStyle": stylObj,
      "referent": img
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
        "referent": img,
        "model": z[0],
        'objStyle': z[1]
      }
      var newObject
      switch (z[0].classtype) {
        case "Stabylo": {
          newObject = stabyloRectangle.createObject(root, initDict)
          break;
        }
        case "AnnotationText": {
          newObject = annotationText.createObject(root, initDict)
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
      rec.model = ddb.updateAnnotation(rec.model.id, {
        "relativeWidth": rec.relativeWidth,
        "relativeHeight": rec.relativeHeight,
      })
      print(JSON.stringify(rec.model))
      annotations.push(rec)
      rec.pushed = true
      return true
    } else {
      ddb.deleteAnnotation(rec.model.id)
      rec = null
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
    sourceSize.width: sectionItem ? sectionItem.width : 0
    // TODO: faire des trais.
  }
  MouseArea {
    id: mouseArea
    objectName: "mouseArea"
    anchors.fill: img
    /* beautify preserve:start */
    property var temp_rec: null
    /* beautify preserve:end */
    preventStealing: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton

    onPressed: {
      if (pressedButtons === Qt.RightButton) {
        if (mouse.modifiers == Qt.ControlModifier) {
          uiManager.menuFlottantImage.ouvre(img)
        } else {
          temp_rec = root.createZone(mouse)
        }
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