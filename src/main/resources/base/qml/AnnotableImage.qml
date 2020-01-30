import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12

Image {
    id: img
    property QtObject mouseArea: mouseArea
    fillMode: Image.PreserveAspectFit
    //sourceSize.width: parent.width
    property var annotations: []
    readonly property var annotationInput: Qt.createComponent(
                                               "qrc:/qml/AnnotationInput.qml")
    readonly property var stabyloRectangle: Qt.createComponent(
                                                "qrc:/qml/StabyloRectangle.qml")

    function addAnnotation(mouseEvent, parent) {
        let newObject = annotationInput.createObject(parent, {
                                                         "relativeX": mouseEvent.x
                                                                      / img.implicitWidth,
                                                         "relativeY": mouseEvent.y
                                                                      / img.implicitHeight,
                                                         "focus": true,
                                                         "referent": img
                                                     })
        img.annotations.push(newObject)
    }

    function initZone(mouseEvent) {
        var new_rec = stabyloRectangle.createObject(parent, {
                                                        "relativeX": mouseEvent.x
                                                                     / img.implicitWidth,
                                                        "relativeY": mouseEvent.y
                                                                     / img.implicitHeight,
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
        print(annotations)
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        property QtObject temp_rec

        onDoubleClicked: {
            img.addAnnotation(mouse, mouseArea)
        }
        onPressed: {
            if (pressedButtons === Qt.LeftButton) {
                temp_rec = img.initZone(mouse)
            } else if (pressedButtons === Qt.RightButton) {
                mouse.accepted = false
                img.removeZone()
            }
        }
        onPositionChanged: {
            if (containsMouse) {
                temp_rec = img.updateZone(mouse, temp_rec)
            }
        }
        onReleased: {
            img.storeZone(temp_rec)
            temp_rec = null
        }
    }
    Component.onCompleted: {

    }
}
