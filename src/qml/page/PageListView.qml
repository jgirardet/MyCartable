import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions"

ListView {
    id: root

    property var removeDialog: removeDialog
    property var addDialog: addDialog

    function onItemAdded(modelIndex, row, col) {
        positionViewAtIndex(row, ListView.Contain);
        currentIndex = row;
    }

    spacing: 10
    clip: true
    cacheBuffer: 20000
    focus: true
    boundsBehavior: Flickable.DragOverBounds
    onCurrentIndexChanged: {
        if (model.lastPosition !== currentIndex)
            model.lastPosition = currentIndex;

    }
    Component.onCompleted: {
        model.rowsInserted.connect(onItemAdded);
    }

    Connections {

        function onModelReset() {
            if (currentIndex != model.lastPosition)
                currentIndex = model.lastPosition;

        }

        target: model
    }

    Dialog {
        id: removeDialog

        property int index

        function ouvre(itemIndex, coords) {
            index = itemIndex;
            open();
            x = coords.x - width / 2;
            y = coords.y - height / 2;
        }

        objectName: "removeDialog"
        title: "Supprimer cet élément ?"
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: root.model.removeSection(index)

        enter: Transition {
            NumberAnimation {
                property: "scale"
                from: 0
                to: 1
            }

        }

    }

    Dialog {
        id: addDialog

        property int index

        function ouvre(itemIndex, coords) {
            index = itemIndex;
            open();
            x = coords.x - width / 2;
            y = coords.y - height / 2;
        }

        title: "Ajotuer un élément ?"

        enter: Transition {
            NumberAnimation {
                property: "scale"
                from: 0
                to: 1
            }

        }

        contentItem: Row {
            Buttons.NewTextSection {
                id: newtext

                targetIndex: typeof addDialog.index != "undefined" ? addDialog.index + 1 : 0
                target: addDialog
            }

            Buttons.NewImageSection {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            Buttons.NewEquationSection {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            Buttons.NewOperationSection {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            Buttons.NewTableauSection {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

        }

    }

    footer: Rectangle {
        height: root.height / 2
        width: root.width
        color: Qt.rgba(98 / 255, 105 / 255, 123 / 255, 1)
    }

    delegate: BasePageDelegate {
    }

    ScrollBar.vertical: ScrollBar {
        minimumSize: 0.2
    }

    // TRANSITIONS
    remove: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
                to: 0
                duration: 1000
            }

            NumberAnimation {
                property: "scale"
                to: 0
                duration: 500
            }

        }

    }

    removeDisplaced: Transition {
        NumberAnimation {
            properties: "x,y"
            duration: 500
        }

    }

    add: Transition {
        NumberAnimation {
            property: "opacity"
            from: 0
            to: 1
            duration: 1000
        }

        NumberAnimation {
            property: "scale"
            from: 0
            to: 1
            duration: 400
        }

    }

    displaced: Transition {
        NumberAnimation {
            properties: "x,y"
            duration: 800
            easing.type: Easing.OutBounce
        }

    }

}
