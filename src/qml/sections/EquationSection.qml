import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
    id: root

    required property Item sectionItem
    required property QtObject section

    width: sectionItem.width
    height: contentHeight + 30
    font.pointSize: 12
    text: section.content
    onCursorPositionChanged: {
        if (!section.isEquationFocusable(cursorPosition))
            cursorPosition = section.curseur;

    }
    font.family: "Code New Roman"
    Keys.onPressed: {
        if ([Qt.Key_Control, Qt.Key_Shift].includes(event.key)) {
            //on ignore controle seul
            return ;
        } else if ((event.key == Qt.Key_Z) && (event.modifiers & Qt.ControlModifier)) {
            if (event.modifiers & Qt.ShiftModifier)
                section.redo();
            else
                section.undo();
        } else {
            section.update(cursorPosition, JSON.stringify(event));
        }
        cursorPosition = section.curseur;
        event.accepted = true;
    }
    onActiveFocusChanged: {
        if (activeFocus)
            section.curseur = cursorPosition;

    }

    background: Rectangle {
        anchors.fill: parent
        color: "white"
    }

}
