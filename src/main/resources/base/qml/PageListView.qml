import QtQuick 2.12
import QtQuick.Controls 2.12


ListView {
    height: parent.height
    width: parent.width
    spacing : 10
    delegate: Rectangle {
        height: 50
        width: ListView.view.width
        color: "blue"
        Label {text: modelData}
    }
}