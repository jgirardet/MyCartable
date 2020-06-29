import QtQuick 2.14
import QtQuick.Controls 2.14

Item {
    //    loader.setSource(`qrc:/qml/sections/${page.classtype}.qml`, {

    id: root

    property var listview: ListView.view
    property int sectionId: page.id
    property int modelIndex: typeof model !== "undefined" ? model.index : undefined

    width: listview.width
    height: loader.height
    Component.onCompleted: {
        loader.setSource("qrc:/qml/sections/" + page.classtype + ".qml", {
            "sectionId": sectionId,
            "sectionItem": root
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

            objectName: "loader"
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
                parent: listview.contentItem
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

        anchors.fill: parent
        height: loader.height
        drag.target: held ? dragitem : undefined
        drag.axis: Drag.YAxis
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton
        onPressed: {
            if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ShiftModifier)) {
                held = true;
                mouse.accepted = true;
            } else if ((mouse.button == Qt.MiddleButton) && (mouse.modifiers & Qt.ShiftModifier)) {
                var coord = mapToItem(listview, mouse.x, mouse.y);
                listview.removeDialog.ouvre(index, coord);
                mouse.accepted = true;
            } else {
                mouse.accepted = false;
            }
        }
        onReleased: {
            held = false;
        }
    }

    DropArea {
        id: droparea

        onEntered: {
            listview.model.move(drag.source.parent.modelIndex, index);
        }

        anchors {
            fill: root
            margins: 10
        }

    }

    MouseArea {
        height: listview.spacing
        width: root.width
        //    color: "green"
        anchors.top: root.bottom
        acceptedButtons: Qt.RightButton
        onClicked: {
            if ((mouse.button == Qt.RightButton) && (mouse.modifiers & Qt.ShiftModifier)) {
                var coord = mapToItem(listview, mouse.x, mouse.y);
                listview.addDialog.ouvre(index, coord);
            }
        }
    }

}
