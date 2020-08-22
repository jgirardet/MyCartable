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

    delegate: Column {
        id: matieredelegate

        property alias matieretexte: matieretexte
        property string nom: modelData.nom
        property int matiereid: modelData.id

        Row {
            id: rowmatieretitre

            spacing: 5
            z: 1

            TextField {
                id: matieretexte

                height: 40
                width: 300

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
                    return modelData.activites.length.toString() + " " + (modelData.activites.length > 1 ? "rubriques" : "rubrique") + "\n" + modelData.nbPages + " " + (modelData.nbPages > 1 ? "pages" : "page");
                }

                anchors.verticalCenter: matieretexte.verticalCenter
                text: modelData.activites ? get_text() : ""
                font.pointSize: 8
                width: 60
            }

            ActionButtonMatiere {
                                onPressed: {
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

                states: State {
                    name: "toggled"

                    PropertyChanges {
                        target: toggleactivitebutton
                        rotation: -90
                    }

                }

                transitions: Transition {
                    NumberAnimation {
                        property: "rotation"
                        duration: 200
                        easing.type: Easing.InOutQuad
                    }

                }

            }

            ActionButtonMatiere {
                id: insertmatierebutton

                referent: matieretexte
                ToolTip.text: "Insérer une nouvelle matière"
                icon.source: "qrc:/icons/add-row"
            }

            ActionButtonMatiere {
                id: delmatierebutton

                referent: matieretexte
                ToolTip.text: "supprimer la matière : " + nom
                icon.source: "qrc:/icons/remove-row-red"
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
