import QtQuick.Dialogs 1.3 as Dialogs13

BasePageAction {
    icon.source: "qrc:///icons/newImageSection"
    nom: "ImageSection"
    onTriggered: dialog.open()
    tooltip: "Ajouter une image/un document"
    shortcut: ""

    dialog: Dialogs13.FileDialog {
        title: "Choisir le fichier à importer"
        folder: shortcuts.pictures
        nameFilters: ["fichiers Images (*.jpg *.png *.bmp *.ppm *.gif, *.pdf)"]
        onAccepted: {
            uiManager.buzyIndicator = true;
            var newPos = append ? ddb.pageModel.count : position + 1;
            ddb.addSection(ddb.currentPage, {
                "path": fileUrl,
                "classtype": nom,
                "position": newPos
            });
        }
    }

}
