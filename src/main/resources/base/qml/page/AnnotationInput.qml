import QtQuick 2.12
import QtQuick.Controls 2.12

TextField {
    id: control

    property QtObject referent
    property real relativeX
    property real relativeY

    padding: 0
    height: contentHeight
    width: contentWidth +5
    x: relativeX * referent.width
    y: relativeY * referent.height
    background: Rectangle {
            implicitWidth: parent.width
            implicitHeight: parent.height
            color: "transparent"
            border.color: control.focus ? "#21be2b" : "transparent"
        }

    Component.onDestruction: {
        let obj = referent.annotations.indexOf(control)
        referent.annotations.splice(obj,1)
    }


    MouseArea {
        objectName: "mouseArea"
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onPressed:  {
            if (mouse.buttons === Qt.LeftButton)
                control.focus=true
            else if (mouse.buttons === Qt.RightButton) {
                control.destroy()
            }
        }
    }

}
