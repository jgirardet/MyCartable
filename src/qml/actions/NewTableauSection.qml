import QtQuick 2.15
import QtQuick.Controls 2.15
//import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3 as Dialogs13

BasePageAction {
    id: tableauaction

    property var groupe

    icon.source: "qrc:///icons/newTableauSection"
    nom: "TableauSection"
    onTriggered: dialog.open()
    tooltip: "Ajouter une tableau"
    shortcut: ""

    groupe: ButtonGroup {
        id: groupeModeles
    }

    dialog: Dialog {
        id: dialogNewTableau

        title: "Ajouter un tableau"
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: {
            ddb.addSection(ddb.currentPage, {
                "lignes": ~~lignesSlider.value,
                "colonnes": ~~colonneSlider.value,
                "classtype": tableauaction.nom,
                "position": tableauaction.append ? ddb.pageModel.count : tableauaction.position + 1,
                "modele": groupeModeles.checkedButton.icon.name
            });
        }

        contentItem: Column {
            Text {
                id: modeldebase

                text: "Modèle"
            }

            Row {
                id: lesteDesModels

                spacing: 2

                ModelChooser {
                    source: "qrc:///icons/modele-vide"
                    text: ""
                    checked: true
                    groupe: groupeModeles
                }

                ModelChooser {
                    source: "qrc:///icons/modele-ligne0"
                    text: "ligne0"
                    groupe: groupeModeles
                }

                ModelChooser {
                    source: "qrc:///icons/modele-colonne0"
                    text: "colonne0"
                    groupe: groupeModeles
                }

                ModelChooser {
                    source: "qrc:///icons/modele-ligne0-colonne0"
                    text: "ligne0-colonne0"
                    groupe: groupeModeles
                }

            }

            Text {
                id: textColumn

                text: "nombre de colonnes : " + colonneSlider.value
            }

            Slider {
                id: colonneSlider

                wheelEnabled: true
                stepSize: 1
                to: 20
                from: 1
                value: 1
            }

            Text {
                id: textLignes

                text: "nombre de lignes: " + lignesSlider.value
            }

            Slider {
                id: lignesSlider

                wheelEnabled: true
                stepSize: 1
                to: 20
                from: 1
                value: 1
            }

        }

    }

}
