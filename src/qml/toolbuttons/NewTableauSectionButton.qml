import QtQuick 2.14
import QtQuick.Controls 2.14

NewSectionButton {
  id: root
  sectionName: "TableauSection"
  ToolTip.text: "Ajouter un Tableau"
  dialog: Dialog {
    id: dialogNewTableau
    title: "Ajouter un tableau"
    contentItem: Column {
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

    standardButtons: Dialog.Ok | Dialog.Cancel
    onAccepted: ddb.addSection(ddb.currentPage, {
      'lignes': ~~lignesSlider.value,
      'colonnes': ~~colonneSlider.value,
      "classtype": "TableauSection",
      "position": typeof root.targetIndex == "number" ? root.targetIndex : null

    })
  }
}