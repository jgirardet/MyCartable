import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as Actions

BaseButton {
    icon.color: enabled ? "transparent" : "grey"
    enabled: action.stack && action.stack.canRedo
    visible: true

    action: Actions.RedoAction {
    }

}
