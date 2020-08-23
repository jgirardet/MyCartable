import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    id: root

    property alias model: repeater.model
    property var ddb

    spacing: 3
    width: parent.width
    anchors.left: parent.left
    anchors.leftMargin: 20
    state: "hidden"
    states: [
        State {
            name: "visible"

            PropertyChanges {
                target: root
                height: undefined
                opacity: 1
            }

        },
        State {
            name: "hidden"

            PropertyChanges {
                target: root
                height: 0
                opacity: 0
            }

        }
    ]

    transitions: Transition {
        NumberAnimation {
            properties: "height, opacity"
            duration: 200
            easing.type: Easing.InOutQuad
        }

    }

    function addAndFocus(activId, pos) {
      repeater.model = ddb.addActivite(activId);
      let ac = repeater.itemAt(pos)
      ac.activitetext.selectAll()
      ac.activitetext.forceActiveFocus()
    }

    Repeater {
        id: repeater

        delegate: Row {
            id: rowactivite

            spacing: 5

            property string nom: modelData.nom
            property int nbPages: modelData.nbPages
            property int  activiteId: modelData.id
            property alias activitetext: activitetext

            TextField {
                id: activitetext

                width: 160
                height: 30
                selectByMouse: true
                focus: true
                function updateText(){
                  nom = text
                  ddb.updateActiviteNom(activiteId,nom)
                }
                Component.onCompleted: {
                  activitetext.text = nom
                  activitetext.onTextChanged.connect(activitetext.updateText)
                }
                background: Rectangle {
                    radius: 10
                    color: "lightcyan"
                    anchors.fill: parent
                }

            }

            Text {
                anchors.verticalCenter: activitetext.verticalCenter
                text: nbPages + " page" + (nbPages > 1 ? "s" : " ")
                width: 40
                font.pointSize: 8
            }

            ActionButtonMatiere {
                id: upactivitebutton

                referent: activitetext
                enabled: !parent.Positioner.isFirstItem
                icon.source: "qrc:/icons/arrow-up"
                ToolTip.text: "Monterla rubrique: " + (rowactivite.nom ?? "")
                onClicked: {
                    repeater.model = ddb.moveActiviteTo(activiteId, parent.Positioner.index - 1);
                }
            }

            ActionButtonMatiere {
                id: downactivitebutton

                referent: activitetext
                enabled: !parent.Positioner.isLastItem
                icon.source: "qrc:/icons/arrow-down"
                ToolTip.text: "Descendre la rubrique: " + rowactivite.nom
                onClicked: {
                    repeater.model = ddb.moveActiviteTo(activiteId, parent.Positioner.index + 1);
                }
            }

            ActionButtonMatiere {
                id: addactivitebutton

                referent: activitetext
                icon.source: "qrc:/icons/plus"
                ToolTip.text: "Ajouter une rubrique"
                onClicked: {
                    root.addAndFocus(activiteId, parent.Positioner.index)

                }
            }

            ActionButtonMatiere {
                id: removeactivitebutton

                referent: activitetext
                enabled: nbPages < 1
                icon.source: "qrc:/icons/removePage"
                ToolTip.text: "Supprimer la rubrique: " + rowactivite.nom
                onClicked: {
                    repeater.model = ddb.removeActivite(activiteId);
                }
            }

        }

    }



}
