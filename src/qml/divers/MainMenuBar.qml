import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/configuration"

MenuBar {
    id: mainMenuBar

    property alias changerAnnee: changerAnnee_id

    Menu {
        //        Action {
        //            text: qsTr("&Peupler la base")
        //            onTriggered: ddb.peupler()
        //        }

        title: qsTr("&Fichier")

        Action {
            text: qsTr("&Changer d'année")
            onTriggered: changerAnnee.open()
        }

        Action {
            text: qsTr("&Ajouter les matieres par défault")
            onTriggered: repeupler_id.open()
        }

    }

    Dialog {
        id: changerAnnee_id

        objectName: "changerAnnee"
        height: 300
        width: 600
        title: "Cliquer sur l'année choisie"
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Cancel
        onOpened: {
            //to refresh
            contentItem.model = ddb.getMenuAnnees();
        }

        contentItem: ListView {
            id: lv

            width: delegate.width
            height: 400 //delegate.height * count
            spacing: 5

            delegate: ValueButton {
                onClicked: {
                    ddb.changeAnnee(value);
                    changerAnnee_id.close();
                }
                text: "mon année de " + modelData.niveau + " en " + modelData.id + "/" + (modelData.id + 1)
                value: modelData.id
            }

            footer: Button {
                text: "Ajouter une année"
                onClicked: newAnneeDialog.open()
            }

        }

    }

    NewAnnee {
        id: newAnneeDialog
    }

    Dialog {
        id: repeupler_id

        objectName: "repeupler"
        height: 300
        width: 600
        title: "Recréer les matières par défault ?"
        standardButtons: Dialog.Ok | Dialog.Cancel
        anchors.centerIn: Overlay.overlay
        onOpened: {
            if (!ddb.anneeActive)
                changerAnnee_id.open();

        }
        onAccepted: ddb.peuplerLesMatieresParDefault(ddb.anneeActive)

        contentItem: Label {
            text: "Ceci ajoutera toute les matières par défault, confirmer ?"
        }

    }

    background: Rectangle {
        anchors.fill: parent
        color: ddb.colorMainMenuBar
    }

}
