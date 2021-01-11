import QtQuick 2.15
//import QtQuick.Dialogs 1.3 // as Dialogs13
import QtQuick.Controls 2.15
import Qt.labs.platform 1.1 as Labs

BasePageAction {
    id: root

    property Timer timer
    property Dialog busy

    icon.source: "qrc:///icons/newImageSection"
    nom: "ImageSection"
    onTriggered: dialog.open()
    tooltip: "Ajouter une image/un document"
    shortcut: ""

    timer: Timer {
        id: timer

        interval: 1
        repeat: false
        onTriggered: {
            dialog.go_accepted();
        }
    }

    dialog: Labs.FileDialog {

        function go_accepted() {
            var newPos = append ? page.model.count : position + 1;
            page.addSection(nom, newPos, {
                "path": file
            });
            root.busy.close();
        }

        title: "Choisir le fichier à importer"
        folder: Labs.StandardPaths.writableLocation(Labs.StandardPaths.PicturesLocation)
        nameFilters: ["fichiers Images (*.jpg *.jpeg *.png *.bmp *.ppm *.gif, *.pdf)"]
        onAccepted: {
            root.busy.open();
            timer.start();
        }
    }

}
