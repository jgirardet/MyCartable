import QtQuick 2.15

BasePageAction {
    property var stack: page ? page.undoStack : null

    icon.source: "qrc:///icons/redo"
    tooltip: stack && stack.canRedo ? "Rétablir: " + stack.redoText : ""
    shortcut: stack && stack.canRedo ? "Ctrl+Maj+z" : ""
    onTriggered: stack.redo()
}
