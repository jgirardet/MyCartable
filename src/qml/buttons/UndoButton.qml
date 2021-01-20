import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as Actions

BaseButton {
    icon.color: action.stack && action.stack.canUndo ? "transparent" : "grey"

    action: Actions.UndoAction {
    }

}
