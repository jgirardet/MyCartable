import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3 as Dialogs13

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

    dialog: Dialogs13.FileDialog {
        property var busy

        function go_accepted() {
            var newPos = append ? page.model.count : position + 1;
            page.addSection(nom, newPos, {
                "path": fileUrl
            });
            root.busy.close();
        }

        title: "Choisir le fichier à importer"
        folder: shortcuts.pictures
        nameFilters: ["fichiers Images (*.jpg *.png *.bmp *.ppm *.gif, *.pdf)"]
        onAccepted: {
            root.busy.open();
            timer.start();
        }
    }

}
