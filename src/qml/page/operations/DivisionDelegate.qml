import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"

Rectangle {
  id: root
  property alias model: input.model
  property alias textinput: input
  property TextInput quotient
  property GridView grid: GridView.view
  height: grid.cellHeight
  width: grid.cellWidth

  color: "white"
  TextInputDelegate {
    id: input

    anchors.fill: parent
    color: model.isRetenue(index) ? "red" : "black"
    horizontalAlignment: model.isRetenueGauche(index) ? TextInput.AlignRight : model.isRetenueDroite(index) ? TextInput.AlignLeft : TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter

    background: BorderRectangle {
      color: input.focus ? "yellow" : root.color
      borderColor: model.isMembreLine(index + model.columns) ? "black" : input.parent.color
      borderTop: -2
    }
    padding: 0

    function moreKeys(event) {
      if (event.key == Qt.Key_Return) {
        root.quotient.forceActiveFocus()
        event.accepted = true

      } else if (event.key == Qt.Key_Plus) {
        model.goToAbaisseLine()
        event.accepted = true
      } else if (event.key == Qt.Key_Minus) {
        model.goToResultLine()
        event.accepted = true

      } else if (event.key == Qt.Key_Asterisk) {
        model.addRetenues()
        event.accepted = true

      }

    }

  }

}