import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
    id: exercicesListView
    objectName: "exercicesListView"
    property int commonHeight: 30
    property string headerText: "header"
    property string headerColor: "blue"
    header: Rectangle {
        id: exercicesHeader
        height: commonHeight
        color: headerColor
        width: ListView.view.width
        z: 2
        Label {
            text: headerText
            anchors.centerIn: parent
        }
    }
    headerPositioning: ListView.OverlayHeader
    width: parent.width
    height: parent.height / 2
    clip: true
    delegate: Button {
        objectName: "delegateExo"
        text: modelData.titre
        width: ListView.view.width
        height: commonHeight
    }
}
