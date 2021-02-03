import QtQuick 2.15

BasePageAction {
    property var stack: page ? page.undoStack : null

    icon.source: "qrc:///icons/undo"
    tooltip: stack && stack.canUndo ? "Annuler: " + stack.undoText : ""
    shortcut: stack && stack.canUndo ? "Ctrl+z" : ""
    onTriggered: stack ? stack.undo() : null
}
