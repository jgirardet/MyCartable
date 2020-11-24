import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/buttons" as Buttons

ListView {
    //        target: model
    //    }
    //        if (currentIndex != model.basePage.lastPosition)
    //            currentIndex = model.basePage.lastPosition;
    //        property var page: page

    id: root

    property var removeDialog: removeDialog
    property var addDialog: addDialog

    function onItemAdded(modelIndex, row, col) {
        positionViewAtIndex(row, ListView.Contain);
        currentIndex = row;
    }

    //    Connections {
    //        function onModelReset() {
    //            if (currentIndex != model.basePage.lastPosition)
    //                currentIndex = model.basePage.lastPosition;
    //        }
    //model
    spacing: 10
    clip: true
    cacheBuffer: 20000
    focus: true
    boundsBehavior: Flickable.DragOverBounds
    currentIndex: model ? model.page.lastPosition : -1
    //    onCurrentIndexChanged: {
    //        if (model.page.lastPosition !== currentIndex) {
    //            model.page.lastPosition = currentIndex;
    //        }
    //    }
    onModelChanged: {
        if (model) {
            print(model);
            model.rowsInserted.connect(onItemAdded);
        }
    }
    contentItem.onChildrenRectChanged: {
        adjustcachebuffer.restart();
    }

    Timer {
        id: adjustcachebuffer

        running: false
        interval: 300
        onTriggered: {
            var cHeight = root.contentItem.childrenRect.height;
            var bufferMax = Math.max(20000, cHeight + (cHeight / 2));
            if (root.cacheBuffer != bufferMax)
                root.cacheBuffer = bufferMax;

        }
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

                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewImageSection {
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewImageSectionVide {
                visible: false
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewEquationSection {
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewOperationSection {
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewTableauSection {
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
            }

            Buttons.NewFriseSection {
                appendMode: false
                target: addDialog
                targetIndex: addDialog.index
                Component.onCompleted: action.triggered.connect(addDialog.close)
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
