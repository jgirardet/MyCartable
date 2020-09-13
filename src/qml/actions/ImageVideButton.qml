import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var size

    height: size.iconHeight
    Layout.fillWidth: true
    color: "white"
    border.width: 1
    border.color: "black"

    MouseArea {
        onClicked: root.parent.choose(size.value)
        anchors.fill: parent
    }

}
