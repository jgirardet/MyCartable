import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3 as Dialogs13

Item {
    id: root




    component BasePageAction: Action {
      property int position
      property  string nom
      property string tooltip
      property var dialog
      property bool append: true

      function newSection () {
        let newPos = append ? ddb.pageModel.count : position + 1
        ddb.addSection(ddb.currentPage, {
                  "classtype": nom,
                  "position": newPos
              });
        }
    }

    component ActionToolTip : ToolTip {
    id: ttip
    property string shortcut

    contentItem: ColumnLayout {
    spacing: 0
    Text {
        text: ttip.text
        Layout.fillWidth: true
        color: "black"
        font.pointSize: 8
        horizontalAlignment: Text.AlignHCenter
    }
    Text {
        text: shortcut.split("+").join(" + ")
        Layout.fillWidth: true
        font.pointSize: 8
        horizontalAlignment: Text.AlignHCenter
        color: "black"
        visible: text != ""
    }

    }

    background: Rectangle {
        color: "white"
        border.color: "black"
    }
    }

    component NewTextSection : BasePageAction {
        nom: "TextSection"
        icon.source: "qrc:///icons/newTextSection"
        onTriggered: newSection()
        tooltip: "Ajouter du texte"
        shortcut: "Ctrl+t"

    }
    component NewEquationSection : BasePageAction {
        icon.source: "qrc:///icons/newEquationSection"
        nom: "EquationSection"
        onTriggered: newSection()
        tooltip: "Ajouter une équation"
        shortcut: "Ctrl+e"
    }

    component NewImageSection : BasePageAction {
        icon.source: "qrc:///icons/newImageSection"
        nom: "ImageSection"
        onTriggered: dialog.open()
        tooltip: "Ajouter une image/un document"
        shortcut: ""
        dialog: Dialogs13.FileDialog {
          title: "Choisir le fichier à importer"
          folder: shortcuts.pictures
          nameFilters: ["fichiers Images (*.jpg *.png *.bmp *.ppm *.gif, *.pdf)"]
          onAccepted: {
              uiManager.buzyIndicator = true
              var newPos = append ? ddb.pageModel.count : position + 1
              ddb.addSection(ddb.currentPage, {
                  "path": fileUrl,
                  "classtype": nom,
                  "position": newPos
              });
          }
        }
    }
    component NewImageSectionVide : BasePageAction {
        icon.source: "qrc:///icons/newImageSectionVide"
        nom: "ImageSectionVide"
        onTriggered: dialog.open()
        tooltip: "Créer un dessin vide"
        shortcut: ""
        dialog: Dialog {
          id: videdialog
          padding: 0
          y: parent.y + parent.height
          implicitWidth: 100
          title: ""
          focus: true
          background: Rectangle {
            anchors.fill: parent
            color : "lightgrey"
          }
          contentItem: RowLayout {
          property var sizes: {
          "petit":{"iconHeight":20, "value":400},
          "moyen":{"iconHeight":40, "value":800},
          "grand":{"iconHeight":60, "value":1200},
          }
            function choose(val) {
              var newPos = append ? ddb.pageModel.count : position + 1
              ddb.addSection(ddb.currentPage, {
                  "height": val,
                  "width": 1280,
                  "classtype": nom,
                  "position": newPos
              });
              videdialog.close()

            }
            ImageVideButton {
                size: parent.sizes.petit
            }
            ImageVideButton {
                size: parent.sizes.moyen
            }
            ImageVideButton {
                size: parent.sizes.grand
            }
          }
//          onAccepted: {
//          onAccepted: {
////              uiManager.buzyIndicator = true
//
//          }
        }
    }

    component NewOperationSection : BasePageAction {
        icon.source: "qrc:///icons/newOperationSection"
        nom: "OperationSection"
        onTriggered: dialog.open()
        tooltip: "Ajouter une opération"
        shortcut: ""
        dialog : Dialog {
          id: dialogoperation

          implicitWidth: 300
          title: "Entrer 2 nombres séparés\npar +,-,* ou /"
          standardButtons: Dialog.Ok | Dialog.Cancel
          focus: true
          onAccepted: {
              ddb.addSection(ddb.currentPage, {
                  "string": contentItem.text,
                  "classtype": nom,
                  "position":append ? ddb.pageModel.count : position + 1
              });
              contentItem.clear();
          }

          contentItem: TextField {
              focus: true
              onAccepted: dialogoperation.accept()

              background: Rectangle {
                  anchors.fill: parent
                  color: "white"
              }

          }

      }

    }


    component ModelChooser : Column {
          property alias source: imgchooser.source
          property alias text: rb.icon.name
          property alias checked: rb.checked
          property var groupe: rb.ButtonGroup.group
          RadioButton {
              id: rb
              ButtonGroup.group: groupe
              display: AbstractButton.IconOnly
          }

          Image {
              id: imgchooser
              width: rb.width
              fillMode: Image.PreserveAspectFit
          }
    }

    component NewTableauSection : BasePageAction {
        id : tableauaction
        icon.source: "qrc:///icons/newTableauSection"
        nom: "TableauSection"
        onTriggered: dialog.open()
        tooltip: "Ajouter une tableau"
        shortcut: ""

        property var groupe: ButtonGroup {
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
                        groupe: groupeModeles
                    }
                    ModelChooser {
                        source: "qrc:///icons/modele-ligne0"
                        text:"ligne0"
                        groupe: groupeModeles
                    }
                    ModelChooser {
                        source: "qrc:///icons/modele-colonne0"
                        text:"colonne0"
                        groupe: groupeModeles
                    }
                    ModelChooser {
                        source: "qrc:///icons/modele-ligne0-colonne0"
                        text:"ligne0-colonne0"
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

    component RemovePage : BasePageAction {
        icon.source: "qrc:///icons/removePage"
        onTriggered: ddb.removePage(ddb.currentPage)
        tooltip: "Supprimer la page ?"
        shortcut: ""
    }


    component ExportOdt : BasePageAction {
        icon.source: "qrc:///icons/odt"
        onTriggered: ddb.exportToOdt()
        tooltip: "Exporter la page en odt"
        shortcut: ""
    }

    component ExportPdf : BasePageAction {
        icon.source: "qrc:///icons/pdf"
        onTriggered: ddb.exportToPDF()
        tooltip: "Exporter la page en pdf"
        shortcut: ""
    }



}
