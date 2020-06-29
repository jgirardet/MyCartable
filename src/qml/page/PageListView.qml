import "../toolbuttons"
import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {
    //  displayMarginEnd: 50
    //  populate: Transition {
    //    NumberAnimation {
    //      property: "scale";from: 0;to: 1.0;duration: 800
    //    }
    //    NumberAnimation {
    //      properties: "x,y";duration: 800;easing.type: Easing.OutBack
    //    }
    //  }

    id: root

    property var removeDialog: removeDialog
    property var addDialog: addDialog

    function onItemAdded(modelIndex, row, col) {
        positionViewAtIndex(row, ListView.Contain);
        currentIndex = row;
    }

    spacing: 10
    clip: true
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
            NewTextSectionButton {
                id: newtext

                targetIndex: typeof addDialog.index != "undefined" ? addDialog.index + 1 : 0
                target: addDialog
            }

            NewImageSectionButton {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            NewEquationSectionButton {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            NewOperationSectionButton {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

            NewTableauSectionButton {
                targetIndex: newtext.targetIndex
                target: newtext.target
            }

        }

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
