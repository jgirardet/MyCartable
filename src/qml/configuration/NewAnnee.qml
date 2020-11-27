import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Dialog {
    id: root

    property alias annee: annee_id.text.text
    property alias classe: classe_id.text.text
    property alias alert: errortext

    onAccepted: {
        if (!annee || !classe) {
            root.open();
            errortext.visible = true;
            return ;
        } else {
            c_dtb.addDB("Annee", {
                "id": annee,
                "niveau": classe
            });
            //            ddb.newAnnee(annee, classe);
            parent.changerAnnee.close();
            parent.changerAnnee.open();
        }
    }
    onOpened: {
        let user = globus.getConfig("user_set");
        if (!globus.getConfig("user_set"))
            newUserDialog.open();

    }
    implicitWidth: 600
    title: "Entrer l'année et la classe"
    standardButtons: Dialog.Ok | Dialog.Cancel
    focus: true
    anchors.centerIn: Overlay.overlay

    NewUser {
        id: newUserDialog

        objectName: "newUserDialog"
        basePopup: root
    }

    contentItem: Column {
        LabeledInput {
            id: annee_id

            label.text: "Année :  "
            text.placeholderText: "ex : 2018 pour 2018/2019"

            text.validator: IntValidator {
                bottom: 2020
                top: 3000
            }

        }

        LabeledInput {
            id: classe_id

            label.text: "Classe :  "
            text.placeholderText: "ex : ce1, CM2, 6 ème B,  3è4, Ts2"
        }

        Label {
            id: errortext

            visible: false
            text: "Annee et classe doivent être remplies"
            color: "red"
        }

    }

}
