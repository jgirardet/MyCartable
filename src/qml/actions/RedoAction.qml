import QtQuick 2.15

BasePageAction {
    property var stack: page && page.classeur ? page.classeur.undoStack : null

    icon.source: "qrc:///icons/redo"
    tooltip: stack && stack.canRedo ? "Rétablir: " + stack.undoText : ""
    shortcut: stack && stack.canRedo ? "Ctrl+Maj+z" : ""
    onTriggered: stack.redo()
}
