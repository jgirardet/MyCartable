import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

TimedSlider {
    id: root

    property var menu
    property var target: menu.target

    wheelEnabled: true
    stepSize: 1
    to: 100
    from: 1

    background: Rectangle {
        property Item barre
        property alias barre: barre_id

        implicitWidth: 200
        implicitHeight: 10
        color: "transparent"
        opacity: 1 //root.value / 10

        Rectangle {
            id: barre_id

            anchors.verticalCenter: parent.verticalCenter
            width: parent.width
            height: 2
            color: "black"
            radius: 2
        }

    }

    handle: Rectangle {
        x: root.leftPadding + root.visualPosition * (root.availableWidth - width)
        y: root.topPadding + root.availableHeight / 2 - height / 2
        implicitWidth: 26
        implicitHeight: 26
        radius: 13
        color: root.pressed ? "#f0f0f0" : "#f6f6f6"
        border.color: "#bdbebf"

        Text {
            id: textColumn

            text: root.value
            font.pixelSize: 12
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }

    }

}
