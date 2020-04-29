import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base
  color: ddb.colorFond
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
      color: "transparent"

      Layout.fillWidth: true
      MatiereComboBox {
        anchors.fill: parent
        textRole: "nom"
        valueRole: "id"
        id: combo
        objectName: "combo"
        model: ddb.matieresList
        currentIndex: ddb.getMatiereIndexFromId(ddb.currentMatiere)
        onActivated: ddb.setCurrentMatiereFromIndexSignal(index)
        Component.onCompleted: activated.connect(ddb.setCurrentMatiereFromIndexSignal)

        contentItem: Text {
          text: combo.displayText
          color: combo.currentValue ? combo.model[combo.currentIndex].fgColor : "white"
          verticalAlignment: Text.AlignVCenter
          horizontalAlignment: Text.AlignHCenter
        }

        background: Rectangle {
          color: combo.currentValue ? combo.model[combo.currentIndex].bgColor : "white"
          radius: 10
        }

        delegate: Button {
          highlighted: combo.highlightedIndex === index
          width: combo.width
          contentItem: Text {
            id: delegateContent
            text: modelData.nom
            color: modelData.fgColor
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
          }
          background: Rectangle {
            color: modelData.bgColor
          }
        }

      }
    }

    ListView {
      id: lvActivite
      objectName: "repeater"
      model: ddb.pagesParSection
      Layout.fillHeight: true
      Layout.fillWidth: true
      spacing: 15
      clip: true
      delegate: ActiviteRectangle {
        model: modelData
        width: lvActivite.width
      }

    }
  }
}