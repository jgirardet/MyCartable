import QtQuick 2.15

BasePageAction {
    property var stack: page && page.classeur ? page.classeur.undoStack : null

    icon.source: "qrc:///icons/undo"
    tooltip: stack ? "Annuler: " + stack.undoText : ""
    shortcut: "Ctrl+z"
    onTriggered: stack ? stack.undo() : null
}
