import QtQuick 2.12
import QtQuick.Controls 1.4


ToolBar {
    id: pageToolBar
    signal nouveau()
//    property alias newClicked: monbut.QAbstractButton.clicked
//    property alias newClicked: mainRow.newButton.clicked
//    Row {
//            id: mainRow
//            anchors.fill: parent
     Button {
        id: monbut
        text: "okmk"
     }
            ToolButton {
                id: newButton
                iconSource: "qrc:///icons/hdd.png"
                onClicked: pageToolBar.nouveau()
            }
//     }
}