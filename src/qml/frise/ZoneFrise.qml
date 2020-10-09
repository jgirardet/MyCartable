import QtQml.Models 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Rectangle {
    //        repeater.model.splice(index, 1);
    //     {
    //        id: listlegendes
    //        Component.onCompleted: {
    //            for (const el of legendes) {
    //      ListModel          append(el);
    //            }
    //        }
    //    }
    //    function remove_legende(index) {
    //        let modd = repeater.model;
    //        modd.splice(index, 1);
    //        repeater.model = modd;
    //        listlegendes.remove(index);
    //    }

    id: root

    property int modelIndex
    property Item dragParent
    property Item sizeParent
    property alias texte: texte
    property alias bgColor: root.color
    property alias legendeItems: legendeItems

    color: colordialog.color
    Component.onCompleted: {
        onColorChanged.connect(function() {
            backgroundColor = color;
        });
    }
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

    ColorPicker {
        id: colordialog

        objectName: "colordialog"
        color: backgroundColor
    }

    TextArea {
        id: texte

        anchors.centerIn: parent
        horizontalAlignment: TextEdit.AlignHCenter
        verticalAlignment: TextEdit.AlignVCenter
        width: parent.width * 0.8
        height: Math.min(contentHeight + 5, parent.height - 5)
        font.pointSize: 12
        text: display
        wrapMode: Text.Wrap
        Component.onCompleted: {
            onTextChanged.connect(function() {
                model.edit = text;
            });
        }

        background: Rectangle {
            anchors.fill: parent
            color: Qt.lighter(colordialog.color)
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
                let newL = ddb.addDB("FriseLegende", {
                    "relativeX": mouse.x / width,
                    "texte": "",
                    "zone": zoneId,
                    "side": false
                });
                legendeItems.append(newL);
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

        onItemAdded: item.legende.forceActiveFocus()
        onItemRemoved: {
            ddb.delDB("FriseLegende", item.legendeId);
        }
        onItemSet: {
            ddb.setDB("FriseLegende", item.legendeId, dict);
        }
        modelObject: legendes

        delegate: Legende {
            id: legende

            handler: legendeItems
            legendeId: id
            legende.text: texte
            state: side ? "up" : ""
            x: parent.width * relativeX
        }

    }

}
