import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

ListView {


    id: root

    width: parent.width
    anchors.leftMargin: 20
    anchors.left: parent.left
    spacing: 5
    height: childrenRect.height
    clip: true
    property var bdd

  function addAndFocus(matid, pos) {
      ddb.addMatiere(matid);
      parent.applyDegradeToMatiere(pos, true)
    }

    delegate: Column {
        id: matieredelegate

        property alias matieretexte: matieretexte
        property string nom: modelData.nom
        property int matiereid: modelData.id
        property alias activitelist: activitelist
        property int nbPages: modelData.nbPages

        Row {
            id: rowmatieretitre

            spacing: 5
            z: 1

            TextField {
                id: matieretexte

                height: 40
                width: 200

                font.bold: true
                font.pointSize: 12
                function updateText(){
                  nom = text
                  ddb.updateMatiereNom(matiereid,nom)
                }
                Component.onCompleted: {
                  matieretexte.text = nom
                  matieretexte.onTextChanged.connect(matieretexte.updateText)
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

                                onPressed: {
                                    if (state == "no_activite"){
                                    activitelist.addAndFocus(matiereid.toString(), 0)
                                    }
                                    if (state == "toggled") {
                                        activitelist.state = "hidden";
                                        state = null;
                                    } else {
                                        activitelist.state = "visible";
                                        state = "toggled";
                                    }
                                }

                id: toggleactivitebutton

                referent: matieretexte
                ToolTip.text: !activitelist.state ? "Afficher les rubriques" : "Masquer les rubriques"
                icon.source: "qrc:/icons/less-than"

                states: [State {
                    name: "toggled"
                    PropertyChanges {
                        target: toggleactivitebutton
                        rotation: -90
                    }

                }, State {
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
//                ToolTip.text: "monter la matière : " + nom
                ToolTip.visible: false
                icon.source: "qrc:/icons/arrow-up"
                onClicked: {
                    ddb.moveMatiereTo(matiereid, index - 1);
                    root.parent.applyDegradeToMatiere(undefined, true)

                }
            }

            ActionButtonMatiere {
                id: downlmatierebutton
                referent: matieretexte
                enabled: index < (root.count - 1)
                ToolTip.visible: false
//                ToolTip.text: "descendre la matière : " + nom // enlever car genant
                icon.source: "qrc:/icons/arrow-down"
                onClicked: {
                    ddb.moveMatiereTo(matiereid, index + 1);
                    root.parent.applyDegradeToMatiere(undefined, true)

                }
            }
            ActionButtonMatiere {
                id: insertmatierebutton

                referent: matieretexte
                ToolTip.text: "Insérer une nouvelle matière"
                icon.source: "qrc:/icons/add-row"
                onClicked: {
                    root.addAndFocus(matiereid, index)

                }
            }

            ActionButtonMatiere {
                id: delmatierebutton
                enabled: nbPages == 0
                referent: matieretexte
                ToolTip.text: "supprimer la matière : " + nom
                icon.source: "qrc:/icons/remove-row-red"
                onClicked: {
                    ddb.removeMatiere(matiereid);
                    root.parent.applyDegradeToMatiere(undefined, true)
                }
            }

        }

        ChangeActivite {

            id: activitelist
            ddb: root.bdd
            model: root.bdd ?  root.bdd.getActivites(modelData.id) : 0
//            Component.onCompleted:{
//            print(ddb, root.bdd)
//            print(root.bdd.getActivites(modelData.id))
//
//            activitelist.model = ddb.getActivites(modelData.id)
//            }
        }

    }

}
