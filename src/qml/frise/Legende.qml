import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Item {
    id: root

    property string legendeId
    property alias languette: languette
    property alias legende: legende
    property var realParent
    property Item handler
    property QtObject section
    property int zoneIndex

    anchors.top: parent.bottom
    states: [
        State {
            name: "up"

            AnchorChanges {
                target: root
                anchors.bottom: parent.top
                anchors.top: undefined
            }

            AnchorChanges {
                target: legende
                anchors.bottom: languette.top
                anchors.top: undefined
            }

            PropertyChanges {
                target: languette
                y: -languette.height
            }

        }
    ]

    UndoAbleTextArea {
        id: legende

        function setText() {
            section.model.updateLegende(root.zoneIndex, index, {
                "texte": text
            });
        }

        txtfield: texte
        undostack: section.undoStack
        anchors.horizontalCenter: languette.horizontalCenter
        anchors.top: languette.bottom
        height: Math.max(contentHeight + 15, 15)
        width: Math.max(contentWidth + 20, 40)
        horizontalAlignment: TextEdit.AlignHCenter
        verticalAlignment: TextEdit.AlignVCenter
        selectByMouse: true

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.MiddleButton
            onWheel: {
                if (!legende.focus)
                    return ;

                //prevent moving legend when scrolling
                if (wheel.angleDelta.y > 0)
                    section.model.updateLegende(root.zoneIndex, index, {
                    "side": true
                });
                else
                    section.model.updateLegende(root.zoneIndex, index, {
                    "side": false
                });
                wheel.accepted = true;
            }
            cursorShape: Qt.IBeamCursor
            onPressed: {
                if (mouse.button & Qt.MiddleButton)
                    section.model.removeLegende(root.zoneIndex, index);

            }
        }

        background: Rectangle {
            anchors.fill: parent
            border.width: 1
            border.color: "black"
        }

    }

    Rectangle {
        id: languette

        width: 2
        height: 10
        color: "black"

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.SizeHorCursor
            drag.target: root
            drag.axis: Drag.XAxis
            drag.minimumX: 5
            drag.maximumX: root.parent.width
            drag.threshold: 0
            onReleased: {
                section.model.updateLegende(root.zoneIndex, index, {
                    "relativeX": root.x / root.parent.width
                });
            }
        }

    }

}
