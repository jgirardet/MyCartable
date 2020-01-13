import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
    signal itemClicked(int id, int matiere)
    headerPositioning: ListView.OverlayHeader
    spacing: 5
    height: parent.height
    width: parent.width
    clip: true
    delegate: RoundButton {
                height: 40
        radius: 10
        text: "mat id  : " + model.display['matiere']+ "//" +model.display['matiereNom']  + ": " + model.display["titre"] + "[" + model.display['activite']
        width: ListView.view.width
        onClicked: ListView.view.itemClicked(model.display.id, model.display.matiere)
        }
//    delegate: Rectangle {
//        width: rencentsListView.width
//        height: 40
//        radius: height *0.7
//        gradient: Gradient {
//            GradientStop {
//                position: 0.0
//                color: "lightsteelblue"
//            }
//            GradientStop {
//                position: 1.0
//                color: "blue"
//            }
//        }
//        Label {
//            text: modelData
//            anchors.centerIn: parent
//        }
//    }
}
