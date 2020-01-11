import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
    id: rencentsListView
    headerPositioning: ListView.OverlayHeader
    spacing: 5
    height: parent.height
    width: parent.width
    clip: true
    delegate: RoundButton {
                height: 40
        radius: 10
        text: modelData['matiere']  + ": " + modelData["titre"]
        width: rencentsListView.width
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
