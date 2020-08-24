import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

TextArea {
    id: root

    property var page
    property int textlen: 0

    text: ddb.currentPage ? ddb.currentTitre : ""
    readOnly: ddb.currentPage == 0 ? true : false
    //  Layout.preferredWidth: parent.width
    //  Layout.preferredHeight: 50
    font.bold: true
    font.pointSize: 16
    font.capitalization: Font.Capitalize
    font.family: ddb.fontMain
    horizontalAlignment: TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter
    onTextChanged: {
        ddb.setCurrentTitre(text);
        if (textlen < length)
            while (contentWidth > (width) - 10)font.pointSize--;
        else
            while (font.pointSize != 16) {
            font.pointSize++;
            if (contentWidth > (width - 10)) {
                font.pointSize--;
                return ;
            }
        };
        textlen = length;
    }
    Keys.onPressed: {
        if (event.key == Qt.Key_Return)
            if (!page.model.rowCount())
            ddb.addSection(ddb.currentPage, {
            "classtype": "TextSection"
        });
;

    }
    Component.onCompleted: {
        ddb.newPageCreated.connect(forceActiveFocus);
    }

    background: Rectangle {
        color: ddb.currentMatiere ? ddb.currentMatiereItem.bgColor : ddb.colorMainMenuBar
        radius: 10
    }

}
