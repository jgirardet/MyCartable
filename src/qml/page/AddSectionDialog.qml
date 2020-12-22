import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/buttons"
import "qrc:/qml/divers"

IndexedDialog {
    id: root

    property QtObject page

    title: "Ajouter un élément ?"

    contentItem: Row {
        NewTextSection {
            id: newtext

            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

        NewImageSection {
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: {
                action.triggered.connect(root.close);
                action.busy.parent = root.parent;
            }
        }

        NewImageSectionVide {
            visible: false
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

        NewEquationSection {
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

        NewOperationSection {
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

        NewTableauSection {
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

        NewFriseSection {
            appendMode: false
            page: root.page
            targetIndex: root.itemIndex
            Component.onCompleted: action.triggered.connect(root.close)
        }

    }

}
