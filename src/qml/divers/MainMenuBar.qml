import QtQuick 2.14
import QtQuick.Controls 2.14

MenuBar {
    id: mainMenuBar

    Menu {
        title: qsTr("&Fichier")

        Action {
            text: qsTr("&Changer d'année")
            onTriggered: changerAnnee.open()
        }

        Action {
            text: qsTr("&Peupler la base")
            onTriggered: ddb.peupler()
        }

    }

    Dialog {
        id: changerAnnee

        objectName: "changerAnnee"
        height: 300
        title: "Cliquer sur l'année choisie"
        standardButtons: Dialog.Cancel

        contentItem: ListView {
            model: ddb.getMenuAnnees()
            width: delegate.width
            height: 200 //delegate.height * count

            delegate: ValueButton {
                onClicked: {
                    ddb.changeAnnee(value);
                    changerAnnee.close();
                }
                text: "mon année de " + modelData.niveau + " en " + modelData.id + "/" + (modelData.id + 1)
                value: modelData.id
            }

        }

    }

    background: Rectangle {
        anchors.fill: parent
        color: ddb.colorMainMenuBar
    }

}
