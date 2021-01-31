import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14
import "qrc:/qml/divers"
import "qrc:/qml/menu"

Rectangle {
    id: base

    property var activite
    property alias deplacePage: deplacePopup
    property alias pages: lv

    color: "transparent"
    height: lv.height + header.height + 10

    Column {
        spacing: 5

        Rectangle {
            id: header

            property MouseArea mousearea: headerMouseArea
            property Label label: headerLabel

            objectName: "header"
            height: 30
            color: activite.matiere.bgColor
            radius: 10
            width: base.width

            Label {
                id: headerLabel

                text: activite.nom
                anchors.centerIn: parent
            }

            MouseArea {
                id: headerMouseArea

                acceptedButtons: Qt.RightButton
                anchors.fill: parent
                onPressed: {
                    if (mouse.buttons == Qt.RightButton)
                        classeur.newPage(activite.id);

                }
            }

        }

        ListView {
            id: lv

            property int commonHeight: 30
            property alias deplacePopup: deplacePopup

            objectName: "lv"
            model: activite.pages
            spacing: 3
            width: base.width
            height: lv.contentItem.childrenRect.height

            DeplacePage {
                id: deplacePopup

                parent: lv
            }

            delegate: PageButton {
                id: but

                width: ListView.view.width
                height: lv.commonHeight
                borderDefaultWidth: 0
                bgColor: "#cdd0d3"
            }

        }

    }

}
