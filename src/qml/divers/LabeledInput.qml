import QtQuick 2.15
import QtQuick.Controls 2.15

Row {
    //    anchors.fill: parent

    //    property alias labelText: labelid.text
    //    property alias placeholderText: textfieldid.placeholderText
    property alias label: labelid
    property alias text: textfieldid

    Label {
        id: labelid

        //        text: "Année :  "
        anchors.verticalCenter: parent.verticalCenter
    }

    TextField {
        //        onAccepted: dialog.accept()
        //        placeholderText: "ex : 2018 pour 2018/2019"
        //        color: Qt.darker("lavender")

        id: textfieldid

        anchors.verticalCenter: parent.verticalCenter

        background: Rectangle {
            anchors.fill: parent
            color: "white"
            border.color: "black"
        }

    }

}
