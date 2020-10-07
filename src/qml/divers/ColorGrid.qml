import QtQuick 2.0
import QtQuick.Controls 2.14

Grid {
        id: root
        signal picked(color col)
        property var colors: []
        columns: 9
        width: parent.width
        spacing: 5
        Repeater {
            id: repeater
            model: ["auto",...root.colors]
            delegate:Label {
                text: modelData.slice(0,6)
                font.pointSize: 6
                width:32
                height: 32
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                background: Rectangle {
                    color: modelData != "auto" ? modelData : "white"
                    anchors.fill: parent
                    border.width: 1
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.picked(modelData)
                }

            }
        }
    }
