import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as Actions

BaseButton {
    icon.color: action.stack && action.stack.canRedo ? "transparent" : "grey"

    action: Actions.RedoAction {
    }

}
