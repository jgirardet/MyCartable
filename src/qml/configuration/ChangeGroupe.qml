import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    id: root

    property alias colordialog: colordialog

    width: 600
    spacing: 10
    clip: true

    RefColorDialog {
        id: colordialog

        modality: Qt.WindowModal
    }

    delegate: Column {
        id: groupe

        property alias text: groupename
        property alias colorbutton: colorbutton
        property alias changematiere: changematiere
        property color baseColor: modelData.bgColor
        property int groupeid: modelData.id
        property string nom: modelData.nom
        property bool firstLoad: true

        function applyDegradeToMatiere(focus_after, reload) {
            if (reload)
                changematiere.model = ddb.reApplyGroupeDegrade(groupeid);
            else
                changematiere.model = ddb.applyGroupeDegrade(groupeid, baseColor);
            if (focus_after != undefined) {
                changematiere.itemAtIndex(focus_after).matieretexte.selectAll();
                changematiere.itemAtIndex(focus_after).matieretexte.forceActiveFocus();
            }
        }

        width: root.width
        onBaseColorChanged: {
            if (firstLoad) {
                firstLoad = false;
                return ;
            } else {
                applyDegradeToMatiere();
            }
        }
        spacing: 10

        Row {
            id: groupetitre

            TextField {
                id: groupename

                function updateText() {
                    nom = text;
                    ddb.updateGroupeMatiereNom(groupeid, nom);
                }

                Component.onCompleted: {
                    groupename.text = nom;
                    groupename.onTextChanged.connect(groupename.updateText);
                }
                font.bold: true
                font.pointSize: 14
                width: 400
                height: 50

                Rectangle {
                    id: colorbutton

                    radius: 10
                    width: 50
                    height: parent.height / 2
                    anchors.right: dodegradebutton.left
                    anchors.rightMargin: 5
                    anchors.verticalCenter: parent.verticalCenter
                    border.color: "black"
                    border.width: 1
                    ToolTip.visible: mousecolorbutton.containsMouse
                    ToolTip.text: "Cliquer pour choisir la couleur du dégradé"

                    MouseArea {
                        id: mousecolorbutton

                        anchors.fill: parent
                        hoverEnabled: true
                        onPressed: {
                            colordialog.currentColor = groupe.baseColor;
                            colordialog.ouvre(gradientstart);
                        }
                    }

                    gradient: Gradient {
                        GradientStop {
                            id: gradientstart

                            property color startcolor

                            position: 0
                            color: groupe.baseColor
                            onStartcolorChanged: {
                                groupe.baseColor = startcolor;
                            }
                        }

                        GradientStop {
                            position: 1
                            color: "white"
                        }

                    }

                }

                Button {
                    id: dodegradebutton

                    font.pointSize: 10
                    display: AbstractButton.TextOnly
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Go!"
                    ToolTip.visible: hovered
                    ToolTip.text: "Créer un dégradé"

                    background: Rectangle {
                        radius: 10
                        anchors.fill: parent
                        color: "transparent"
                    }

                }

                background: Rectangle {
                    radius: 10
                    border.color: "black"
                    border.width: 3

                    gradient: Gradient {
                        property alias start: gradientnamestart

                        GradientStop {
                            id: gradientnamestart

                            position: 0
                            color: groupe.baseColor
                        }

                        GradientStop {
                            position: 1
                            color: "white"
                        }

                    }

                }

            }

            ActionButtonMatiere {
                //                    ddb.moveMatiereTo(matiereid, index - 1);
                //                    root.parent.applyDegradeToMatiere(undefined, true)

                id: upmatierebutton

                referent: groupename
                enabled: index > 0
                ToolTip.visible: false
                icon.source: "qrc:/icons/arrow-up"
                onClicked: {
                    root.model = ddb.moveGroupeMatiereTo(groupeid, index - 1);
                }
            }

            ActionButtonMatiere {
                id: downlmatierebutton

                referent: groupename
                enabled: index < (root.count - 1)
                ToolTip.visible: false
                icon.source: "qrc:/icons/arrow-down"
                onClicked: {
                    root.model = ddb.moveGroupeMatiereTo(groupeid, index + 1);
                }
            }

            ActionButtonMatiere {
                id: addgroupebutton

                referent: groupename
                icon.source: "qrc:/icons/add-row"
                ToolTip.text: "Insérer un nouveau groupe"
            }

            ActionButtonMatiere {
                id: delgroupebutton

                referent: groupename
                icon.source: "qrc:/icons/remove-row-red"
                ToolTip.text: "supprimer le groupe: " + nom
            }

        }

        ChangeMatiere {
            id: changematiere

            Component.onCompleted: {
                model = ddb.getMatieres(groupeid);
                bdd = ddb;
            }
        }

    }

}