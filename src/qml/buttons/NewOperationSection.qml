import QtQuick 2.15
import "qrc:/qml/actions" as PageActions

BaseButton {
    id: operationbutton

    action: PageActions.NewOperationSection {
        position: targetIndex
        append: appendMode
        Component.onCompleted: action.dialog.parent = operationbutton
    }

}
