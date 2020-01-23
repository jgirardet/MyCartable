import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
//    signal itemClicked()
    signal itemClicked(int id, int matiere)
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
        text: "mat id  : " + model.page['matiere']+ "//" +model.page['matiereNom']  + ": " + model.page["titre"] + "[" + model.page['activite']
        width: ListView.view.width
        onClicked: ListView.view.itemClicked(model.page.id, model.page.matiere)
        }
}

