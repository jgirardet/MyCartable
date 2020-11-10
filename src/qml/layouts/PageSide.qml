import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/divers"
import "qrc:/qml/matiere"
import "qrc:/qml/page"

Rectangle {
    id: base

    property alias contenu: mousearea.contenu
    property bool bigLayout

    color: ddb.colorFond
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    state: "small"
    states: [
        State {
            name: "small"

            PropertyChanges {
                target: recents
                width: 50
            }

        },
        State {
            name: "big"

            PropertyChanges {
                target: recents
                width: Math.min(250, parent.width / 3)
            }

        }
    ]

    MouseArea {
        id: mousearea

        property var contenu

        onContenuChanged: {
            if (contenu)
                contenu.parent = mousearea;

        }
        anchors.fill: parent
        hoverEnabled: true
        onContainsMouseChanged: {
            if (containsMouse)
                base.state = "big";
            else if (!containsMouse && !base.bigLayout)
                base.state = "small";
        }
        acceptedButtons: Qt.NoButton
    }

    Behavior on width {
        PropertyAnimation {
        }

    }

}
