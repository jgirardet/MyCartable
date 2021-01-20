import QtQuick 2.15

BasePageAction {
    property var stack: page && page.classeur ? page.classeur.undoStack : null

    icon.source: "qrc:///icons/redo"
    tooltip: stack ? "Rétablir: " + stack.undoText : ""
    shortcut: "Ctrl+Maj+z"
    onTriggered: stack.redo()
}
