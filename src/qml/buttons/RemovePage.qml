import QtQuick 2.15
import "qrc:/qml/actions" as PageActions

BaseButton {
    id: bouton

    action: PageActions.RemovePage {
        Component.onCompleted: action.dialog.parent = bouton
    }

}
