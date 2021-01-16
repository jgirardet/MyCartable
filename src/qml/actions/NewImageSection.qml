import MyCartable 1.0
import Qt.labs.platform 1.1 as Labs
import QtQuick 2.15
import QtQuick.Controls 2.15

BasePageAction {
    id: root

    property Timer timer
    property Dialog busy
    property QtObject db

    icon.source: "qrc:///icons/newImageSection"
    nom: "ImageSection"
    onTriggered: dialog.open()
    tooltip: "Ajouter une image/un document"
    shortcut: ""

    db: Database {
        id: database
    }

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
        folder: database.getConfig("last_image_open_folder") ? database.getConfig("last_image_open_folder") : Labs.StandardPaths.writableLocation(Labs.StandardPaths.HomeLocation)
        nameFilters: ["fichiers Images (*.jpg *.jpeg *.png *.bmp *.ppm *.gif, *.pdf)"]
        onAccepted: {
            root.busy.open();
            database.setConfig("last_image_open_folder", folder.toString());
            timer.start();
        }
    }

}
