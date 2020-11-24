import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property var listview: ListView.view
    property string sectionId: section.id
    property int modelIndex: typeof model !== "undefined" ? model.index : undefined
    property alias dragarea: dragArea

    focus: true
    width: listview.width
    height: loader.height
    Component.onCompleted: {
        loader.setSource("qrc:/qml/sections/" + section.classtype + ".qml", {
            "sectionId": sectionId,
            "sectionItem": root,
            "section": section
        });
    }
    onActiveFocusChanged: {
        if (activeFocus)
            loader.item ? loader.item.forceActiveFocus() : null;

    }
    ListView.onAdd: {
        loader.item.forceActiveFocus();
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

            focus: true
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

        objectName: "pageDragArea"
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
            if (drag.source.parent.modelIndex != index && drag.source.objectName == dragArea.objectName)
                listview.model.move(drag.source.parent.modelIndex, index);
            else
                drag.accepted = false;
        }

        anchors {
            fill: root
            margins: 10
        }

    }

    MouseArea {
        objectName: "intermousearea"
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
