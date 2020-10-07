import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/frise"

ListView {
    //    spacing: 20

    id: root

    property int bottomBorderWidth: 5

    orientation: ListView.Horizontal

    MouseArea {
        id: mousearea

        anchors.fill: parent
        onClicked: {
            if (mouse.button == Qt.LeftButton)
                root.model.append();

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

        width: ratio * root.width // + separator.width
        height: root.height
        onEntered: {
            let dragindex = drag.source.modelIndex;
            if (index === dragindex)
                return ;

            root.model.move(dragindex, index + 1);
        }

        Row {
            anchors.fill: parent

            ZoneFrise {
                id: zonefrise

                width: droparea.width - separator.width
                height: droparea.height
                modelIndex: index
                dragParent: root
                sizeParent: droparea
            }

            Separator {
                id: separator

                dragParent: root
                visible: !zonefrise.Drag.active
            }

        }

    }

}
