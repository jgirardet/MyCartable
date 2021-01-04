import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/menu"

TextEdit {
    id: root

    property bool doNotUpdate: false
    required property Item sectionItem
    required property QtObject section

    function setStyleFromMenu(params) {
        var res = section.updateTextSectionOnMenu(text, cursorPosition, selectionStart, selectionEnd, params);
        if (!res["eventAccepted"]) {
            // ici event Accepted veut dire : on ne remet pas à jour le text
            return ;
        } else {
            doNotUpdate = true;
            text = res["text"];
            cursorPosition = res["cursorPosition"];
        }
    }

    function showMenu() {
        var s_start = Math.min(root.selectionStart, root.selectionEnd);
        var s_end = Math.max(root.selectionEnd, root.selectionEnd);
        menuFlottantText.ouvre(root);
        root.cursorPosition = s_start;
        root.moveCursorSelection(s_end, TextEdit.SelectCharacters);
    }

    font.pointSize: 16 // necéssaire pour que les taille html soient corrent == taille de p
    height: contentHeight + 0
    width: sectionItem.width
    textFormat: TextEdit.RichText
    leftPadding: 0
    rightPadding: 0
    selectByMouse: true
    wrapMode: TextEdit.Wrap
    Keys.onPressed: {
        var res = section.updateTextSectionOnKey(text, cursorPosition, selectionStart, selectionEnd, JSON.stringify(event));
        event.accepted = res["eventAccepted"];
        if (event.accepted == false) {
            return ;
        } else {
            doNotUpdate = true;
            text = res["text"];
            cursorPosition = res["cursorPosition"];
        }
    }
    onSectionChanged: {
        var res = section.loadTextSection();
        doNotUpdate = true;
        text = res["text"];
        cursorPosition = res["cursorPosition"];
    }
    onTextChanged: {
        if (doNotUpdate) {
            doNotUpdate = false;
            return ;
        } else {
            var res = section.updateTextSectionOnChange(text, cursorPosition, selectionStart, selectionEnd);
            if (res["eventAccepted"]) {
                // ici event Accepted veut dire : on ne remet pas à jour le text
                return ;
            } else {
                doNotUpdate = true;
                text = res["text"];
                cursorPosition = res["cursorPosition"];
            }
        }
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
            }
        }
    }

}
