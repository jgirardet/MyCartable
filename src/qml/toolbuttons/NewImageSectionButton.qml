import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Dialogs 1.3 as Dialogs13

NewSectionButton {
    id: root

    sectionName: "ImageSection"
    ToolTip.text: "Ajouter une Image"

    dialog: Dialogs13.FileDialog {
        id: dialogcomp

        title: "Choisir une image à importer"
        folder: shortcuts.pictures
        nameFilters: ["fichiers Images (*.jpg *.png *.bmp *.ppm, *.pdf)"]
        onAccepted: {
            ddb.addSection(ddb.currentPage, {
                "path": fileUrl,
                "classtype": "ImageSection",
                "position": typeof root.targetIndex == "number" ? root.targetIndex : null
            });
        }
    }

}
