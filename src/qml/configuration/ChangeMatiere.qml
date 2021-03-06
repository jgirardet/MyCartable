import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    id: root

    property QtObject api

    function addAndFocus(matid, pos) {
        api.addMatiere(matid);
        parent.applyDegradeToMatiere(pos, true);
    }

    model: api.getMatieres(groupeid)
    width: parent.width
    anchors.leftMargin: 20
    anchors.left: parent.left
    spacing: 5
    height: childrenRect.height
    clip: true

    delegate: Column {
        id: matieredelegate

        property alias matieretexte: matieretexte
        property string nom: modelData.nom
        property string matiereid: modelData.id
        property alias activitelist: activitelist
        property int nbPages: modelData.nbPages

        Row {
            id: rowmatieretitre

            spacing: 5
            z: 1

            TextField {
                id: matieretexte

                function updateText() {
                    if (text) {
                        nom = text;
                        api.updateMatiereNom(matiereid, nom);
                    }
                }

                height: 40
                width: 200
                font.bold: true
                font.pointSize: 12
                Component.onCompleted: {
                    matieretexte.text = nom;
                    matieretexte.onTextChanged.connect(matieretexte.updateText);
                }

                background: Rectangle {
                    color: modelData.bgColor ?? "transparent"
                    radius: 10
                }

            }

            Text {
                function get_text() {
                    return modelData.activites.length.toString() + " " + (modelData.activites.length > 1 ? "rubriques" : "rubrique") + "\n" + nbPages + " " + (nbPages > 1 ? "pages" : "page");
                }

                anchors.verticalCenter: matieretexte.verticalCenter
                text: modelData.activites ? get_text() : ""
                font.pointSize: 8
                width: 60
            }

            ActionButtonMatiere {
                id: toggleactivitebutton

                onPressed: {
                    if (state == "no_activite")
                        activitelist.addAndFocus(matiereid, 0, true);

                    if (state == "toggled") {
                        activitelist.state = "hidden";
                        state = null;
                    } else {
                        activitelist.state = "visible";
                        state = "toggled";
                    }
                }
                referent: matieretexte
                ToolTip.text: !activitelist.state ? "Afficher les rubriques" : "Masquer les rubriques"
                icon.source: "qrc:/icons/less-than"
                states: [
                    State {
                        name: "toggled"

                        PropertyChanges {
                            target: toggleactivitebutton
                            rotation: -90
                        }

                    },
                    State {
                        name: "no_activite"
                        when: !activitelist.model.length

                        PropertyChanges {
                            target: toggleactivitebutton
                            icon.source: "qrc:/icons/plus"
                            ToolTip.text: "Ajouter une rubrique"
                        }

                    }
                ]

                transitions: Transition {
                    NumberAnimation {
                        property: "rotation"
                        duration: 200
                        easing.type: Easing.InOutQuad
                    }

                }

            }

            ActionButtonMatiere {
                id: upmatierebutton

                referent: matieretexte
                enabled: index > 0
                ToolTip.visible: false
                icon.source: "qrc:/icons/arrow-up"
                onClicked: {
                    api.moveMatiereTo(matiereid, index - 1);
                    root.parent.applyDegradeToMatiere(undefined, true);
                }
            }

            ActionButtonMatiere {
                id: downlmatierebutton

                referent: matieretexte
                enabled: index < (root.count - 1)
                ToolTip.visible: false
                icon.source: "qrc:/icons/arrow-down"
                onClicked: {
                    api.moveMatiereTo(matiereid, index + 1);
                    root.parent.applyDegradeToMatiere(undefined, true);
                }
            }

            ActionButtonMatiere {
                id: insertmatierebutton

                referent: matieretexte
                ToolTip.text: "Insérer une nouvelle matière"
                icon.source: "qrc:/icons/add-row"
                onClicked: {
                    root.addAndFocus(matiereid, index);
                }
            }

            ActionButtonMatiere {
                id: delmatierebutton

                enabled: nbPages == 0
                referent: matieretexte
                ToolTip.text: "supprimer la matière : " + nom
                icon.source: "qrc:/icons/remove-row-red"
                onClicked: {
                    api.removeMatiere(matiereid);
                    root.parent.applyDegradeToMatiere(undefined, true);
                }
            }

        }

        ChangeActivite {
            id: activitelist

            api: root.api
            matiere: modelData.id
        }

    }

}
