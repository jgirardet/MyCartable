import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base
  color: ddb.colorFond
  /* beautify preserve:start */
  property var repeater: _repeater
  /* beautify preserve:end */
  ColumnLayout {
    id: activitesColumn
    anchors.fill: parent
    spacing: 5
    Rectangle {
      id: matiereSelect
      objectName: "matiereSelect"
      Layout.preferredHeight: ddb.getLayoutSizes("preferredHeaderHeight")
      Layout.minimumHeight: Layout.preferredHeight
      Layout.maximumHeight: Layout.preferredHeight
      Layout.fillWidth: true
      MatiereComboBox {
        id: _comboBoxSelectMatiere
        objectName: "_comboBoxSelectMatiere"
        model: ddb.matieresListNom
        currentIndex: ddb.getMatiereIndexFromId(ddb.currentMatiere)
        onActivated: ddb.setCurrentMatiereFromIndexSignal(index)
        Component.onCompleted: activated.connect(ddb.setCurrentMatiereFromIndexSignal)
      }
    }

    Repeater {
      id: _repeater
      objectName: "repeater"
      model: ddb.pagesParSection
      ActiviteRectangle {
        model: modelData

      }

    }
  }
}