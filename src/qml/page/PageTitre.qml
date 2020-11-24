import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14

TextArea {
    id: root

    property QtObject page
    property int textlen: 0

    text: page ? page.titre : "" //ddb.currentPage ? ddb.currentTitre : ""
    readOnly: !page
    //  Layout.preferredWidth: parent.width
    //  Layout.preferredHeight: 50
    font.bold: true
    font.pointSize: 16
    font.capitalization: Font.Capitalize
    font.family: ddb.fontMain
    horizontalAlignment: TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter
    onTextChanged: {
        if (page)
            // des fois page est près mais pas titre ???
            page.titre = text;

        if (textlen < length) {
            while (contentWidth > (width) - 10) {
                font.pointSize--;
                if (font.pointSize <= 4)
                    break;

            }
        } else {
            while (font.pointSize != 16) {
                font.pointSize++;
                if (contentWidth > (width - 10)) {
                    font.pointSize--;
                    return ;
                }
            }
        }
        textlen = length;
    }
    Keys.onPressed: {
        if (event.key == Qt.Key_Return)
            if (!page.model.rowCount())
            ddb.addSection(page.id, {
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
