import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
    id: root

    property string sectionId
    property var sectionItem
    property int previousCursorPosition

    width: sectionItem.width - 0
    height: contentHeight + 30
    font.pointSize: 12
    onSectionIdChanged: {
        var data = ddb.loadSection(sectionId);
        text = data.content;
        cursorPosition = data.curseur;
    }
    onCursorPositionChanged: {
        previousCursorPosition = cursorPosition;
    }
    font.family: "Code New Roman"
    Keys.onPressed: {
        var new_data = ddb.updateEquation(sectionId, text, cursorPosition, JSON.stringify(event));
        root.text = new_data.content;
        root.cursorPosition = new_data.curseur;
        event.accepted = true;
    }
    onSelectionStartChanged: {
        if (!ddb.isEquationFocusable(text, selectionStart))
            cursorPosition = previousCursorPosition;

    }

    background: Rectangle {
        anchors.fill: parent
        color: "white"
    }

}
