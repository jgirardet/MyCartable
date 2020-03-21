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
    anchors.fill: parent
    color: model.isRetenueLine(index) ? "red" : model.isLine1(index) ? "green" : model.isMembreLine(index) ? "blue" : "black"
    horizontalAlignment: TextInput.AlignHCenter
//    verticalAlignment: model.isResultLine(index) ? TextInput.AlignVCenter : model.isRetenueLine(index) ? TextInput.AlignBottom : TextInput.AlignTop
    verticalAlignment: model.isResultLine(index) ? TextInput.AlignBottom : model.isResultLine(index+model.columns) ? TextInput.AlignTop : TextInput.AlignVCenter
//      bottomPadding: model.isResultLine(index) ? 0 : 5

    background: BorderRectangle {
      color: input.parent.color
      borderColor: model.isResultLine(index) || model.isLine1(index-model.columns) ? "black" : input.parent.color
      borderTop: -2
//      borderBottom: -2
    }

  }

}