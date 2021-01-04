import QtQuick 2.15
import "qrc:/qml/actions" as PageActions

BaseButton {
    id: tableaubutton

    action: PageActions.NewTableauSection {
        position: targetIndex
        append: appendMode
        Component.onCompleted: action.dialog.parent = tableaubutton
    }

}
