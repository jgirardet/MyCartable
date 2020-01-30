import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    id: control

    property QtObject referent
    property real relativeX
    property real relativeY
    property real relativeWidth: 0
    property real relativeHeight: 0



    height: relativeHeight * referent.height
    width: relativeWidth * referent.width
    x: relativeX * referent.width
    y: relativeY * referent.height
    color: Qt.rgba(0.5, 0.4, 0.2, 0.4)

    Component.onDestruction: {
        let obj = referent.annotations.indexOf(control)
        referent.annotations.splice(obj,1)
    }


    MouseArea {
        objectName: "mouseArea"
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onPressed:  {
            if (mouse.buttons === Qt.RightButton) {
                control.destroy()
            }
        }
    }

}
