import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"

Rectangle {
  id: root
  property alias model: input.model
  property alias textinput: input

  property GridView grid: GridView.view
  height: grid.cellHeight
  width: grid.cellWidth

  color: "white"
  TextInputDelegate {
    id: input
    height: parent / 2

    leftPadding: model.isRetenueDroit(index) ? 0 : 5
    rightPadding: model.isRetenueGauche(index) ? 1 : 5
    color: model.isRetenueGauche(index) || model.isRetenueDroit(index) ? "red" : "black"
    horizontalAlignment: model.isRetenueDroit(index) ? TextInput.AlignLeft : model.isRetenueGauche(index) ? TextInput.AlignRight : TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter

  }

}