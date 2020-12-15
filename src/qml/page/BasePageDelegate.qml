/*
section injecté via model
index injecté via repeater
*/

import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property var referent
    property alias dragarea: dragArea
    property alias contentItem: loader.item
    required property int index
    required property QtObject section

    signal loaded(int idx)

    focus: true
    width: referent.width
    height: loader.height
    Component.onCompleted: {
        loader.setSource("qrc:/qml/sections/" + section.classtype + ".qml", {
            "sectionItem": root,
            "section": section
        });
    }

    Rectangle {
        id: dragitem

        objectName: "dragitem"
        width: loader.width
        height: loader.height
        color: "transparent"
        Drag.active: dragArea.held
        Drag.source: dragArea
        Drag.hotSpot.x: width / 2
        Drag.hotSpot.y: height / 2

        Loader {
            id: loader

            function sendLoaded() {
                if (loader.item.status == undefined || loader.item.status == 1)
                    root.loaded(index);

            }

            focus: true
            asynchronous: true
            onLoaded: {
                if (loader.item.status != undefined && loader.item.status != 1)
                    loader.item.onStatusChanged.connect(sendLoaded);
                else
                    sendLoaded();
            }
        }

        anchors {
            verticalCenter: parent.verticalCenter
        }

        states: State {
            when: dragArea.held

            PropertyChanges {
                target: dragitem
                color: "steelblue"
                opacity: 0.6
            }

            ParentChange {
                target: dragitem
                parent: referent
            }

            AnchorChanges {
                target: dragitem

                anchors {
                    horizontalCenter: undefined
                    verticalCenter: undefined
                }

            }

        }

    }

    MouseArea {
        id: dragArea

        property bool held: false

        objectName: "pageDragArea" //ne pas suppimer, important
        anchors.fill: parent
        height: loader.height
        drag.target: held ? dragitem : undefined
        drag.axis: Drag.YAxis
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton
        cursorShape: Qt.NoCursor
        onPressed: {
            if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ShiftModifier)) {
                held = true;
                mouse.accepted = true;
            } else if ((mouse.button == Qt.MiddleButton) && (mouse.modifiers & Qt.ShiftModifier)) {
                referent.removeDialog.open(index);
                mouse.accepted = true;
            } else {
                mouse.accepted = false;
            }
        }
        onReleased: {
            held = false;
        }
    }

    MouseArea {
        objectName: "intermousearea"
        height: referent.spacing
        width: root.width
        anchors.top: root.bottom
        acceptedButtons: Qt.RightButton
        onClicked: {
            if ((mouse.button == Qt.RightButton) && (mouse.modifiers & Qt.ShiftModifier))
                referent.addDialog.open(index);

        }
    }

    DropArea {
        id: droparea

        onEntered: {
            if (drag.source.parent.index != index && drag.source.objectName == dragArea.objectName)
                referent.page.model.move(drag.source.parent.index, index);
            else
                drag.accepted = false;
        }

        anchors {
            fill: root
            margins: 1
        }

    }

}
