import QtQuick 2.14
import QtQuick.Controls 2.14

TextEdit {

    id: root

    property int sectionId
    property var sectionItem
    property bool doNotUpdate: false

    function setStyleFromMenu(params) {
        var res = ddb.updateTextSectionOnMenu(sectionId, text, cursorPosition, selectionStart, selectionEnd, params);
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
        uiManager.menuFlottantText.ouvre(root);
        root.cursorPosition = s_start;
        root.moveCursorSelection(s_end, TextEdit.SelectCharacters);
    }

    font.pointSize: 20 // necéssaire pour que les taille html soient corrent == taille de p
    height: contentHeight + 30
    width: sectionItem.width
    textFormat: TextEdit.RichText
    leftPadding: 10
    rightPadding: 10
    selectByMouse: true
    wrapMode: TextEdit.Wrap
    Keys.onPressed: {
        var res = ddb.updateTextSectionOnKey(sectionId, text, cursorPosition, selectionStart, selectionEnd, JSON.stringify(event));
        event.accepted = res["eventAccepted"];
        if (event.accepted == false) {
            return ;
        } else {
            doNotUpdate = true;
            text = res["text"];
            cursorPosition = res["cursorPosition"];
        }
    }
    onSectionIdChanged: {
        var res = ddb.loadTextSection(sectionId);
        doNotUpdate = true;
        text = res["text"];
        cursorPosition = res["cursorPosition"];
    }
    onTextChanged: {
        if (doNotUpdate) {
            doNotUpdate = false;
            return ;
        } else {
            var res = ddb.updateTextSectionOnChange(sectionId, text, cursorPosition, selectionStart, selectionEnd);
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
