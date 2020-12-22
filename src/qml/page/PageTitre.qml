import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14

TextField {
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
    font.bold: true
    font.pointSize: 16
    font.capitalization: Font.Capitalize
    horizontalAlignment: TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter
    onTextChanged: {
        if (page)
            page.titre = text;

    }
    Keys.onPressed: {
        if (event.key == Qt.Key_Return) {
            if (!page.model.count)
                page.addSection("TextSection");

        }
    }

    background: Rectangle {
        color: page ? page.matiere.bgColor : "transparent"
        radius: 10
    }

}
