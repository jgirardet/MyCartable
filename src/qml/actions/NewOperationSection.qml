import QtQuick 2.15
import QtQuick.Controls 2.15

BasePageAction {
    icon.source: "qrc:///icons/newOperationSection"
    nom: "OperationSection"
    onTriggered: dialog.open()
    tooltip: "Ajouter une opération"
    shortcut: ""

    dialog: Dialog {
        id: dialogoperation

        implicitWidth: 300
        title: "Entrer 2 nombres séparés\npar +,-,* ou /"
        standardButtons: Dialog.Ok | Dialog.Cancel
        focus: true
        onAccepted: {
            ddb.addSection(ddb.currentPage, {
                "string": contentItem.text,
                "classtype": nom,
                "position": append ? ddb.pageModel.count : position + 1
            });
            contentItem.clear();
        }

        contentItem: TextField {
            focus: true
            onAccepted: dialogoperation.accept()

            background: Rectangle {
                anchors.fill: parent
                color: "white"
            }

        }

    }

}
