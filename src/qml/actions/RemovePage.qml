import QtQuick 2.15
import QtQuick.Controls 2.15

BasePageAction {
    id: root

    icon.source: "qrc:///icons/removePage"
    onTriggered: {
        dialog.open();
    }
    tooltip: "Supprimer la page ?"
    shortcut: ""

    dialog: Dialog {
        property alias confirmation: confirmdialog

        anchors.centerIn: Overlay.overlay
        onAccepted: {
            if (page.model.count)
                confirmdialog.open();
            else
                confirmdialog.accept();
        }
        standardButtons: Dialog.Ok | Dialog.Cancel
        title: "Supprimer cette page ?"

        Dialog {
            id: confirmdialog

            parent: root.dialog.parent
            anchors.centerIn: Overlay.overlay
            onAccepted: page.classeur.deletePage()
            standardButtons: Dialog.Ok | Dialog.Cancel
            title: "Attention cette page n'est pas vide, la supprimer quand même ?"
        }

    }

}
