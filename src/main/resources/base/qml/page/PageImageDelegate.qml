import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
        property var section
        height: 600
        width: 600
        color: "blue"
        Image {
        id: image
        source: "file://"+section.content
        asynchronous: true

        anchors.fill : parent
        }
    }