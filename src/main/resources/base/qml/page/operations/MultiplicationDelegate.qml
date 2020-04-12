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
    verticalAlignment: TextInput.AlignVCenter



    background: BorderRectangle {
      color: input.focus ? "yellow" :root.color
      borderColor: model.isResultLine(index) || model.isLine1(index - model.columns) ? "black" : input.parent.color
      borderTop: -2
    }

    font.underline: model.highLight.includes(index)
    font.weight: model.highLight.includes(index) ? Font.Black : Font.Normal

    validator: RegularExpressionValidator {
      regularExpression: /^\d{1},?$/
    }

    function moreKeys(event) {

      if (event.key == Qt.Key_Comma) {
        edit = display + event.text
        event.accepted = true
      }

    }

  }

}