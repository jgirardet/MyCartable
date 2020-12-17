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
            //            ddb.addSection(ddb.currentPage, {
            //                "string": contentItem.text,
            //                "classtype": nom,
            //                "position": append ? ddb.pageModel.count : position + 1
            //            });
            uiManager.buzyIndicator = true;
            let string = contentItem.text;
            let classtype = nom;
            if (string.includes("+"))
                classtype = "AdditionSection";
            else if (string.includes("-"))
                classtype = "SoustractionSection";
            else if (string.includes("*"))
                classtype = "MultiplicationSection";
            else if (string.includes("/"))
                classtype = "DivisionSection";
            var newPos = append ? page.model.count : position + 1;
            page.addSection(classtype, newPos, {
                "string": string
            });
            uiManager.buzyIndicator = false;
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
