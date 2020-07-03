import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

TextField {
    id: root

    property var page

    text: ddb.currentPage ? ddb.currentTitre : ""
    readOnly: ddb.currentPage == 0 ? true : false
    //  Layout.preferredWidth: parent.width
    //  Layout.preferredHeight: 50
    font.weight: Font.Bold
    font.capitalization: Font.AllUppercase
    color: ddb.currentMatiere ? ddb.currentMatiereItem.fgColor : "white"
    horizontalAlignment: TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter
    onTextChanged: {
        ddb.setCurrentTitre(text);
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
