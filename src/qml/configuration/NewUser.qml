import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Dialog {
    //        contentItem.clear();
    //        parent.close();

    id: root

    property QtObject basePopup
    property alias nom: nom_id.text.text
    property alias prenom: prenom_id.text.text
    property alias alert: errortext

    onAccepted: {
        if (!nom || !prenom) {
            root.open();
            errortext.visible = true;
            return ;
        } else {
            ddb.newUser(nom, prenom);
        }
    }
    onRejected: {
        basePopup.close();
    }
    implicitWidth: 600
    title: "Entrer nom et prénom de l'élève"
    standardButtons: Dialog.Ok | Dialog.Cancel
    focus: true
    anchors.centerIn: Overlay.overlay

    contentItem: Column {
        LabeledInput {
            id: nom_id

            label.text: "Nom : "
            text.placeholderText: "                "
        }

        LabeledInput {
            id: prenom_id

            label.text: "Prenom : "
            text.placeholderText: "                "
        }

        Label {
            id: errortext

            visible: false
            text: "Nom et Prénom doivent être remplis"
            color: "red"
        }

    }

}
