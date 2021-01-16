import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    id: root

    property alias model: repeater.model
    property QtObject api
    property string matiere
    property alias repeater: repeater

    function addAndFocus(activId, pos, append) {
        repeater.model = api.addActivite(activId, append);
        let ac = repeater.itemAt(pos);
        ac.activitetext.selectAll();
        ac.activitetext.forceActiveFocus();
    }

    model: api.getActivites(modelData.id)
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

    Repeater {
        id: repeater

        delegate: Row {
            id: rowactivite

            property string nom: modelData.nom
            property int nbPages: modelData.nbPages
            property string activiteId: modelData.id
            property alias activitetext: activitetext

            spacing: 5

            TextField {
                id: activitetext

                function updateText() {
                    if (text) {
                        nom = text;
                        api.updateActiviteNom(activiteId, nom);
                    }
                }

                width: 160
                height: 30
                selectByMouse: true
                focus: true
                Component.onCompleted: {
                    activitetext.text = nom;
                    activitetext.onTextChanged.connect(activitetext.updateText);
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
                    repeater.model = api.moveActiviteTo(activiteId, parent.Positioner.index - 1);
                }
            }

            ActionButtonMatiere {
                id: downactivitebutton

                referent: activitetext
                enabled: !parent.Positioner.isLastItem
                icon.source: "qrc:/icons/arrow-down"
                ToolTip.text: "Descendre la rubrique: " + rowactivite.nom
                onClicked: {
                    repeater.model = api.moveActiviteTo(activiteId, parent.Positioner.index + 1);
                }
            }

            ActionButtonMatiere {
                id: addactivitebutton

                referent: activitetext
                icon.source: "qrc:/icons/plus"
                ToolTip.text: "Ajouter une rubrique"
                onClicked: {
                    root.addAndFocus(activiteId, parent.Positioner.index);
                }
            }

            ActionButtonMatiere {
                id: removeactivitebutton

                referent: activitetext
                enabled: nbPages < 1
                icon.source: "qrc:/icons/removePage"
                ToolTip.text: "Supprimer la rubrique: " + rowactivite.nom
                onClicked: {
                    repeater.model = api.removeActivite(activiteId);
                }
            }

        }

    }

    transitions: Transition {
        NumberAnimation {
            properties: "height, opacity"
            duration: 200
            easing.type: Easing.InOutQuad
        }

    }

}
