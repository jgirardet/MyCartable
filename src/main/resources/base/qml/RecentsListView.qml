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
        text: "|id=" + modelData.id + "/" + modelData.activiteIndex + " mat=" + modelData.matiere + " " +modelData.titre
        width: ListView.view.width
        onClicked: ListView.view.itemClicked(modelData.id, modelData.matiere)
        }
}

