import QtQuick 2.15
import QtQuick.Controls 2.15

Loader {
    id: root

    property var referent
    property var mouse: mousearea
    property bool held: false

    function move(dx, dy) {
        anchors.leftMargin += dx;
        anchors.topMargin += dy;
        saveMove();
    }

    function saveMove() {
        edit = {
            "id": annot.id,
            "x": root.x / root.parent.implicitWidth,
            "y": root.y / root.parent.implicitHeight
        };
    }

    function setStyleFromMenu(data) {
        data["id"] = annot.id;
        edit = data;
    }

    anchors.top: parent.top
    anchors.topMargin: annot.y * parent.implicitHeight
    anchors.left: parent.left
    anchors.leftMargin: annot.x * parent.implicitWidth
    focus: parent.currentAnnotation === root
    Component.onCompleted: {
        root.setSource("qrc:/qml/annotations/" + annot.classtype + ".qml", {
            "referent": referent
        });
    }
    states: [
        State {
            name: "dragging"
            when: root.held

            AnchorChanges {
                target: root
                anchors.top: undefined
                anchors.left: undefined
            }

        }
    ]

    MouseArea {
        //            }
        //            ddb.setImageSectionCursor(mousearea, "text");

        id: mousearea

        cursorShape: Qt.NoCursor
        anchors.fill: parent
        z: 1
        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
        hoverEnabled: true
        onEntered: {
            root.parent.currentAnnotation = root;
        }
        onExited: {
            ddb.setImageSectionCursor(mousearea);
        }
        onPositionChanged: {
            let tool = "";
            if (!root.item.checkPointIsNotDraw(mouse.x, mouse.y)) {
                if (mouse.modifiers & Qt.ControlModifier)
                    tool = "dragmove";
                else
                    tool = "default";
            }
            ddb.setImageSectionCursor(mousearea, tool);
        }
        preventStealing: true
        onPressed: {
            // check coordonnate
            if (root.item.checkPointIsNotDraw(mouse.x, mouse.y)) {
                // non teste : comment faire ?
                mouse.accepted = false;
                return ;
            }
            if (mouse.buttons === Qt.MiddleButton) {
                root.parent.model.remove(index);
            } else if (mouse.buttons === Qt.RightButton) {
                root.item.menu.ouvre(root);
                mouse.accepted = true;
            } else if (mouse.buttons === Qt.LeftButton && (mouse.modifiers & Qt.ControlModifier)) {
                root.held = true;
            } else {
                mouse.accepted = false;
            }
        }
        onReleased: {
            if (held) {
                saveMove();
                root.held = false;
            }
        }
        drag.target: held ? root : null
        drag.smoothed: false
    }

}
