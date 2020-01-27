import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
        height: 50
        width: 200
        color: "blue"
        property alias text:editable.text
        Label {
        id: editable
        anchors.fill : parent
        }
    }