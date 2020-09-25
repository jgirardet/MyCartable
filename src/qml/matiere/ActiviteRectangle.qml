import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14
import "qrc:/qml/divers"
import "qrc:/qml/menu"

Rectangle {
    id: base

    property var model

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
            color: ddb ? ddb.currentMatiereItem.bgColor : "transparent"
            radius: 10
            width: base.width

            Label {
                id: headerLabel

                text: base.model.nom
                anchors.centerIn: parent
            }

            MouseArea {
                id: headerMouseArea

                acceptedButtons: Qt.RightButton
                anchors.fill: parent
                onPressed: {
                    if (mouse.buttons == Qt.RightButton)
                    {
                        ddb.newPage(model.id);
                    }

                }
            }

        }

        ListView {
            id: lv

            property int commonHeight: 30
            property alias deplacePopup: deplacePopup

            objectName: "lv"
            model: base.model.pages
            spacing: 3
            width: base.width
            height: lv.contentItem.childrenRect.height

            DeplacePage {
                id: deplacePopup
                objectName: "deplacepage"
            }

            delegate: PageButton {
                id: but

                width: ListView.view.width
                height: lv.commonHeight
                model: modelData
                borderDefaultWidth: 0
                Component.onCompleted: {
                    background.color = "#cdd0d3";
                }
            }

        }

    }

}
