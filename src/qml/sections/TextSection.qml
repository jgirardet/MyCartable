import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/menu"

TextEdit {
    id: root

    property bool doNotUpdate: false
    required property Item sectionItem
    required property QtObject section
    property alias menu: menuFlottantText

    function appyChangeFromSection() {
        doNotUpdate = true;
        text = section.text;
        cursorPosition = section.cursor;
    }

    function setStyleFromMenu(params) {
        section.updateTextSectionOnMenu(text, cursorPosition, selectionStart, selectionEnd, params);
    }

    function showMenu() {
        var s_start = Math.min(root.selectionStart, root.selectionEnd);
        var s_end = Math.max(root.selectionEnd, root.selectionEnd);
        menuFlottantText.ouvre(root);
        root.cursorPosition = s_start;
        root.moveCursorSelection(s_end, TextEdit.SelectCharacters);
    }

    onSectionChanged: {
        section.loadTextSection();
        appyChangeFromSection();
    }
    font.pointSize: 14 // necéssaire pour que les taille html soient corrent == taille de p
    height: contentHeight + 0
    width: sectionItem.width
    textFormat: TextEdit.RichText
    leftPadding: 0
    rightPadding: 0
    selectByMouse: true
    wrapMode: TextEdit.Wrap
    Keys.onPressed: {
        if ((event.key == Qt.Key_Z) && (event.modifiers & Qt.ControlModifier)) {
            if (event.modifiers & Qt.ShiftModifier)
                section.undoStack.redo();
            else
                section.undoStack.undo();
            event.accepted = true;
            return ;
        }
        section.updateTextSectionOnKey(text, cursorPosition, selectionStart, selectionEnd, JSON.stringify(event));
        //  ici event Accepted veut dire : on ne remet pas à jour le text
        event.accepted = section.accepted;
    }
    onTextChanged: {
        if (doNotUpdate) {
            doNotUpdate = false;
            return ;
        } else {
            section.updateTextSectionOnChange(text, cursorPosition, selectionStart, selectionEnd);
        }
    }

    Connections {
        function onForceUpdate() {
            root.appyChangeFromSection();
            root.forceActiveFocus();
        }

        target: section
    }

    MenuFlottantText {
        id: menuFlottantText
    }

    MouseArea {
        id: mousearea

        anchors.fill: root
        acceptedButtons: Qt.RightButton
        onPressed: {
            if (mouse.button == Qt.RightButton) {
                root.showMenu();
                mouse.accepted = true;
            } else if (mouse.button == Qt.RightButton) {
                section.cursor = root.cursorPosition;
            }
        }
    }

}
