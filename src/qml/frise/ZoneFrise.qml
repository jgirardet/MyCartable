import MyCartable 1.0
import QtQml.Models 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Rectangle {
    id: root

    property int modelIndex
    property QtObject section
    property Item dragParent
    property Item sizeParent
    property alias texte: texte
    property alias bgColor: root.color
    property alias legendeItems: legendeItems

    color: backgroundColor
    border.color: "yellow"
    border.width: 0
    Drag.active: dragHandler.active
    Drag.source: root
    Drag.hotSpot.x: width / 2
    states: [
        State {
            when: dragHandler.active

            ParentChange {
                target: root
                parent: root.dragParent
            }

            PropertyChanges {
                target: root
                opacity: 0.6
                border.width: 3
            }

        }
    ]

    Database {
        id: database
    }

    ColorPicker {
        id: colordialog

        objectName: "colordialog"
        onColorChanged: {
            if (backgroundColor != color)
                backgroundColor = color;

        }
        Component.onCompleted: color = backgroundColor
    }

    UndoAbleTextArea {
        id: texte

        function setText() {
            edit = text;
        }

        txtfield: display
        undostack: root.section.undoStack
        anchors.centerIn: parent
        horizontalAlignment: TextEdit.AlignHCenter
        verticalAlignment: TextEdit.AlignVCenter
        width: parent.width * 0.8
        height: Math.min(contentHeight + 15, parent.height - 5)
        font.pointSize: Math.max(dragParent.width / 100, 10)
        wrapMode: Text.Wrap

        background: Rectangle {
            anchors.fill: parent
            color: Qt.lighter(backgroundColor)
        }

    }

    MouseArea {
        id: mousearea

        anchors.fill: parent
        acceptedButtons: Qt.RightButton | Qt.MiddleButton
        cursorShape: dragHandler.active ? Qt.SizeAllCursor : undefined
        onPressed: {
            if (mouse.button === Qt.MiddleButton)
                dragParent.model.remove(index);
            else if (mouse.button === Qt.RightButton)
                colordialog.open();
        }
    }

    DragHandler {
        id: dragHandler

        yAxis.enabled: false
        acceptedButtons: Qt.LeftButton

        xAxis {
            enabled: true
            minimum: 0
            maximum: dragParent.width - droparea.width
        }

    }

    Rectangle {
        id: borderinf

        anchors.left: root.left
        anchors.right: root.right
        anchors.bottom: root.bottom
        color: "black"
        anchors.bottomMargin: -height
        height: root.dragParent.bottomBorderWidth

        MouseArea {
            id: borderinfmouse

            hoverEnabled: true
            anchors.fill: parent
            cursorShape: Qt.BlankCursor
            onClicked: {
                root.section.model.addLegende(root.modelIndex, {
                    "relativeX": mouse.x / width,
                    "texte": "",
                    "zone": zoneId,
                    "side": false
                });
            }
        }

        Rectangle {
            height: 20
            width: 2
            color: "black"
            anchors.top: parent.bottom
            visible: borderinfmouse.containsMouse && !borderinfmouse.pressed
            x: Math.max(borderinfmouse.mouseX, 5)
            y: borderinfmouse.mouseY
        }

    }

    DynamicRepeater {
        id: legendeItems

        function legendeAdded(zIdx, lIdx, content) {
            if (zIdx == root.modelIndex)
                legendeItems.insert(lIdx, content);

        }

        function legendeRemoved(zIdx, lIdx) {
            if (zIdx == root.modelIndex)
                legendeItems.remove(lIdx);

        }

        function legendeUpdated(zIdx, lIdx, content) {
            if (zIdx == root.modelIndex) {
                legendeItems.setProperty(lIdx, "texte", content["texte"]);
                legendeItems.setProperty(lIdx, "relativeX", content["relativeX"]);
                legendeItems.setProperty(lIdx, "side", content["side"]);
            }
        }

        onItemAdded: item.legende.forceActiveFocus()
        modelObject: legendes
        Component.onCompleted: {
            root.section.model.legendeAdded.connect(legendeAdded);
            root.section.model.legendeRemoved.connect(legendeRemoved);
            root.section.model.legendeUpdated.connect(legendeUpdated);
        }

        delegate: Legende {
            id: legende

            handler: legendeItems
            legendeId: id
            state: side ? "up" : ""
            x: parent.width * relativeX
            section: root.section
            zoneIndex: root.modelIndex
        }

    }

}
