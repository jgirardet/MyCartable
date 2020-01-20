import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
    signal itemClicked(int id)
    headerPositioning: ListView.OverlayHeader
    spacing: 5
    height: parent.height
    width: parent.width
    clip: true
    delegate: RoundButton {
        id: _buttonDelegateRecents
        objectName: "_buttonDelegateRecents"
        height: 40
        radius: 10
        text: "mat id  : " + model.display['matiere']+ "//" +model.display['matiereNom']  + ": " + model.display["titre"] + "[" + model.display['activite']
        width: ListView.view.width
        onClicked: ListView.view.itemClicked(model.display.id)
        }
}

