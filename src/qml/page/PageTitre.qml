import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14

TextField {
    // des fois page est près mais pas titre ???
    //        ddb.newPageCreated.connect(forceActiveFocus);

    id: root

    property QtObject page
    property int textlen: 0

    onPageChanged: {
        if (page)
            text = page.titre;
        else
            text = "";
    }
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
            if (!page.model.count)
            page.addSection("TextSection");
;

    }

    background: Rectangle {
        color: page ? page.matiere.bgColor : ddb.colorMainMenuBar
        radius: 10
    }

}
