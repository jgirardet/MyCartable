import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
    id: root

    required property Item sectionItem // basepagedelegate
    required property QtObject section

    width: sectionItem.width
    height: contentHeight + 30
    font.pointSize: 12
    text: section.content
    Component.onCompleted: cursorPosition = section.curseur // seulement pour init pas binding (cursorpos peut trop changer)
    onCursorPositionChanged: {
        if (!section.isEquationFocusable(cursorPosition))
            cursorPosition = section.curseur;

    }
    font.family: "Code New Roman"
    Keys.onPressed: {
        section.update(cursorPosition, JSON.stringify(event));
        cursorPosition = section.curseur;
        event.accepted = true;
    }

    background: Rectangle {
        anchors.fill: parent
        color: "white"
    }

}
