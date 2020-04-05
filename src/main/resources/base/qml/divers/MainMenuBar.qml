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
  }

  Dialog {
    id: changerAnnee
    objectName: "changerAnnee"
    height: 300
    title: "Cliquer sur l'année choisie"
    contentItem: ListView {
      model: ddb.getMenuAnnees()
      width: delegate.width
      height: 200 //delegate.height * count
      delegate: ValueButton {
        onClicked: {
          ddb.changeAnnee(value)
          changerAnnee.close()
        }
        text: "mon année de " + modelData.niveau + " en " + modelData.id + "/" + (modelData.id + 1)
        value: modelData.id
      }

    }

    standardButtons: Dialog.Cancel
  }

}