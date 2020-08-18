import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

NewSectionButton {
    //            RowLayout {
    //                RadioButton {
    //                    text: qsTr("Second")
    //                }
    //                RadioButton {
    //                    text: qsTr("Third")
    //                }
    //            }

    id: root

    sectionName: "TableauSection"
    ToolTip.text: "Ajouter un Tableau"
    ButtonGroup {
        id: groupeModeles
    }
    component ModelChooser : Column {
        property alias source: imgchooser.source
        property alias text: rb.icon.name
        property alias checked: rb.checked
        RadioButton {
            id: rb
            ButtonGroup.group: groupeModeles
            display: AbstractButton.IconOnly
        }

        Image {
            id: imgchooser

            width: rb.width
            fillMode: Image.PreserveAspectFit
        }

    }

    dialog: Dialog {
        id: dialogNewTableau

        title: "Ajouter un tableau"
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: {
        ddb.addSection(ddb.currentPage, {
            "lignes": ~~lignesSlider.value,
            "colonnes": ~~colonneSlider.value,
            "classtype": "TableauSection",
            "position": typeof root.targetIndex == "number" ? root.targetIndex : null,
            "modele": groupeModeles.checkedButton.icon.name
        })

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
                    text:""
                    checked: true
                }
                ModelChooser {
                    source: "qrc:///icons/modele-ligne0"
                    text:"ligne0"
                }
                ModelChooser {
                    source: "qrc:///icons/modele-colonne0"
                    text:"colonne0"
                }
                ModelChooser {
                    source: "qrc:///icons/modele-ligne0-colonne0"
                    text:"ligne0-colonne0"
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
