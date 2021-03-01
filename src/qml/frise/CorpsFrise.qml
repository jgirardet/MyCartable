import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/frise"

ListView {
    id: root

    property int bottomBorderWidth: 5
    property QtObject section

    orientation: ListView.Horizontal

    MouseArea {
        id: mousearea

        anchors.fill: parent
        onClicked: {
            if (mouse.button == Qt.LeftButton)
                root.model.add();

        }
        z: -1
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: -border.width
        color: "white"
        border.color: "black"
        border.width: bottomBorderWidth
        z: -1
    }

    displaced: Transition {
        NumberAnimation {
            properties: "x,y"
            easing.type: Easing.OutQuad
        }

    }

    delegate: DropArea {
        id: droparea

        property alias zone: zonefrise
        property alias separator: separator

        //        width: ratio * root.width // + separator.width
        width: separator.localRatio * root.width
        // + separator.width
        height: root.height
        onEntered: {
            let dragindex = drag.source.modelIndex;
            if (index === dragindex)
                return ;

            root.model.move(dragindex, index + 1);
        }

        Row {
            anchors.fill: parent

            Connections {
                function onRatioChanged(idx, val) {
                    separator.localRatio = ratio;
                }

                target: root.section.model
            }

            ZoneFrise {
                id: zonefrise

                width: droparea.width - separator.width
                height: droparea.height
                modelIndex: index
                dragParent: root
                sizeParent: droparea
                section: root.section
            }

            Separator {
                id: separator

                dragParent: root
                visible: !zonefrise.Drag.active
            }

        }

    }

}
